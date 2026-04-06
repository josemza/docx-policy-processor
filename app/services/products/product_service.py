import json

from app.core.config import get_settings
from app.repositories.products.product_repository import SqlAlchemyProductRepository

BOOTSTRAP_PRODUCTS = [
    {
        "code": "VIDA_INDIVIDUAL",
        "name": "Vida Individual",
        "title_template": "Póliza de Vida Individual",
        "header_template": "Producto VIDA INDIVIDUAL - Póliza {{ numero_poliza }}",
        "configuration": {
            "page_setup": {"paper_size": "A4", "margin_top_cm": 2.5, "margin_bottom_cm": 2.5},
            "font_defaults": {"family": "Arial", "size_pt": 10},
            "paragraph_defaults": {"line_spacing": 1.15, "alignment": "justify"},
            "title_rules": {"case": "upper", "bold": True, "alignment": "center"},
        },
    },
    {
        "code": "SALUD_COLECTIVA",
        "name": "Salud Colectiva",
        "title_template": "Póliza de Salud Colectiva",
        "header_template": "Producto SALUD COLECTIVA - Póliza {{ numero_poliza }}",
        "configuration": {
            "page_setup": {"paper_size": "A4", "margin_top_cm": 2.0, "margin_bottom_cm": 2.0},
            "font_defaults": {"family": "Calibri", "size_pt": 10},
            "paragraph_defaults": {"line_spacing": 1.0, "alignment": "justify"},
            "title_rules": {"case": "title", "bold": True, "alignment": "left"},
        },
    },
]


class ProductService:
    def __init__(self, *, product_repository: SqlAlchemyProductRepository) -> None:
        self.product_repository = product_repository

    def list_active_products(self):
        return self.product_repository.list_active_products()

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
