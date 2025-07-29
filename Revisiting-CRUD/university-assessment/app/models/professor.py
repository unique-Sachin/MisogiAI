from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional


class ProfessorBase(BaseModel):
    """Base professor model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Professor's full name")
    email: EmailStr = Field(..., description="Professor's email address")
    department: str = Field(..., min_length=1, max_length=100, description="Department of the professor")
    hire_date: str = Field(..., description="Date when the professor was hired (YYYY-MM-DD)")

class ProfessorCreate(ProfessorBase):
    """Model for creating a new professor"""
    pass

class ProfessorUpdate(BaseModel):
    """Model for updating professor information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    hire_date: Optional[str] = None

class Professor(ProfessorBase):
    """Complete professor model with ID"""
    id: int = Field(..., description="Unique professor ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Dr. Jane Smith",
                "email": "dr.jane.smith@example.com",
                "department": "Computer Science",
                "hire_date": "2020-01-15"
            }
        }

# Dictionary-based database
professors_db: Dict[int, Professor] = {}    

# Counter for generating new professor IDs
next_professor_id = 1

def get_next_professor_id() -> int:
    """Generate the next available professor ID"""
    global next_professor_id
    current_id = next_professor_id
    next_professor_id += 1
    return current_id

def create_professor(professor_data: ProfessorCreate) -> Professor:
    """Create a new professor and add it to the database"""
    global professors_db
    professor_id = get_next_professor_id()
    new_professor = Professor(id=professor_id, **professor_data.dict())
    professors_db[professor_id] = new_professor
    return new_professor

def get_professor(professor_id: int) -> Optional[Professor]:
    """Retrieve a professor by ID"""
    return professors_db.get(professor_id)

def get_all_professors() -> List[Professor]:
    """Retrieve all professors"""
    return list(professors_db.values())

def update_professor(professor_id: int, professor_update: ProfessorUpdate) -> Optional[Professor]:
    """Update a professor's information"""
    if professor_id not in professors_db:
        return None
    existing_professor = professors_db[professor_id]
    updated_data = existing_professor.copy(update=professor_update.dict(exclude_unset=True))
    professors_db[professor_id] = updated_data
    return updated_data

def delete_professor(professor_id: int) -> bool:
    """Delete a professor by ID"""
    if professor_id in professors_db:
        del professors_db[professor_id]
        return True
    return False

__all__ = [
    "Professor",
    "ProfessorBase",
    "ProfessorCreate",
    "ProfessorUpdate",
    "create_professor",
    "get_professor",
    "get_all_professors",
    "update_professor",
    "delete_professor"
]
# Sample data for testing
def sample_professors() -> List[Professor]:
    """Populate the database with sample professors for testing"""
    return [
        Professor(id=1, name="Dr. John Doe", email="dr.john.doe@example.com", department="Computer Science", hire_date="2020-01-15"),
        Professor(id=2, name="Dr. Jane Smith", email="dr.jane.smith@example.com", department="Mathematics", hire_date="2019-03-22"),
        Professor(id=3, name="Dr. Emily Johnson", email="dr.emily.johnson@example.com", department="Physics", hire_date="2021-07-30")
    ]
    
def populate_sample_data() -> Dict[int, Professor]:
    """Populate the database with sample professors"""  
    for professor in sample_professors():
        professors_db[professor.id] = professor
    return professors_db
populate_sample_data()
