from pydantic import BaseModel, ConfigDict


class DocumentOperationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    format_rule_id: str
    policy_number: str
    original_filename: str
    sanitized_filename: str
    file_size_bytes: int
    status: str
    original_path: str
    output_path: str
