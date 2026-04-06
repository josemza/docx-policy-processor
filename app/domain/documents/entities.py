from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class DocumentOperation:
    id: str
    user_id: str
    product_id: str
    format_rule_id: str
    policy_number: str
    original_filename: str
    sanitized_filename: str
    stored_original_name: str
    stored_output_name: str
    original_path: str
    output_path: str
    file_size_bytes: int
    mime_type: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
