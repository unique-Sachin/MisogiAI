from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.ticket_type import TicketType
from app.schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate, TicketType as TicketTypeSchema, TicketTypeWithBookings
from app.dependencies import get_ticket_type_or_404

router = APIRouter(prefix="/ticket-types", tags=["ticket-types"])

@router.post("/", response_model=TicketTypeSchema)
def create_ticket_type(ticket_type: TicketTypeCreate, db: Session = Depends(get_db)):
    """Create a new ticket type"""
    db_ticket_type = TicketType(**ticket_type.dict())
    db.add(db_ticket_type)
    db.commit()
    db.refresh(db_ticket_type)
    return db_ticket_type

@router.get("/", response_model=List[TicketTypeSchema])
def get_all_ticket_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all ticket types"""
    ticket_types = db.query(TicketType).offset(skip).limit(limit).all()
    return ticket_types

@router.get("/{type_id}", response_model=TicketTypeSchema)
def get_ticket_type(type_id: int, db: Session = Depends(get_db)):
    """Get a specific ticket type"""
    return get_ticket_type_or_404(type_id, db)

@router.get("/{type_id}/bookings", response_model=TicketTypeWithBookings)
def get_ticket_type_bookings(type_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a specific ticket type"""
    ticket_type = get_ticket_type_or_404(type_id, db)
    return ticket_type

@router.put("/{type_id}", response_model=TicketTypeSchema)
def update_ticket_type(type_id: int, ticket_type_update: TicketTypeUpdate, db: Session = Depends(get_db)):
    """Update a ticket type"""
    ticket_type = get_ticket_type_or_404(type_id, db)
    
    update_data = ticket_type_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket_type, field, value)
    
    db.commit()
    db.refresh(ticket_type)
    return ticket_type

@router.delete("/{type_id}")
def delete_ticket_type(type_id: int, db: Session = Depends(get_db)):
    """Delete a ticket type"""
    ticket_type = get_ticket_type_or_404(type_id, db)
    db.delete(ticket_type)
    db.commit()
    return {"message": "Ticket type deleted successfully"} 