from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VenueBase(BaseModel):
    name: str
    address: str
    capacity: int
    description: Optional[str] = None

class VenueCreate(VenueBase):
    pass

class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class Venue(VenueBase):
    id: int
    
    class Config:
        from_attributes = True

# Simple event model without forward references
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

class VenueWithEvents(Venue):
    events: List[SimpleEvent] = []
    
    class Config:
        from_attributes = True 