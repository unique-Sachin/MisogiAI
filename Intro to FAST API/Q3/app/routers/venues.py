from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueUpdate, Venue as VenueSchema, VenueWithEvents
from app.dependencies import get_venue_or_404

router = APIRouter(prefix="/venues", tags=["venues"])

@router.post("/", response_model=VenueSchema)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
    """Create a new venue"""
    db_venue = Venue(**venue.dict())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

@router.get("/", response_model=List[VenueSchema])
def get_all_venues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all venues"""
    venues = db.query(Venue).offset(skip).limit(limit).all()
    return venues

@router.get("/{venue_id}", response_model=VenueSchema)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """Get a specific venue"""
    return get_venue_or_404(venue_id, db)

@router.get("/{venue_id}/events", response_model=VenueWithEvents)
def get_venue_events(venue_id: int, db: Session = Depends(get_db)):
    """Get all events at a specific venue"""
    venue = get_venue_or_404(venue_id, db)
    return venue

@router.get("/{venue_id}/occupancy")
def get_venue_occupancy(venue_id: int, db: Session = Depends(get_db)):
    """Get venue occupancy statistics"""
    from app.models.event import Event
    from app.models.booking import Booking
    from sqlalchemy import func
    
    venue = get_venue_or_404(venue_id, db)
    
    # Calculate total bookings for this venue
    total_bookings = db.query(func.sum(Booking.quantity)).join(Event).filter(
        Event.venue_id == venue_id,
        Booking.status != "cancelled"
    ).scalar() or 0
    
    # Calculate total events
    total_events = db.query(Event).filter(Event.venue_id == venue_id).count()
    
    # Calculate occupancy rate
    occupancy_rate = (total_bookings / venue.capacity * 100) if venue.capacity > 0 else 0
    
    return {
        "venue_id": venue_id,
        "venue_name": venue.name,
        "capacity": venue.capacity,
        "total_bookings": total_bookings,
        "total_events": total_events,
        "occupancy_rate": round(occupancy_rate, 2)
    }

@router.put("/{venue_id}", response_model=VenueSchema)
def update_venue(venue_id: int, venue_update: VenueUpdate, db: Session = Depends(get_db)):
    """Update a venue"""
    venue = get_venue_or_404(venue_id, db)
    
    update_data = venue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    
    db.commit()
    db.refresh(venue)
    return venue

@router.delete("/{venue_id}")
def delete_venue(venue_id: int, db: Session = Depends(get_db)):
    """Delete a venue"""
    venue = get_venue_or_404(venue_id, db)
    db.delete(venue)
    db.commit()
    return {"message": "Venue deleted successfully"} 