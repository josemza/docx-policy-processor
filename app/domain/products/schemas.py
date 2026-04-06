from typing import Any

from pydantic import BaseModel, ConfigDict


class FormatRuleResponse(BaseModel):
    id: str
    version: int
    configuration: dict[str, Any]


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    title_template: str
    header_template: str
    active_format_rule: FormatRuleResponse | None
