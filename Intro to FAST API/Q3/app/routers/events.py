from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.event import Event
from app.models.booking import Booking
from app.schemas.event import EventCreate, EventUpdate, Event as EventSchema, EventWithDetails, EventStats
from app.dependencies import get_event_or_404, calculate_available_tickets
from sqlalchemy import func

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventSchema)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    # Verify venue exists
    from app.dependencies import get_venue_or_404
    get_venue_or_404(event.venue_id, db)
    
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventSchema])
def get_all_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all events"""
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventSchema)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event"""
    return get_event_or_404(event_id, db)

@router.get("/{event_id}/bookings", response_model=EventWithDetails)
def get_event_bookings(event_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a specific event"""
    event = get_event_or_404(event_id, db)
    return event

@router.get("/{event_id}/available-tickets")
def get_available_tickets(event_id: int, db: Session = Depends(get_db)):
    """Get available tickets for an event"""
    event = get_event_or_404(event_id, db)
    available = calculate_available_tickets(event, db)
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "max_tickets": event.max_tickets,
        "available_tickets": available,
        "tickets_sold": event.max_tickets - available
    }

@router.get("/{event_id}/revenue")
def get_event_revenue(event_id: int, db: Session = Depends(get_db)):
    """Calculate total revenue for a specific event"""
    event = get_event_or_404(event_id, db)
    
    total_revenue = db.query(func.sum(Booking.total_amount)).filter(
        Booking.event_id == event_id,
        Booking.status != "cancelled"
    ).scalar() or 0
    
    total_bookings = db.query(func.count(Booking.id)).filter(
        Booking.event_id == event_id,
        Booking.status != "cancelled"
    ).scalar() or 0
    
    tickets_sold = db.query(func.sum(Booking.quantity)).filter(
        Booking.event_id == event_id,
        Booking.status != "cancelled"
    ).scalar() or 0
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_revenue": float(total_revenue),
        "total_bookings": int(total_bookings),
        "tickets_sold": int(tickets_sold),
        "available_tickets": calculate_available_tickets(event, db)
    }

@router.put("/{event_id}", response_model=EventSchema)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    """Update an event"""
    event = get_event_or_404(event_id, db)
    
    update_data = event_update.dict(exclude_unset=True)
    
    # Verify venue exists if venue_id is being updated
    if "venue_id" in update_data:
        from app.dependencies import get_venue_or_404
        get_venue_or_404(update_data["venue_id"], db)
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    event = get_event_or_404(event_id, db)
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"} 