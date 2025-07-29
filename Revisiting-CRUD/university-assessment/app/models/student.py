from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional


class StudentBase(BaseModel):
    """Base student model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Student's full name")
    email: EmailStr = Field(..., description="Student's email address")
    major: str = Field(..., min_length=1, max_length=100, description="Student's major")
    year: int = Field(..., ge=1, le=6, description="Year of study (1-6)")
    gpa: float = Field(..., ge=0.0, le=4.0, description="Grade Point Average (0.0-4.0)")


class StudentCreate(StudentBase):
    """Model for creating a new student"""
    pass


class StudentUpdate(BaseModel):
    """Model for updating student information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    major: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1, le=6)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)


class Student(StudentBase):
    """Complete student model with ID"""
    id: int = Field(..., description="Unique student ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@university.edu",
                "major": "Computer Science",
                "year": 3,
                "gpa": 3.75
            }
        }


# Dictionary-based database
students_db: Dict[int, Student] = {}

# Counter for generating new student IDs
next_student_id = 1


def get_next_id() -> int:
    """Generate the next available student ID"""
    global next_student_id
    current_id = next_student_id
    next_student_id += 1
    return current_id


def create_student(student_data: StudentCreate) -> Student:
    """Create a new student in the database"""
    student_id = get_next_id()
    student = Student(id=student_id, **student_data.dict())
    students_db[student_id] = student
    return student


def get_student(student_id: int) -> Optional[Student]:
    """Get a student by ID"""
    return students_db.get(student_id)


def get_all_students() -> list[Student]:
    """Get all students"""
    return list(students_db.values())


def update_student(student_id: int, student_update: StudentUpdate) -> Optional[Student]:
    """Update a student by ID"""
    if student_id not in students_db:
        return None
    
    student = students_db[student_id]
    update_data = student_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(student, field, value)
    
    students_db[student_id] = student
    return student


def delete_student(student_id: int) -> bool:
    """Delete a student by ID"""
    if student_id in students_db:
        del students_db[student_id]
        return True
    return False


# Sample data for testing
def populate_sample_data():
    """Add some sample students to the database"""
    sample_students = [
        StudentCreate(
            name="Alice Johnson",
            email="alice.johnson@university.edu",
            major="Computer Science",
            year=2,
            gpa=3.8
        ),
        StudentCreate(
            name="Bob Smith",
            email="bob.smith@university.edu", 
            major="Mathematics",
            year=4,
            gpa=3.6
        ),
        StudentCreate(
            name="Carol Davis",
            email="carol.davis@university.edu",
            major="Physics",
            year=1,
            gpa=3.9
        )
    ]
    
    for student_data in sample_students:
        create_student(student_data)


# Initialize with sample data
populate_sample_data()