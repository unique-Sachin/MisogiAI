from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_date: datetime
    venue_id: int
    max_tickets: int

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    venue_id: Optional[int] = None
    max_tickets: Optional[int] = None

class Event(EventBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Simple models without forward references
class SimpleVenue(BaseModel):
    id: int
    name: str
    address: str
    capacity: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

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

class EventWithDetails(Event):
    venue: Optional[SimpleVenue] = None
    bookings: List[SimpleBooking] = []
    
    class Config:
        from_attributes = True

class EventStats(BaseModel):
    total_bookings: int
    total_revenue: float
    available_tickets: int 