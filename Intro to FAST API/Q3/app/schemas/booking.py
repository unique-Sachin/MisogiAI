from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    customer_name: str
    customer_email: str
    quantity: int
    event_id: int
    ticket_type_id: int

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    quantity: Optional[int] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class Booking(BookingBase):
    id: int
    confirmation_code: str
    total_amount: float
    status: BookingStatus
    booking_date: datetime
    
    class Config:
        from_attributes = True

class BookingStats(BaseModel):
    total_bookings: int
    total_events: int
    total_venues: int
    total_revenue: float
    available_tickets: int

# Simple models without forward references for now
class SimpleEvent(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    event_date: datetime
    venue_id: int
    max_tickets: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SimpleVenue(BaseModel):
    id: int
    name: str
    address: str
    capacity: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class SimpleTicketType(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class BookingWithDetails(Booking):
    event: Optional[SimpleEvent] = None
    ticket_type: Optional[SimpleTicketType] = None
    venue: Optional[SimpleVenue] = None

    class Config:
        from_attributes = True 