from app.core.config import get_settings
from app.core.exceptions import DocumentProcessingError, ResourceNotFoundError, ValidationAppError
from app.infrastructure.storage.files import DocumentStorage
from app.infrastructure.word.docx_formatter import DocxFormatter
from app.repositories.documents.document_repository import SqlAlchemyDocumentRepository
from app.repositories.products.product_repository import SqlAlchemyProductRepository


class DocumentService:
    def __init__(
        self,
        *,
        product_repository: SqlAlchemyProductRepository,
        document_repository: SqlAlchemyDocumentRepository,
    ) -> None:
        self.product_repository = product_repository
        self.document_repository = document_repository
        self.storage = DocumentStorage()
        self.settings = get_settings()
        self.formatter = DocxFormatter()

    def create_upload_operation(
        self,
        *,
        user_id: str,
        product_id: str,
        policy_number: str,
        filename: str,
        content: bytes,
        mime_type: str | None,
    ):
        product = self.product_repository.get_active_product(product_id)
        if product is None:
            raise ResourceNotFoundError("El producto seleccionado no existe o no esta activo.")
        if product.active_format_rule is None:
            raise ValidationAppError(
                "El producto no tiene una regla de formato activa.",
                code="missing_active_format_rule",
            )

        normalized_policy = policy_number.strip()
        if not normalized_policy:
            raise ValidationAppError(
                "El numero de poliza es obligatorio.",
                code="missing_policy_number",
            )

        extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if extension != "docx":
            raise ValidationAppError(
                "Solo se permiten archivos .docx.",
                code="invalid_file_extension",
            )

        file_size = len(content)
        if file_size == 0:
            raise ValidationAppError(
                "El archivo recibido esta vacio.",
                code="empty_file",
            )
        if file_size > self.settings.documents_max_upload_bytes:
            raise ValidationAppError(
                "El archivo excede el tamaño máximo permitido.",
                code="file_too_large",
                details={"max_bytes": self.settings.documents_max_upload_bytes},
            )
        if not content.startswith(b"PK"):
            raise ValidationAppError(
                "El archivo no parece ser un .docx valido.",
                code="invalid_docx_signature",
            )

        reserved = self.storage.reserve_paths(filename)
        self.storage.store_original(reserved.original_path, content)

        return self.document_repository.create_operation(
            user_id=user_id,
            product_id=product.id,
            format_rule_id=product.active_format_rule.id,
            policy_number=normalized_policy,
            original_filename=filename,
            sanitized_filename=reserved.sanitized_filename,
            stored_original_name=reserved.stored_original_name,
            stored_output_name=reserved.stored_output_name,
            original_path=self.storage.serialize_path(reserved.original_path),
            output_path=self.storage.serialize_path(reserved.output_path),
            file_size_bytes=file_size,
            mime_type=mime_type,
            status="RECEIVED",
        )

    def process_operation(self, *, operation_id: str, user_id: str):
        operation = self.document_repository.get_by_id_for_user(operation_id, user_id)
        if operation is None:
            raise ResourceNotFoundError("La operación documental no existe para el usuario actual.")

        product = self.product_repository.get_product_with_rule(
            operation.product_id,
            operation.format_rule_id,
        )
        if product is None or product.active_format_rule is None:
            self.document_repository.update_status(
                operation_id=operation.id,
                status="ERROR",
                error_message="No se pudo resolver la configuración del producto para esta operación.",
            )
            raise DocumentProcessingError(
                "No se pudo resolver la configuración del producto para esta operación.",
                code="missing_operation_product_configuration",
            )

        source_path = self.storage.resolve_relative_path(operation.original_path)
        output_path = self.storage.resolve_relative_path(operation.output_path)
        if not source_path.exists():
            self.document_repository.update_status(
                operation_id=operation.id,
                status="ERROR",
                error_message="El archivo original no existe en el almacenamiento temporal.",
            )
            raise ResourceNotFoundError("El archivo original de la operación no existe.")

        self.document_repository.update_status(operation_id=operation.id, status="PROCESSING")
        try:
            self.formatter.format_document(
                source_path=source_path,
                destination_path=output_path,
                product=product,
                policy_number=operation.policy_number,
            )
        except DocumentProcessingError as exc:
            self.document_repository.update_status(
                operation_id=operation.id,
                status="ERROR",
                error_message=exc.message,
            )
            raise
        except Exception as exc:
            self.document_repository.update_status(
                operation_id=operation.id,
                status="ERROR",
                error_message="Ocurrió un error inesperado durante el formateo DOCX.",
            )
            raise DocumentProcessingError(
                "Ocurrió un error inesperado durante el formateo DOCX.",
                code="unexpected_docx_processing_error",
            ) from exc

        return self.document_repository.update_status(
            operation_id=operation.id,
            status="COMPLETED",
            error_message=None,
        )
