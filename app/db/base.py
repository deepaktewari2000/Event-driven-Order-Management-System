from .base_class import Base

# Import all models here so Alembic can detect them
from app.models.user import User  # noqa
from app.models.order import Order  # noqa
from app.models.product import Product  # noqa

