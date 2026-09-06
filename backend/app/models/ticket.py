"""SupportTicket ORM model."""

from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    ticket_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    type = Column(String, nullable=False)        # RETURN or EXCHANGE
    status = Column(String, nullable=False)       # CREATED, COMPLETED, REJECTED
    replacement_product_id = Column(String, nullable=True)  # For exchanges
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<SupportTicket {self.ticket_id}: {self.type}/{self.status}>"
