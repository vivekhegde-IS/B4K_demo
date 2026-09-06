"""Order ORM model."""

from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.database.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    purchase_date = Column(Date, nullable=False)

    items = relationship("OrderItem", back_populates="order", lazy="joined")

    def __repr__(self):
        return f"<Order {self.order_id}>"
