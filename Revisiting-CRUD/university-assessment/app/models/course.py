from pydantic import BaseModel, Field
from typing import Dict, Optional   
from typing import List

class CourseBase(BaseModel):
    """Base course model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Course name")
    code: str = Field(..., min_length=1, max_length=20, description="Course code")
    credits: int = Field(..., ge=1, le=6, description="Number of credits for the course")
    professor_id: int = Field(..., description="ID of the professor teaching the course")
    max_capacity: int = Field(..., ge=1, description="Maximum capacity of students for the course")


class CourseCreate(CourseBase):
    """Model for creating a new course"""
    pass

class CourseUpdate(BaseModel):
    """Model for updating course information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    credits: Optional[int] = Field(None, ge=1, le=6)
    professor_id: Optional[int] = None
    max_capacity: Optional[int] = Field(None, ge=1)

class Course(CourseBase):
    """Complete course model with ID"""
    id: int = Field(..., description="Unique course ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Introduction to Programming",
                "code": "CS101",
                "credits": 3,
                "professor_id": 2,
                "max_capacity": 30
            }
        }

# Dictionary-based database
courses_db: Dict[int, Course] = {}
# Counter for generating new course IDs
next_course_id = 1


def get_next_course_id() -> int:   
    """Generate the next available course ID"""
    global next_course_id
    current_id = next_course_id
    next_course_id += 1
    return current_id

def create_course(course_data: CourseCreate) -> Course:
    """Create a new course and add it to the database"""
    global courses_db
    course_id = get_next_course_id()
    new_course = Course(id=course_id, **course_data.dict())
    courses_db[course_id] = new_course
    return new_course

def get_course(course_id: int) -> Optional[Course]:
    """Retrieve a course by its ID"""
    return courses_db.get(course_id)

def get_all_courses() -> List[Course]:
    """Get a list of all courses"""
    return list(courses_db.values())

def update_course(course_id: int, course_update: CourseUpdate) -> Optional[Course]:
    """Update an existing course by its ID"""
    global courses_db
    if course_id not in courses_db:
        return None
    existing_course = courses_db[course_id]
    updated_data = existing_course.model_dump(exclude_unset=True)
    updated_data.update(course_update.model_dump(exclude_unset=True))
    updated_course = Course(id=course_id, **updated_data)
    courses_db[course_id] = updated_course
    return updated_course

def delete_course(course_id: int) -> bool:
    """Delete a course by its ID"""
    global courses_db
    if course_id in courses_db:
        del courses_db[course_id]
        return True
    return False


# Sample data for testing
def sample_courses() -> List[Course]:
    """Populate the database with sample courses for testing"""
    return [
        create_course(CourseCreate(name="Data Structures", code="CS102", credits=3, professor_id=1, max_capacity=40)),
        create_course(CourseCreate(name="Database Systems", code="CS201", credits=4, professor_id=2, max_capacity=35)),
        create_course(CourseCreate(name="Web Development", code="CS301", credits=3, professor_id=3, max_capacity=30))
    ]
def populate_sample_data():
    """Populate the database with sample courses"""
    sample_courses()
    return get_all_courses()
populate_sample_data()  # Call to populate sample data on module load
