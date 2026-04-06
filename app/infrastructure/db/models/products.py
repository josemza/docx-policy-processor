from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    title_template: Mapped[str] = mapped_column(Text())
    header_template: Mapped[str] = mapped_column(Text())
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    format_rules: Mapped[list["FormatRuleModel"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    document_operations: Mapped[list["DocumentOperationModel"]] = relationship(back_populates="product")


class FormatRuleModel(Base):
    __tablename__ = "format_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    configuration_json: Mapped[str] = mapped_column(Text())
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    product: Mapped[ProductModel] = relationship(back_populates="format_rules")
    document_operations: Mapped[list["DocumentOperationModel"]] = relationship(back_populates="format_rule")
