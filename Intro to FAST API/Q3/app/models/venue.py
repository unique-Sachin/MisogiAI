from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    address = Column(Text, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(Text)
    
    # Relationships
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan") 