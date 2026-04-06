from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.dependencies import get_current_session_context, get_document_service
from app.core.responses import success_response
from app.domain.documents.schemas import DocumentOperationResponse
from app.services.documents.document_service import DocumentService

router = APIRouter()


@router.post("/upload")
async def upload_document(
    product_id: str = Form(...),
    policy_number: str = Form(...),
    file: UploadFile = File(...),
    session_context=Depends(get_current_session_context),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    content = await file.read()
    operation = document_service.create_upload_operation(
        user_id=session_context.user.id,
        product_id=product_id,
        policy_number=policy_number,
        filename=file.filename or "",
        content=content,
        mime_type=file.content_type,
    )
    return success_response(
        message="Documento recibido y registrado correctamente.",
        data=DocumentOperationResponse.model_validate(operation).model_dump(),
    )
