# Expense Tracker with FastAPI

A modern, full-featured expense tracking application built with FastAPI, SQLAlchemy, and SQLite. Features a responsive web interface and comprehensive REST API.

## Features

### 🎯 Core Functionality
- **CRUD Operations**: Create, read, update, and delete expenses
- **Category Management**: Predefined categories with filtering
- **Date Filtering**: Filter expenses by date range
- **Real-time Summary**: Total expenses and category breakdown
- **Data Validation**: Comprehensive input validation and error handling

### 🎨 User Interface
- **Modern Design**: Bootstrap 5 with custom styling
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Forms**: Real-time validation and feedback
- **Category Filtering**: Dynamic table filtering by category
- **Delete Confirmation**: Modal dialogs for safe deletion
- **Currency Formatting**: Proper currency display
- **Loading States**: Visual feedback for user actions

### 🔧 Technical Features
- **FastAPI Framework**: High-performance async API
- **SQLite Database**: Lightweight, serverless database
- **SQLAlchemy ORM**: Type-safe database operations
- **Pydantic Validation**: Request/response data validation
- **Auto-generated Docs**: Interactive API documentation
- **Sample Data**: Pre-populated test data

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Quick Start

1. **Clone or download the project files**
   ```bash
   # Ensure you have all the project files in your directory
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

## Project Structure

```
expense-tracker/
├── main.py              # FastAPI application and routes
├── database.py          # Database configuration
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic validation models
├── crud.py              # Database CRUD operations
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── templates/
│   └── index.html      # Main web interface template
└── static/
    ├── style.css       # Custom CSS styles
    └── script.js       # JavaScript functionality
```

## API Endpoints

### Expense Management

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/expenses` | Get all expenses | `skip`, `limit`, `start_date`, `end_date` |
| POST | `/expenses` | Create new expense | Request body with expense data |
| PUT | `/expenses/{expense_id}` | Update expense | `expense_id`, request body |
| DELETE | `/expenses/{expense_id}` | Delete expense | `expense_id` |
| GET | `/expenses/category/{category}` | Filter by category | `category` |
| GET | `/expenses/total` | Get totals and breakdown | `start_date`, `end_date` |

### Example API Usage

**Create Expense:**
```bash
curl -X POST "http://localhost:8000/expenses" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 25.50,
       "category": "Food",
       "description": "Lunch at restaurant"
     }'
```

**Get Expenses with Date Filter:**
```bash
curl "http://localhost:8000/expenses?start_date=2025-01-01&end_date=2025-01-31"
```

**Get Total Expenses:**
```bash
curl "http://localhost:8000/expenses/total"
```

## Categories

The application supports the following predefined categories:
- Food
- Transport
- Utilities
- Entertainment
- Healthcare
- Shopping
- Education
- Other

## Data Validation

### Expense Creation/Update Rules
- **Amount**: Must be positive (> 0)
- **Category**: Must be from predefined list
- **Description**: Required, 1-255 characters
- **Date**: Optional, defaults to current datetime

### Error Handling
- 400: Bad Request (validation errors, invalid dates)
- 404: Not Found (expense doesn't exist)
- 422: Unprocessable Entity (Pydantic validation errors)

## Database Schema

### Expense Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    amount FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

## Development

### Adding New Categories
1. Update `ExpenseCategory` enum in `models.py`
2. Categories will automatically appear in the UI

### Database Operations
- Database file: `expenses.db` (created automatically)
- Sample data: Automatically generated on first run
- Reset database: Delete `expenses.db` file and restart

### Customizing the UI
- Modify `templates/index.html` for layout changes
- Update `static/style.css` for styling
- Enhance `static/script.js` for functionality

## Testing

### Manual Testing
1. Open http://localhost:8000
2. Add sample expenses using the form
3. Test category filtering
4. Try deleting expenses
5. Verify date ranges work

### API Testing
- Use the interactive docs at http://localhost:8000/docs
- Test all endpoints with various parameters
- Verify error handling with invalid data

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Database Issues:**
```bash
# Delete database file to reset
rm expenses.db  # or del expenses.db on Windows
python main.py
```

**Port Already in Use:**
```python
# Change port in main.py
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

## Production Deployment

For production deployment, consider:

1. **Use PostgreSQL** instead of SQLite
2. **Environment Variables** for configuration
3. **Docker** containerization
4. **Reverse Proxy** (nginx)
5. **HTTPS** certificates
6. **Database Migrations** with Alembic

Example production run:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions:
- Check the API documentation at `/docs`
- Review this README
- Create an issue for bugs or feature requests 