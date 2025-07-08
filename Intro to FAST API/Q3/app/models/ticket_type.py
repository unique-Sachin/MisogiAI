from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base

class TicketType(Base):
    __tablename__ = "ticket_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)  # VIP, Standard, Economy
    price = Column(Float, nullable=False)
    description = Column(Text)
    
    # Relationships
    bookings = relationship("Booking", back_populates="ticket_type") 