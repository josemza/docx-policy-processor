from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MarginsConfig(BaseModel):
    top_cm: float = Field(gt=0, le=10)
    bottom_cm: float = Field(gt=0, le=10)
    left_cm: float = Field(gt=0, le=10)
    right_cm: float = Field(gt=0, le=10)


class PageSetupConfig(BaseModel):
    paper_size: Literal["A4", "LETTER"] = "A4"
    margins: MarginsConfig


class TextStyleConfig(BaseModel):
    font_family: str = Field(min_length=1, max_length=100)
    font_size_pt: float = Field(gt=0, le=72)
    uppercase: bool = False


class GeneralTextConfig(TextStyleConfig):
    line_spacing: float = Field(gt=0.5, le=3)
    color_hex: str = Field(pattern=r"^#?[0-9A-Fa-f]{6}$")

    @field_validator("color_hex")
    @classmethod
    def normalize_color(cls, value: str) -> str:
        return value.replace("#", "").upper()


class TitleTextConfig(TextStyleConfig):
    alignment: Literal["left", "center", "right", "justify"] = "center"
    bold: bool = True


class FormatRuleConfig(BaseModel):
    page_setup: PageSetupConfig
    general_text: GeneralTextConfig
    title_text: TitleTextConfig

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if "general_text" in data and "title_text" in data:
            return data

        page_setup = data.get("page_setup", {}) or {}
        font_defaults = data.get("font_defaults", {}) or {}
        paragraph_defaults = data.get("paragraph_defaults", {}) or {}
        title_rules = data.get("title_rules", {}) or {}

        return {
            "page_setup": {
                "paper_size": str(page_setup.get("paper_size", "A4")).upper(),
                "margins": {
                    "top_cm": page_setup.get("margin_top_cm", 2.5),
                    "bottom_cm": page_setup.get("margin_bottom_cm", 2.5),
                    "left_cm": page_setup.get("margin_left_cm", 2.0),
                    "right_cm": page_setup.get("margin_right_cm", 2.0),
                },
            },
            "general_text": {
                "font_family": font_defaults.get("family", "Arial"),
                "font_size_pt": font_defaults.get("size_pt", 10),
                "line_spacing": paragraph_defaults.get("line_spacing", 1.15),
                "uppercase": False,
                "color_hex": "000000",
            },
            "title_text": {
                "font_family": font_defaults.get("family", "Arial"),
                "font_size_pt": max(float(font_defaults.get("size_pt", 10)) + 4, 12),
                "uppercase": str(title_rules.get("case", "")).lower() == "upper",
                "alignment": title_rules.get("alignment", "center"),
                "bold": bool(title_rules.get("bold", True)),
            },
        }


class FormatRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    version: int
    configuration: FormatRuleConfig
    active: bool
    effective_from: object


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    title_template: str
    header_template: str
    active_format_rule: FormatRuleResponse | None


class FormatRuleCreateRequest(BaseModel):
    product_id: str
    configuration: FormatRuleConfig
    active: bool = True


class FormatRuleUpdateRequest(BaseModel):
    configuration: FormatRuleConfig
    active: bool = True
