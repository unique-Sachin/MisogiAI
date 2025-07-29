from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from enum import Enum


class GradeEnum(str, Enum):
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    F = "F"
    INCOMPLETE = "I"
    WITHDRAW = "W"
    PASS = "P"
    NO_PASS = "NP"


class EnrollmentBase(BaseModel):
    """Base enrollment model with common fields"""
    student_id: int = Field(..., description="ID of the enrolled student")
    course_id: int = Field(..., description="ID of the course")
    enrollment_date: datetime = Field(default_factory=datetime.now, description="Date of enrollment")
    grade: Optional[GradeEnum] = Field(None, description="Grade received in the course")

    @validator('enrollment_date')
    def validate_enrollment_date(cls, v):
        if v > datetime.now():
            raise ValueError('Enrollment date cannot be in the future')
        return v


class EnrollmentCreate(BaseModel):
    """Model for creating a new enrollment"""
    student_id: int = Field(..., description="ID of the student to enroll")
    course_id: int = Field(..., description="ID of the course to enroll in")
    enrollment_date: Optional[datetime] = Field(None, description="Date of enrollment (defaults to now)")

    @validator('enrollment_date', pre=True, always=True)
    def set_enrollment_date(cls, v):
        return v or datetime.now()


class EnrollmentUpdate(BaseModel):
    """Model for updating enrollment information"""
    grade: Optional[GradeEnum] = Field(None, description="Grade to assign or update")


class Enrollment(EnrollmentBase):
    """Complete enrollment model with ID"""
    id: int = Field(..., description="Unique enrollment ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": 1,
                "course_id": 1,
                "enrollment_date": "2024-01-15T10:30:00",
                "grade": "A"
            }
        }


# Dictionary-based database
enrollments_db: Dict[int, Enrollment] = {}

# Counter for generating new enrollment IDs
next_enrollment_id = 1


def get_next_enrollment_id() -> int:
    """Generate the next available enrollment ID"""
    global next_enrollment_id
    current_id = next_enrollment_id
    next_enrollment_id += 1
    return current_id


def create_enrollment(enrollment_data: EnrollmentCreate) -> Enrollment:
    """Create a new enrollment in the database"""
    # Check if student is already enrolled in this course
    for enrollment in enrollments_db.values():
        if (enrollment.student_id == enrollment_data.student_id and 
            enrollment.course_id == enrollment_data.course_id):
            raise ValueError(f"Student {enrollment_data.student_id} is already enrolled in course {enrollment_data.course_id}")
    
    enrollment_id = get_next_enrollment_id()
    enrollment = Enrollment(id=enrollment_id, **enrollment_data.dict())
    enrollments_db[enrollment_id] = enrollment
    return enrollment


def get_enrollment(enrollment_id: int) -> Optional[Enrollment]:
    """Get an enrollment by ID"""
    return enrollments_db.get(enrollment_id)


def get_all_enrollments() -> List[Enrollment]:
    """Get all enrollments"""
    return list(enrollments_db.values())


def get_enrollments_by_student(student_id: int) -> List[Enrollment]:
    """Get all enrollments for a specific student"""
    return [enrollment for enrollment in enrollments_db.values() 
            if enrollment.student_id == student_id]


def get_enrollments_by_course(course_id: int) -> List[Enrollment]:
    """Get all enrollments for a specific course"""
    return [enrollment for enrollment in enrollments_db.values() 
            if enrollment.course_id == course_id]


def update_enrollment(enrollment_id: int, enrollment_update: EnrollmentUpdate) -> Optional[Enrollment]:
    """Update an enrollment by ID"""
    if enrollment_id not in enrollments_db:
        return None
    
    enrollment = enrollments_db[enrollment_id]
    update_data = enrollment_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(enrollment, field, value)
    
    enrollments_db[enrollment_id] = enrollment
    return enrollment


def delete_enrollment(enrollment_id: int) -> bool:
    """Delete an enrollment by ID"""
    if enrollment_id in enrollments_db:
        del enrollments_db[enrollment_id]
        return True
    return False


def get_enrollment_by_student_course(student_id: int, course_id: int) -> Optional[Enrollment]:
    """Get enrollment by student ID and course ID"""
    for enrollment in enrollments_db.values():
        if enrollment.student_id == student_id and enrollment.course_id == course_id:
            return enrollment
    return None


# Sample data for testing
def populate_sample_data():
    """Add some sample enrollments to the database"""
    sample_enrollments = [
        EnrollmentCreate(
            student_id=1,
            course_id=1,
            enrollment_date=datetime(2024, 1, 15, 10, 30)
        ),
        EnrollmentCreate(
            student_id=1,
            course_id=2,
            enrollment_date=datetime(2024, 1, 16, 14, 0)
        ),
        EnrollmentCreate(
            student_id=2,
            course_id=1,
            enrollment_date=datetime(2024, 1, 15, 11, 0)
        ),
        EnrollmentCreate(
            student_id=2,
            course_id=3,
            enrollment_date=datetime(2024, 1, 17, 9, 30)
        ),
        EnrollmentCreate(
            student_id=3,
            course_id=2,
            enrollment_date=datetime(2024, 1, 16, 15, 30)
        )
    ]
    
    for enrollment_data in sample_enrollments:
        try:
            create_enrollment(enrollment_data)
        except ValueError:
            # Skip if already enrolled
            pass
    
    # Add some grades to existing enrollments
    enrollments = get_all_enrollments()
    if len(enrollments) >= 3:
        update_enrollment(1, EnrollmentUpdate(grade=GradeEnum.A))
        update_enrollment(2, EnrollmentUpdate(grade=GradeEnum.B_PLUS))
        update_enrollment(3, EnrollmentUpdate(grade=GradeEnum.A_MINUS))


# Initialize with sample data
populate_sample_data()
