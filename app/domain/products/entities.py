from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class FormatRule:
    id: str
    product_id: str
    version: int
    configuration: dict[str, Any]
    active: bool
    effective_from: datetime
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class Product:
    id: str
    code: str
    name: str
    title_template: str
    header_template: str
    active: bool
    created_at: datetime
    updated_at: datetime
    active_format_rule: FormatRule | None = None
