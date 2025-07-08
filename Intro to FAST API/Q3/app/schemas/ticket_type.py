from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TicketTypeBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class TicketType(TicketTypeBase):
    id: int
    
    class Config:
        from_attributes = True

# Simple booking model without forward references
class SimpleBooking(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    quantity: int
    event_id: int
    ticket_type_id: int
    confirmation_code: str
    total_amount: float
    status: str
    booking_date: datetime
    
    class Config:
        from_attributes = True

class TicketTypeWithBookings(TicketType):
    bookings: List[SimpleBooking] = []
    
    class Config:
        from_attributes = True 