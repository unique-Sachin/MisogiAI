from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.venue import Venue
from app.models.ticket_type import TicketType
from app.schemas.booking import BookingCreate, BookingUpdate, BookingStatusUpdate, Booking as BookingSchema, BookingWithDetails, BookingStats
from app.dependencies import get_booking_or_404, get_event_or_404, get_ticket_type_or_404, generate_confirmation_code, validate_booking_capacity
from sqlalchemy import func, and_, or_

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingSchema)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """Create a new booking"""
    # Verify event and ticket type exist
    event = get_event_or_404(booking.event_id, db)
    ticket_type = get_ticket_type_or_404(booking.ticket_type_id, db)
    
    # Validate capacity
    if not validate_booking_capacity(event, booking.quantity, db):
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    
    # Calculate total amount
    total_amount = ticket_type.price * booking.quantity
    
    # Generate confirmation code
    confirmation_code = generate_confirmation_code()
    
    # Ensure confirmation code is unique
    while db.query(Booking).filter(Booking.confirmation_code == confirmation_code).first():
        confirmation_code = generate_confirmation_code()
    
    db_booking = Booking(
        **booking.dict(),
        confirmation_code=confirmation_code,
        total_amount=total_amount
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/", response_model=List[BookingWithDetails])
def get_all_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all bookings with event, venue, and ticket type details"""
    bookings = db.query(Booking).options(
        joinedload(Booking.event).joinedload(Event.venue),
        joinedload(Booking.ticket_type)
    ).offset(skip).limit(limit).all()
    
    # Manually populate venue field for each booking
    result = []
    for booking in bookings:
        booking_dict = BookingWithDetails.from_orm(booking)
        if booking.event and booking.event.venue:
            booking_dict.venue = booking.event.venue
        result.append(booking_dict)
    
    return result

@router.get("/search", response_model=List[BookingWithDetails])
def search_bookings(
    event: Optional[str] = Query(None, description="Event name to filter by"),
    venue: Optional[str] = Query(None, description="Venue name to filter by"),
    ticket_type: Optional[str] = Query(None, description="Ticket type to filter by"),
    status: Optional[BookingStatus] = Query(None, description="Booking status to filter by"),
    customer_name: Optional[str] = Query(None, description="Customer name to filter by"),
    event_id: Optional[int] = Query(None, description="Event ID to filter by"),
    db: Session = Depends(get_db)
):
    """Search bookings by various criteria"""
    query = db.query(Booking).options(
        joinedload(Booking.event).joinedload(Event.venue),
        joinedload(Booking.ticket_type)
    )
    
    if event:
        query = query.join(Event).filter(Event.name.ilike(f"%{event}%"))
    
    if venue:
        query = query.join(Event).join(Venue).filter(Venue.name.ilike(f"%{venue}%"))
    
    if ticket_type:
        query = query.join(TicketType).filter(TicketType.name.ilike(f"%{ticket_type}%"))
    
    if status:
        query = query.filter(Booking.status == status)
    
    if customer_name:
        query = query.filter(Booking.customer_name.ilike(f"%{customer_name}%"))
    
    if event_id:
        query = query.filter(Booking.event_id == event_id)
    
    bookings = query.all()
    
    # Manually populate venue field for each booking
    result = []
    for booking in bookings:
        booking_dict = BookingWithDetails.from_orm(booking)
        if booking.event and booking.event.venue:
            booking_dict.venue = booking.event.venue
        result.append(booking_dict)
    
    return result

@router.get("/stats", response_model=BookingStats)
def get_booking_stats(db: Session = Depends(get_db)):
    """Get booking system statistics"""
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0
    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_venues = db.query(func.count(Venue.id)).scalar() or 0
    
    total_revenue = db.query(func.sum(Booking.total_amount)).filter(
        Booking.status != "cancelled"
    ).scalar() or 0
    
    # Calculate total available tickets across all events
    total_max_tickets = db.query(func.sum(Event.max_tickets)).scalar() or 0
    total_booked_tickets = db.query(func.sum(Booking.quantity)).filter(
        Booking.status != "cancelled"
    ).scalar() or 0
    available_tickets = total_max_tickets - total_booked_tickets
    
    return BookingStats(
        total_bookings=int(total_bookings),
        total_events=int(total_events),
        total_venues=int(total_venues),
        total_revenue=float(total_revenue),
        available_tickets=max(0, int(available_tickets))
    )

@router.get("/{booking_id}", response_model=BookingWithDetails)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get a specific booking with details"""
    booking = db.query(Booking).options(
        joinedload(Booking.event).joinedload(Event.venue),
        joinedload(Booking.ticket_type)
    ).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Manually populate venue field
    booking_dict = BookingWithDetails.from_orm(booking)
    if booking.event and booking.event.venue:
        booking_dict.venue = booking.event.venue
    
    return booking_dict

@router.put("/{booking_id}", response_model=BookingSchema)
def update_booking(booking_id: int, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    """Update booking details"""
    booking = get_booking_or_404(booking_id, db)
    
    update_data = booking_update.dict(exclude_unset=True)
    
    # If quantity is being updated, validate capacity and recalculate total
    if "quantity" in update_data:
        event = booking.event
        # Calculate current capacity excluding this booking
        current_quantity = booking.quantity
        new_quantity = update_data["quantity"]
        quantity_diff = new_quantity - current_quantity
        
        if quantity_diff > 0:  # Increasing quantity
            from app.dependencies import calculate_available_tickets
            available = calculate_available_tickets(event, db) + current_quantity
            if new_quantity > available:
                raise HTTPException(status_code=400, detail="Not enough tickets available")
        
        # Recalculate total amount
        booking.total_amount = booking.ticket_type.price * new_quantity
    
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    return booking

@router.patch("/{booking_id}/status", response_model=BookingSchema)
def update_booking_status(booking_id: int, status_update: BookingStatusUpdate, db: Session = Depends(get_db)):
    """Update booking status (confirmed, cancelled, pending)"""
    booking = get_booking_or_404(booking_id, db)
    booking.status = status_update.status
    
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """Cancel a booking"""
    booking = get_booking_or_404(booking_id, db)
    db.delete(booking)
    db.commit()
    return {"message": "Booking cancelled successfully"} 