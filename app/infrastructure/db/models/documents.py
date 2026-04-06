from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class DocumentOperationModel(Base):
    __tablename__ = "document_operations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), index=True)
    format_rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("format_rules.id"), index=True)
    policy_number: Mapped[str] = mapped_column(String(100), index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    sanitized_filename: Mapped[str] = mapped_column(String(255))
    stored_original_name: Mapped[str] = mapped_column(String(255), unique=True)
    stored_output_name: Mapped[str] = mapped_column(String(255), unique=True)
    original_path: Mapped[str] = mapped_column(String(500))
    output_path: Mapped[str] = mapped_column(String(500))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="RECEIVED")
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["UserModel"] = relationship(back_populates="document_operations")
    product: Mapped["ProductModel"] = relationship(back_populates="document_operations")
    format_rule: Mapped["FormatRuleModel"] = relationship(back_populates="document_operations")
