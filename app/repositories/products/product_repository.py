import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.products.entities import FormatRule, Product
from app.infrastructure.db.models.products import FormatRuleModel, ProductModel



def _to_format_rule(model: FormatRuleModel) -> FormatRule:
    return FormatRule(
        id=model.id,
        product_id=model.product_id,
        version=model.version,
        configuration=json.loads(model.configuration_json),
        active=model.active,
        effective_from=model.effective_from,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )



def _to_product(model: ProductModel, active_rule: FormatRuleModel | None = None) -> Product:
    return Product(
        id=model.id,
        code=model.code,
        name=model.name,
        title_template=model.title_template,
        header_template=model.header_template,
        active=model.active,
        created_at=model.created_at,
        updated_at=model.updated_at,
        active_format_rule=_to_format_rule(active_rule) if active_rule else None,
    )


class SqlAlchemyProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active_products(self) -> list[Product]:
        stmt = (
            select(ProductModel)
            .where(ProductModel.active.is_(True))
            .options(selectinload(ProductModel.format_rules))
            .order_by(ProductModel.name.asc())
        )
        products = []
        for model in self.db.scalars(stmt):
            active_rule = self._resolve_active_rule(model.format_rules)
            products.append(_to_product(model, active_rule))
        return products

    def get_active_product(self, product_id: str) -> Product | None:
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id, ProductModel.active.is_(True))
            .options(selectinload(ProductModel.format_rules))
        )
        model = self.db.scalar(stmt)
        if model is None:
            return None
        return _to_product(model, self._resolve_active_rule(model.format_rules))

    def get_product_with_rule(self, product_id: str, format_rule_id: str) -> Product | None:
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.format_rules))
        )
        model = self.db.scalar(stmt)
        if model is None:
            return None
        matched_rule = None
        for rule in model.format_rules:
            if rule.id == format_rule_id:
                matched_rule = rule
                break
        return _to_product(model, matched_rule) if matched_rule else None

    def create_product_with_rule(
        self,
        *,
        code: str,
        name: str,
        title_template: str,
        header_template: str,
        configuration_json: str,
        version: int = 1,
    ) -> Product:
        product = ProductModel(
            code=code,
            name=name,
            title_template=title_template,
            header_template=header_template,
            active=True,
        )
        self.db.add(product)
        self.db.flush()
        rule = FormatRuleModel(
            product_id=product.id,
            version=version,
            configuration_json=configuration_json,
            active=True,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(product)
        self.db.refresh(rule)
        return _to_product(product, rule)

    def count_products(self) -> int:
        return len(self.db.scalars(select(ProductModel)).all())

    @staticmethod
    def _resolve_active_rule(rules: list[FormatRuleModel]) -> FormatRuleModel | None:
        active_rules = [rule for rule in rules if rule.active]
        if not active_rules:
            return None
        return sorted(active_rules, key=lambda item: (item.version, item.effective_from), reverse=True)[0]
