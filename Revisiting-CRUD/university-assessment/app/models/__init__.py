"""
Models package for the University Assessment API.

This package contains Pydantic models for data validation and serialization.
"""

from .student import (
    Student,
    StudentBase,
    StudentCreate,
    StudentUpdate,
    create_student,
    get_student,
    get_all_students,
    update_student,
    delete_student
)

from .course import (
    Course,
    CourseCreate,
    CourseUpdate,
    create_course,
    get_course,
    get_all_courses,
    update_course,
    delete_course
)

from .enrollment import (
    Enrollment,
    EnrollmentBase,
    EnrollmentCreate,
    EnrollmentUpdate,
    GradeEnum,
    create_enrollment,
    get_enrollment,
    get_all_enrollments,
    get_enrollments_by_student,
    get_enrollments_by_course,
    update_enrollment,
    delete_enrollment,
    get_enrollment_by_student_course
)

__all__ = [
    "Student",
    "StudentBase", 
    "StudentCreate",
    "StudentUpdate",
    "create_student",
    "get_student",
    "get_all_students",
    "update_student",
    "delete_student",
    "Course",
    "CourseCreate",
    "CourseUpdate",
    "create_course",
    "get_course",
    "get_all_courses",
    "update_course",
    "delete_course",
    "Enrollment",
    "EnrollmentBase",
    "EnrollmentCreate",
    "EnrollmentUpdate",
    "GradeEnum",
    "create_enrollment",
    "get_enrollment",
    "get_all_enrollments",
    "get_enrollments_by_student",
    "get_enrollments_by_course",
    "update_enrollment",
    "delete_enrollment",
    "get_enrollment_by_student_course"
]