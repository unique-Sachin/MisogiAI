from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.venue import Venue
from app.models.event import Event
from app.models.ticket_type import TicketType
from app.models.booking import Booking
import string
import random

def get_venue_or_404(venue_id: int, db: Session = Depends(get_db)) -> Venue:
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

def get_event_or_404(event_id: int, db: Session = Depends(get_db)) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

def get_ticket_type_or_404(ticket_type_id: int, db: Session = Depends(get_db)) -> TicketType:
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    return ticket_type

def get_booking_or_404(booking_id: int, db: Session = Depends(get_db)) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

def generate_confirmation_code() -> str:
    """Generate a unique confirmation code for bookings"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def calculate_available_tickets(event: Event, db: Session) -> int:
    """Calculate available tickets for an event"""
    from sqlalchemy import func
    
    total_booked = db.query(func.sum(Booking.quantity)).filter(
        Booking.event_id == event.id,
        Booking.status != "cancelled"
    ).scalar() or 0
    
    available = event.max_tickets - total_booked
    return max(0, available)

def validate_booking_capacity(event: Event, quantity: int, db: Session) -> bool:
    """Validate if booking quantity is within available capacity"""
    available = calculate_available_tickets(event, db)
    return quantity <= available 