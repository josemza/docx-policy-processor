from sqlalchemy.orm import Session

from app.domain.documents.entities import DocumentOperation
from app.infrastructure.db.models.documents import DocumentOperationModel



def _to_domain(model: DocumentOperationModel) -> DocumentOperation:
    return DocumentOperation(
        id=model.id,
        user_id=model.user_id,
        product_id=model.product_id,
        format_rule_id=model.format_rule_id,
        policy_number=model.policy_number,
        original_filename=model.original_filename,
        sanitized_filename=model.sanitized_filename,
        stored_original_name=model.stored_original_name,
        stored_output_name=model.stored_output_name,
        original_path=model.original_path,
        output_path=model.output_path,
        file_size_bytes=model.file_size_bytes,
        mime_type=model.mime_type,
        status=model.status,
        error_message=model.error_message,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyDocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_operation(
        self,
        *,
        user_id: str,
        product_id: str,
        format_rule_id: str,
        policy_number: str,
        original_filename: str,
        sanitized_filename: str,
        stored_original_name: str,
        stored_output_name: str,
        original_path: str,
        output_path: str,
        file_size_bytes: int,
        mime_type: str | None,
        status: str = "RECEIVED",
    ) -> DocumentOperation:
        model = DocumentOperationModel(
            user_id=user_id,
            product_id=product_id,
            format_rule_id=format_rule_id,
            policy_number=policy_number,
            original_filename=original_filename,
            sanitized_filename=sanitized_filename,
            stored_original_name=stored_original_name,
            stored_output_name=stored_output_name,
            original_path=original_path,
            output_path=output_path,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            status=status,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_domain(model)
