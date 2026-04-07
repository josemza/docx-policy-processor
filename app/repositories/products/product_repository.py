import json
from datetime import datetime, timezone

from sqlalchemy import func, select
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

    def get_product(self, product_id: str) -> Product | None:
        stmt = select(ProductModel).where(ProductModel.id == product_id).options(
            selectinload(ProductModel.format_rules)
        )
        model = self.db.scalar(stmt)
        if model is None:
            return None
        return _to_product(model, self._resolve_active_rule(model.format_rules))

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
        matched_rule = next((rule for rule in model.format_rules if rule.id == format_rule_id), None)
        return _to_product(model, matched_rule) if matched_rule else None

    def list_format_rules(self, product_id: str) -> list[FormatRule]:
        stmt = (
            select(FormatRuleModel)
            .where(FormatRuleModel.product_id == product_id)
            .order_by(FormatRuleModel.version.desc())
        )
        return [_to_format_rule(model) for model in self.db.scalars(stmt)]

    def get_format_rule(self, rule_id: str) -> FormatRule | None:
        model = self.db.get(FormatRuleModel, rule_id)
        return _to_format_rule(model) if model else None

    def create_format_rule(
        self,
        *,
        product_id: str,
        configuration_json: str,
        active: bool = True,
    ) -> FormatRule:
        version = self._next_version(product_id)
        if active:
            self._deactivate_rules(product_id)
        model = FormatRuleModel(
            product_id=product_id,
            version=version,
            configuration_json=configuration_json,
            active=active,
            effective_from=datetime.now(timezone.utc),
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_format_rule(model)

    def update_format_rule_versioned(
        self,
        *,
        rule_id: str,
        configuration_json: str,
        active: bool = True,
    ) -> FormatRule | None:
        current = self.db.get(FormatRuleModel, rule_id)
        if current is None:
            return None
        current.active = False
        self.db.add(current)
        self.db.flush()
        new_rule = FormatRuleModel(
            product_id=current.product_id,
            version=self._next_version(current.product_id),
            configuration_json=configuration_json,
            active=active,
            effective_from=datetime.now(timezone.utc),
        )
        if active:
            self._deactivate_rules(current.product_id)
        self.db.add(new_rule)
        self.db.commit()
        self.db.refresh(new_rule)
        return _to_format_rule(new_rule)

    def deactivate_format_rule(self, rule_id: str) -> FormatRule | None:
        model = self.db.get(FormatRuleModel, rule_id)
        if model is None:
            return None
        model.active = False
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_format_rule(model)

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

    def _next_version(self, product_id: str) -> int:
        stmt = select(func.max(FormatRuleModel.version)).where(FormatRuleModel.product_id == product_id)
        current = self.db.scalar(stmt)
        return int(current or 0) + 1

    def _deactivate_rules(self, product_id: str) -> None:
        stmt = select(FormatRuleModel).where(
            FormatRuleModel.product_id == product_id,
            FormatRuleModel.active.is_(True),
        )
        for model in self.db.scalars(stmt):
            model.active = False
            self.db.add(model)

    @staticmethod
    def _resolve_active_rule(rules: list[FormatRuleModel]) -> FormatRuleModel | None:
        active_rules = [rule for rule in rules if rule.active]
        if not active_rules:
            return None
        return sorted(active_rules, key=lambda item: (item.version, item.effective_from), reverse=True)[0]
