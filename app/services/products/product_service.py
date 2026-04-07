import json

from app.core.config import get_settings
from app.core.exceptions import ResourceNotFoundError, ValidationAppError
from app.domain.products.schemas import FormatRuleConfig
from app.repositories.products.product_repository import SqlAlchemyProductRepository

BOOTSTRAP_PRODUCTS = [
    {
        "code": "VIDA_INDIVIDUAL",
        "name": "Vida Individual",
        "title_template": "Póliza de Vida Individual",
        "header_template": "Producto VIDA INDIVIDUAL - Póliza {{ numero_poliza }}",
        "configuration": {
            "page_setup": {
                "paper_size": "A4",
                "margins": {"top_cm": 2.5, "bottom_cm": 2.5, "left_cm": 2.0, "right_cm": 2.0},
            },
            "general_text": {
                "font_family": "Arial",
                "font_size_pt": 10,
                "line_spacing": 1.15,
                "uppercase": False,
                "color_hex": "000000",
            },
            "title_text": {
                "font_family": "Arial",
                "font_size_pt": 14,
                "uppercase": True,
                "alignment": "center",
                "bold": True,
            },
        },
    },
    {
        "code": "SALUD_COLECTIVA",
        "name": "Salud Colectiva",
        "title_template": "Póliza de Salud Colectiva",
        "header_template": "Producto SALUD COLECTIVA - Póliza {{ numero_poliza }}",
        "configuration": {
            "page_setup": {
                "paper_size": "A4",
                "margins": {"top_cm": 2.0, "bottom_cm": 2.0, "left_cm": 2.0, "right_cm": 2.0},
            },
            "general_text": {
                "font_family": "Calibri",
                "font_size_pt": 10,
                "line_spacing": 1.0,
                "uppercase": False,
                "color_hex": "1D2430",
            },
            "title_text": {
                "font_family": "Calibri",
                "font_size_pt": 13,
                "uppercase": False,
                "alignment": "left",
                "bold": True,
            },
        },
    },
]


class ProductService:
    def __init__(self, *, product_repository: SqlAlchemyProductRepository) -> None:
        self.product_repository = product_repository

    def list_active_products(self):
        return self.product_repository.list_active_products()

    def list_format_rules(self, product_id: str):
        self._ensure_product_exists(product_id)
        return self.product_repository.list_format_rules(product_id)

    def get_format_rule(self, rule_id: str):
        rule = self.product_repository.get_format_rule(rule_id)
        if rule is None:
            raise ResourceNotFoundError("La regla de formato no existe.")
        return rule

    def create_format_rule(self, *, product_id: str, configuration: FormatRuleConfig, active: bool):
        self._ensure_product_exists(product_id)
        return self.product_repository.create_format_rule(
            product_id=product_id,
            configuration_json=configuration.model_dump_json(),
            active=active,
        )

    def update_format_rule(self, *, rule_id: str, configuration: FormatRuleConfig, active: bool):
        existing = self.product_repository.get_format_rule(rule_id)
        if existing is None:
            raise ResourceNotFoundError("La regla de formato no existe.")
        updated = self.product_repository.update_format_rule_versioned(
            rule_id=rule_id,
            configuration_json=configuration.model_dump_json(),
            active=active,
        )
        if updated is None:
            raise ResourceNotFoundError("La regla de formato no existe.")
        return updated

    def delete_format_rule(self, rule_id: str):
        existing = self.product_repository.get_format_rule(rule_id)
        if existing is None:
            raise ResourceNotFoundError("La regla de formato no existe.")
        if existing.active and len([r for r in self.product_repository.list_format_rules(existing.product_id) if r.active]) <= 1:
            raise ValidationAppError(
                "No se puede eliminar la única regla activa del producto.",
                code="last_active_format_rule",
            )
        deleted = self.product_repository.deactivate_format_rule(rule_id)
        if deleted is None:
            raise ResourceNotFoundError("La regla de formato no existe.")
        return deleted

    def bootstrap_catalog(self) -> None:
        settings = get_settings()
        if not settings.bootstrap_product_catalog:
            return
        if self.product_repository.count_products() > 0:
            return
        for item in BOOTSTRAP_PRODUCTS:
            self.product_repository.create_product_with_rule(
                code=item["code"],
                name=item["name"],
                title_template=item["title_template"],
                header_template=item["header_template"],
                configuration_json=json.dumps(item["configuration"]),
            )

    def _ensure_product_exists(self, product_id: str) -> None:
        product = self.product_repository.get_product(product_id)
        if product is None:
            raise ResourceNotFoundError("El producto no existe.")
