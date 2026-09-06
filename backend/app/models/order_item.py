"""OrderItem ORM model — junction table between Orders and Products."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    def __repr__(self):
        return f"<OrderItem {self.order_id}/{self.product_id} x{self.quantity}>"
