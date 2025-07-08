from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import engine, Base
from app.routers import venues, events, ticket_types, bookings

# Create database tables
Base.metadata.create_all(bind=engine)

# Import all schemas to ensure they're available
from app.schemas import booking, venue, event, ticket_type

# Create FastAPI app
app = FastAPI(
    title="Ticket Booking System",
    description="A comprehensive ticket booking system with database relationships",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(venues.router)
app.include_router(events.router)
app.include_router(ticket_types.router)
app.include_router(bookings.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 