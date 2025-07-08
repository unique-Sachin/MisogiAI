# 🎫 FastAPI Ticket Booking System

A comprehensive, production-ready ticket booking system built with FastAPI, SQLAlchemy, and modern web technologies. This system provides complete CRUD operations, advanced search capabilities, revenue analytics, and a responsive web interface.

## 🚀 Features

### Core Functionality
- **🏟️ Venue Management**: Create, read, update, and delete venues with capacity management
- **🎪 Event Management**: Organize events with date/time scheduling and ticket limits
- **🎟️ Ticket Types**: Multiple ticket categories (General, VIP, etc.) with different pricing
- **📋 Booking System**: Complete booking workflow with confirmation codes and status tracking
- **🔍 Advanced Search**: Multi-criteria search across events, venues, customers, and booking status
- **📊 Analytics Dashboard**: Real-time revenue tracking, occupancy rates, and booking statistics

### Advanced Features
- **✅ Capacity Validation**: Prevents overbooking with real-time ticket availability
- **💰 Revenue Analytics**: Event-wise and system-wide revenue reporting
- **📈 Occupancy Tracking**: Venue utilization statistics
- **🔄 Status Management**: Booking lifecycle (pending → confirmed → cancelled)
- **🔗 Database Relationships**: Properly structured relational data with foreign keys
- **🌐 Modern Web UI**: Responsive interface with real-time updates

## 🛠️ Technologies Used

- **Backend**: FastAPI 0.104.1
- **Database**: SQLAlchemy 2.0+ with SQLite
- **Validation**: Pydantic 2.10+
- **Server**: Uvicorn with auto-reload
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Modern CSS with glass morphism effects
- **Forms**: Python-multipart for form handling

## 📦 Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd Q3
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the application**
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Database Schema

### Models & Relationships

```
Venue (1) ──→ (Many) Event (1) ──→ (Many) Booking (Many) ──→ (1) TicketType
```

#### Venue
- `id`: Primary key
- `name`: Venue name
- `address`: Physical address
- `capacity`: Maximum occupancy
- `description`: Venue description

#### Event
- `id`: Primary key
- `name`: Event name
- `description`: Event description
- `event_date`: Scheduled date/time
- `venue_id`: Foreign key to Venue
- `max_tickets`: Maximum tickets available
- `created_at`: Creation timestamp

#### TicketType
- `id`: Primary key
- `name`: Ticket category (e.g., "General", "VIP")
- `price`: Ticket price
- `description`: Ticket description

#### Booking
- `id`: Primary key
- `confirmation_code`: Unique booking code
- `customer_name`: Customer name
- `customer_email`: Customer email
- `quantity`: Number of tickets
- `total_amount`: Total cost
- `status`: Booking status (pending/confirmed/cancelled)
- `booking_date`: Booking timestamp
- `event_id`: Foreign key to Event
- `ticket_type_id`: Foreign key to TicketType

## 🔗 API Endpoints

### Venues
- `GET /venues/` - List all venues
- `POST /venues/` - Create new venue
- `GET /venues/{id}` - Get venue details
- `PUT /venues/{id}` - Update venue
- `DELETE /venues/{id}` - Delete venue
- `GET /venues/{id}/events` - Get venue events
- `GET /venues/{id}/occupancy` - Get occupancy statistics

### Events
- `GET /events/` - List all events
- `POST /events/` - Create new event
- `GET /events/{id}` - Get event details
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event
- `GET /events/{id}/bookings` - Get event bookings
- `GET /events/{id}/available-tickets` - Get available tickets
- `GET /events/{id}/revenue` - Get event revenue

### Ticket Types
- `GET /ticket-types/` - List all ticket types
- `POST /ticket-types/` - Create new ticket type
- `GET /ticket-types/{id}` - Get ticket type details
- `PUT /ticket-types/{id}` - Update ticket type
- `DELETE /ticket-types/{id}` - Delete ticket type
- `GET /ticket-types/{id}/bookings` - Get ticket type bookings

### Bookings
- `GET /bookings/` - List all bookings with details
- `POST /bookings/` - Create new booking
- `GET /bookings/{id}` - Get booking details
- `PUT /bookings/{id}` - Update booking
- `DELETE /bookings/{id}` - Cancel booking
- `PATCH /bookings/{id}/status` - Update booking status
- `GET /bookings/search` - Advanced search with filters
- `GET /bookings/stats` - System statistics

### Search Parameters
- `customer_name`: Filter by customer name
- `event`: Filter by event name
- `venue`: Filter by venue name
- `ticket_type`: Filter by ticket type
- `status`: Filter by booking status
- `event_id`: Filter by event ID

## 💻 Web Interface

### Dashboard Sections

1. **📊 Dashboard**: System overview with key metrics
2. **🏟️ Venues**: Venue management interface
3. **🎪 Events**: Event creation and management
4. **🎟️ Ticket Types**: Ticket category management
5. **📋 Bookings**: Booking management and status updates
6. **🔍 Search**: Advanced booking search with multiple filters

### Key Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data refresh
- **Form Validation**: Client-side validation with error handling
- **Modern UI**: Glass morphism effects and smooth animations
- **Status Indicators**: Visual booking status representation

## 🧪 Testing Examples

### Create a Venue
```bash
curl -X POST "http://localhost:8000/venues/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Madison Square Garden",
    "address": "4 Pennsylvania Plaza, New York, NY 10001",
    "capacity": 20000,
    "description": "The World'\''s Most Famous Arena"
  }'
```

### Create an Event
```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rock Concert",
    "description": "Amazing rock concert",
    "event_date": "2024-03-15T19:00:00",
    "venue_id": 1,
    "max_tickets": 1000
  }'
```

### Create a Booking
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "quantity": 2,
    "event_id": 1,
    "ticket_type_id": 1
  }'
```

### Search Bookings
```bash
# Search by customer name
curl "http://localhost:8000/bookings/search?customer_name=John"

# Search by event
curl "http://localhost:8000/bookings/search?event=Concert"

# Search by status
curl "http://localhost:8000/bookings/search?status=confirmed"
```

## 📊 Analytics Examples

### Get System Statistics
```bash
curl "http://localhost:8000/bookings/stats"
```

**Response:**
```json
{
  "total_bookings": 15,
  "total_events": 5,
  "total_venues": 3,
  "total_revenue": 25750.00,
  "available_tickets": 2847
}
```

### Get Event Revenue
```bash
curl "http://localhost:8000/events/1/revenue"
```

**Response:**
```json
{
  "event_id": 1,
  "event_name": "Rock Concert",
  "total_revenue": 15500.00,
  "total_bookings": 12,
  "tickets_sold": 245,
  "available_tickets": 755
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for configuration:
```env
DATABASE_URL=sqlite:///./booking_system.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Database Migration
The application automatically creates tables on startup. For production:
```bash
# Install Alembic for migrations
pip install alembic

# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use PostgreSQL instead of SQLite
- Add authentication and authorization
- Implement rate limiting
- Add logging and monitoring
- Use environment variables for configuration
- Set up SSL/TLS
- Configure reverse proxy (Nginx)

## 🐛 Troubleshooting

### Common Issues

**Issue**: Server won't start
**Solution**: Check if port 8000 is available, activate virtual environment

**Issue**: Database errors
**Solution**: Delete `booking_system.db` file to reset database

**Issue**: Import errors
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## 📝 API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with:
- **Swagger UI**: Test endpoints directly
- **Request/Response schemas**: Complete data models
- **Authentication**: When implemented
- **Error codes**: HTTP status codes and meanings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@ticketbooking.com
- Documentation: [Link to full documentation]

---

**Built with ❤️ using FastAPI and modern web technologies** 