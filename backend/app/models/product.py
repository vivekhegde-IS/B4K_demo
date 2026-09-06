"""Product ORM model."""

from sqlalchemy import Column, String, Float, Text
from app.database.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Product {self.product_id}: {self.name}>"
