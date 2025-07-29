# University Assessment API

A comprehensive FastAPI-based REST API for managing university data including students, courses, professors, and enrollments. This project demonstrates full CRUD operations with dictionary-based database storage.

## 🚀 Features

- **Student Management**: Create, read, update, and delete student records
- **Course Management**: Manage course catalog with details like credits and capacity
- **Professor Management**: Handle professor information and assignments
- **Enrollment System**: Track student enrollments in courses with grades
- **Grade Management**: Support for standard academic grading system
- **Data Validation**: Comprehensive input validation using Pydantic
- **Interactive API Documentation**: Auto-generated docs with Swagger UI
- **Sample Data**: Pre-loaded test data for immediate testing

## 🏗️ Project Structure

```
university-assessment/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and routes
│   └── models/
│       ├── __init__.py
│       ├── student.py          # Student model and operations
│       ├── course.py           # Course model and operations
│       ├── professor.py        # Professor model and operations
│       └── enrollment.py       # Enrollment model and operations
├── .venv/                      # Virtual environment
└── README.md
```

## 📋 Models

### Student
- **Fields**: ID, name, email, major, year (1-6), GPA (0.0-4.0)
- **Validation**: Email format, GPA range, year constraints

### Course
- **Fields**: ID, name, code, credits (1-6), professor_id, max_capacity
- **Validation**: Course code format, credit limits

### Professor
- **Fields**: ID, name, email, department, hire_date
- **Validation**: Email format, hire date constraints

### Enrollment
- **Fields**: ID, student_id, course_id, enrollment_date, grade
- **Grades**: A+, A, A-, B+, B, B-, C+, C, C-, D+, D, F, I, W, P, NP
- **Business Logic**: Prevents duplicate enrollments

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd university-assessment
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn email-validator
   ```

## 🚀 Running the Application

1. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

2. **Start the server**
   ```bash
   cd app
   uvicorn main:app --reload --port 8001
   ```

3. **Access the API**
   - API Base URL: `http://127.0.0.1:8001`
   - Interactive Documentation: `http://127.0.0.1:8001/docs`
   - Alternative Documentation: `http://127.0.0.1:8001/redoc`

## 📚 API Endpoints

### Health Check
- `GET /` - Health check endpoint

### Students
- `GET /students/` - Get all students
- `POST /students/` - Create a new student
- `GET /students/{id}` - Get student by ID
- `PUT /students/{id}` - Update student
- `DELETE /students/{id}` - Delete student

### Courses
- `GET /courses/` - Get all courses
- `POST /courses/` - Create a new course
- `GET /courses/{id}` - Get course by ID
- `PUT /courses/{id}` - Update course
- `DELETE /courses/{id}` - Delete course

### Professors
- `GET /professors/` - Get all professors
- `POST /professors/` - Create a new professor
- `GET /professors/{id}` - Get professor by ID
- `PUT /professors/{id}` - Update professor
- `DELETE /professors/{id}` - Delete professor

### Enrollments
- `GET /enrollments/` - Get all enrollments
- `POST /enrollments/` - Create a new enrollment
- `GET /enrollments/{id}` - Get enrollment by ID
- `GET /enrollments/student/{student_id}` - Get enrollments for a student
- `GET /enrollments/course/{course_id}` - Get enrollments for a course
- `PUT /enrollments/{id}` - Update enrollment (assign/update grade)
- `DELETE /enrollments/{id}` - Delete enrollment

## 📝 Example Usage

### Create a Student
```bash
curl -X POST "http://127.0.0.1:8001/students/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john.doe@university.edu",
       "major": "Computer Science",
       "year": 2,
       "gpa": 3.5
     }'
```

### Create a Course
```bash
curl -X POST "http://127.0.0.1:8001/courses/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Data Structures",
       "code": "CS102",
       "credits": 3,
       "professor_id": 1,
       "max_capacity": 40
     }'
```

### Enroll a Student
```bash
curl -X POST "http://127.0.0.1:8001/enrollments/" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": 1,
       "course_id": 1
     }'
```

### Assign a Grade
```bash
curl -X PUT "http://127.0.0.1:8001/enrollments/1" \
     -H "Content-Type: application/json" \
     -d '{
       "grade": "A"
     }'
```

## 🔍 Sample Data

The application comes pre-loaded with sample data:

### Students (3)
- Alice Johnson (Computer Science, Year 2, GPA 3.8)
- Bob Smith (Mathematics, Year 4, GPA 3.6)
- Carol Davis (Physics, Year 1, GPA 3.9)

### Courses (3)
- Data Structures (CS102, 3 credits)
- Database Systems (CS201, 4 credits)
- Web Development (CS301, 3 credits)

### Enrollments (5)
- Students enrolled in various courses with some grades assigned

## 🛡️ Data Validation

### Student Validation
- Name: 1-100 characters
- Email: Valid email format
- Major: 1-100 characters
- Year: 1-6 (academic years)
- GPA: 0.0-4.0

### Course Validation
- Name: 1-100 characters
- Code: 1-20 characters
- Credits: 1-6
- Max capacity: Minimum 1 student

### Enrollment Validation
- Prevents duplicate enrollments
- Enrollment date cannot be in the future
- Grade must be from predefined enum values

## 🏗️ Architecture

### Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the application
- **Python 3.8+**: Programming language

### Design Patterns
- **Repository Pattern**: Separate data access logic in model files
- **Dependency Injection**: Clean separation of concerns
- **Model-View-Controller**: Clear separation of data, business logic, and presentation

### Database
- **In-Memory Dictionary Storage**: Simple dictionary-based storage for demonstration
- **Auto-incrementing IDs**: Automatic ID generation for entities
- **Data Persistence**: Data persists during application runtime

## 🧪 Testing

### Manual Testing
1. Start the application
2. Visit `http://127.0.0.1:8001/docs`
3. Use the interactive documentation to test endpoints
4. Try various CRUD operations with sample data

### API Testing with curl
```bash
# Get all students
curl -X GET "http://127.0.0.1:8001/students/"

# Get student enrollments
curl -X GET "http://127.0.0.1:8001/enrollments/student/1"

# Get course enrollments
curl -X GET "http://127.0.0.1:8001/enrollments/course/1"
```

## 🔮 Future Enhancements

- [ ] Database integration (PostgreSQL/MySQL)
- [ ] Authentication and authorization
- [ ] Role-based access control
- [ ] Course prerequisites system
- [ ] Academic calendar integration
- [ ] Reporting and analytics
- [ ] Email notifications
- [ ] File upload for transcripts
- [ ] Search and filtering capabilities
- [ ] Pagination for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Authors

- **Sachin Mishra** - Initial work

## 📞 Support

For questions or support, please contact:
- Email: [your-email@example.com]
- GitHub: [your-github-username]

---

**Note**: This is a demonstration project using in-memory storage. For production use, integrate with a proper database system and add appropriate security measures.
