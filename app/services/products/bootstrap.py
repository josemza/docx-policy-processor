from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.infrastructure.db.session import get_session_local
from app.repositories.products.product_repository import SqlAlchemyProductRepository
from app.services.products.product_service import ProductService



def bootstrap_product_catalog() -> None:
    settings = get_settings()
    if not settings.bootstrap_product_catalog:
        return

    session_local, _ = get_session_local()
    db: Session = session_local()
    try:
        service = ProductService(product_repository=SqlAlchemyProductRepository(db))
        service.bootstrap_catalog()
    finally:
        db.close()
