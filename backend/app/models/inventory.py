"""Inventory ORM model."""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    store_location = Column(String, nullable=False)
    aisle = Column(String, nullable=False)
    shelf = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)

    product = relationship("Product", backref="inventory_records")

    def __repr__(self):
        return f"<Inventory {self.inventory_id}: {self.product_id} @ {self.store_location}>"
