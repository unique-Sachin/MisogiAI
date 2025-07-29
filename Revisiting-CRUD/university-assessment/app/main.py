from fastapi import APIRouter, FastAPI, HTTPException, status
from typing import List
from models.professor import (Professor, ProfessorUpdate, create_professor, delete_professor, get_all_professors, update_professor, get_professor)
from models.course import (Course, CourseUpdate, create_course, delete_course, get_all_courses, update_course, get_course)
from models.student import (
    Student, 
    StudentCreate, 
    StudentUpdate,
    create_student,
    get_student,
    get_all_students,
    update_student,
    delete_student
)
from models.enrollment import (
    Enrollment,
    EnrollmentCreate,
    EnrollmentUpdate,
    create_enrollment,
    get_enrollment,
    get_all_enrollments,
    get_enrollments_by_student,
    get_enrollments_by_course,
    update_enrollment,
    delete_enrollment,
    get_enrollment_by_student_course
)

app = FastAPI(
    title="University Assessment API",
    description="A simple FastAPI application for managing university students and courses",
    version="1.0.0"
)

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "University Assessment API is running"}


# Student CRUD endpoints
student_router = APIRouter(prefix="/students", tags=["students"])

@student_router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_new_student(student: StudentCreate):
    """Create a new student"""
    new_student = create_student(student)
    return new_student


@student_router.get("/", response_model=List[Student])
def read_students():
    """Get all students"""
    return get_all_students()


@student_router.get("/{student_id}", response_model=Student)
def read_student(student_id: int):
    """Get a specific student by ID"""
    student = get_student(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    return student


@student_router.put("/{student_id}", response_model=Student)
def update_existing_student(student_id: int, student_update: StudentUpdate):
    """Update a student by ID"""
    updated_student = update_student(student_id, student_update)
    if updated_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    return updated_student


@student_router.delete("/{student_id}")
def delete_existing_student(student_id: int):
    """Delete a student by ID"""
    success = delete_student(student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    return {"message": f"Student with ID {student_id} has been deleted successfully"}

# Course CRUD endpoints
course_router = APIRouter(prefix="/courses", tags=["courses"])

@course_router.get("/", response_model=List[Course])
def read_courses():
    """Get all courses"""
    return get_all_courses()

@course_router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_new_course(course: Course):
    """Create a new course"""
    new_course = create_course(course)
    return new_course

@course_router.get("/{course_id}", response_model=Course)
def read_course(course_id: int):
    """Get a specific course by ID"""
    course = get_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    return course

@course_router.put("/{course_id}", response_model=Course)
def update_existing_course(course_id: int, course_update: CourseUpdate):
    """Update a course by ID"""
    updated_course = update_course(course_id, course_update)
    if updated_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    return updated_course

@course_router.delete("/{course_id}")
def delete_existing_course(course_id: int):
    """Delete a course by ID"""
    success = delete_course(course_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    return {"message": f"Course with ID {course_id} has been deleted successfully"}


professor_router = APIRouter(prefix="/professors", tags=["professors"])
@professor_router.get("/", response_model=List[Professor])
def read_professors():
    """Get all professors"""
    return get_all_professors()


@professor_router.post("/", response_model=Professor, status_code=status.HTTP_201_CREATED)
def create_new_professor(professor: Professor):
    """Create a new professor"""
    new_professor = create_professor(professor)
    return new_professor

@professor_router.get("/{professor_id}", response_model=Professor)
def read_professor(professor_id: int):
    """Get a specific professor by ID"""
    professor = get_professor(professor_id)
    if professor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor with ID {professor_id} not found"
        )
    return professor
@professor_router.put("/{professor_id}", response_model=Professor)
def update_existing_professor(professor_id: int, professor_update: ProfessorUpdate):
    """Update a professor by ID"""
    updated_professor = update_professor(professor_id, professor_update)
    if updated_professor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor with ID {professor_id} not found"
        )
    return updated_professor

@professor_router.delete("/{professor_id}")
def delete_existing_professor(professor_id: int):
    """Delete a professor by ID"""
    success = delete_professor(professor_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor with ID {professor_id} not found"
        )
    return {"message": f"Professor with ID {professor_id} has been deleted successfully"}


# Enrollment CRUD endpoints
enrollment_router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@enrollment_router.post("/", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
def create_new_enrollment(enrollment: EnrollmentCreate):
    """Create a new enrollment"""
    try:
        new_enrollment = create_enrollment(enrollment)
        return new_enrollment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@enrollment_router.get("/", response_model=List[Enrollment])
def read_enrollments():
    """Get all enrollments"""
    return get_all_enrollments()

@enrollment_router.get("/{enrollment_id}", response_model=Enrollment)
def read_enrollment(enrollment_id: int):
    """Get a specific enrollment by ID"""
    enrollment = get_enrollment(enrollment_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found"
        )
    return enrollment

@enrollment_router.get("/student/{student_id}", response_model=List[Enrollment])
def read_enrollments_by_student(student_id: int):
    """Get all enrollments for a specific student"""
    enrollments = get_enrollments_by_student(student_id)
    return enrollments

@enrollment_router.get("/course/{course_id}", response_model=List[Enrollment])
def read_enrollments_by_course(course_id: int):
    """Get all enrollments for a specific course"""
    enrollments = get_enrollments_by_course(course_id)
    return enrollments

@enrollment_router.put("/{enrollment_id}", response_model=Enrollment)
def update_existing_enrollment(enrollment_id: int, enrollment_update: EnrollmentUpdate):
    """Update an enrollment by ID (typically to assign/update grade)"""
    updated_enrollment = update_enrollment(enrollment_id, enrollment_update)
    if updated_enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found"
        )
    return updated_enrollment

@enrollment_router.delete("/{enrollment_id}")
def delete_existing_enrollment(enrollment_id: int):
    """Delete an enrollment by ID"""
    success = delete_enrollment(enrollment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with ID {enrollment_id} not found"
        )
    return {"message": f"Enrollment with ID {enrollment_id} has been deleted successfully"}


# Include routers in the main application
app.include_router(student_router)
app.include_router(course_router)
app.include_router(professor_router)
app.include_router(enrollment_router)