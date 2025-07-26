class Course:
    all_courses = []
    total_enrollments = 0

    def __init__(self, course_code, title, instructor, credits, max_students):
        self.course_code = course_code
        self.title = title
        self.instructor = instructor
        self.credits = credits
        self.max_students = max_students
        self.enrolled_students = []
        self.grades = {}
        self.waitlist = []
        Course.all_courses.append(self)

    def __str__(self):
        return f"{self.course_code} - {self.title} ({self.instructor})"

    def get_available_spots(self):
        return self.max_students - len(self.enrolled_students)

    def get_enrollment_count(self):
        return len(self.enrolled_students)

    def enroll(self, student):
        if len(self.enrolled_students) < self.max_students:
            self.enrolled_students.append(student)
            Course.total_enrollments += 1
            return "Enrolled successfully."
        else:
            self.waitlist.append(student)
            return "Course is full. Added to waitlist."

    def add_grade(self, student_id, grade):
        self.grades[student_id] = grade

    def get_course_statistics(self):
        if not self.grades:
            return {"average": None, "min": None, "max": None}
        values = list(self.grades.values())
        return {
            "average": round(sum(values) / len(values), 2),
            "min": min(values),
            "max": max(values)
        }

    def is_full(self):
        return len(self.enrolled_students) >= self.max_students

    @classmethod
    def get_total_enrollments(cls):
        return cls.total_enrollments


class Student:
    all_students = []
    total_grades = 0
    cumulative_gpa_sum = 0

    def __init__(self, student_id, name, email, program):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.program = program
        self.enrollments = []
        self.grades = {}  # course_code: grade
        Student.all_students.append(self)

    def __str__(self):
        return f"{self.name} ({self.program})"

    def enroll_in_course(self, course):
        message = course.enroll(self)
        if "Enrolled successfully" in message:
            self.enrollments.append(course)
        return message

    def add_grade(self, course_code, grade):
        self.grades[course_code] = grade

    def calculate_gpa(self):
        if not self.grades:
            return 0.0
        total_points = 0
        total_credits = 0
        for course in self.enrollments:
            if course.course_code in self.grades:
                total_points += self.grades[course.course_code] * course.credits
                total_credits += course.credits
        gpa = round(total_points / total_credits, 2) if total_credits else 0.0
        return gpa

    def get_transcript(self):
        return {code: grade for code, grade in self.grades.items()}

    @classmethod
    def get_total_students(cls):
        return len(cls.all_students)

    @classmethod
    def get_average_gpa(cls):
        total = 0
        count = 0
        for student in cls.all_students:
            gpa = student.calculate_gpa()
            if gpa > 0:
                total += gpa
                count += 1
        return round(total / count, 2) if count > 0 else 0.0

    @classmethod
    def get_top_students(cls, n):
        scored = [(s.name, s.calculate_gpa()) for s in cls.all_students if s.calculate_gpa() > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n]
    


# Test Case 1
math_course = Course("MATH101", "Calculus I", "Dr. Smith", 3, 30)
physics_course = Course("PHYS101", "Physics I", "Dr. Johnson", 4, 25)
cs_course = Course("CS101", "Programming Basics", "Prof. Brown", 3, 20)
print(f"Course: {math_course}")
print(f"Available spots in Math: {math_course.get_available_spots()}")

# Test Case 2
student1 = Student("S001", "Alice Wilson", "alice@university.edu", "Computer Science")
student2 = Student("S002", "Bob Davis", "bob@university.edu", "Mathematics")
student3 = Student("S003", "Carol Lee", "carol@university.edu", "Physics")
print(f"Student: {student1}")
print(f"Total students: {Student.get_total_students()}")

# Test Case 3
enrollment1 = student1.enroll_in_course(math_course)
enrollment = student1.enroll_in_course(cs_course)
enrollment3 = student2.enroll_in_course(math_course)
print(f"Alice's enrollment in Math: {enrollment1}")
print(f"Math course enrollment count: {math_course.get_enrollment_count()}")

# Test Case 4
student1.add_grade("MATH101", 85.5)
student1.add_grade("CS101", 92.0)
student2.add_grade("MATH101", 78.3)
print(f"Alice's GPA: {student1.calculate_gpa()}")
print(f"Alice's transcript: {student1.get_transcript()}")

# Test Case 5
math_course.add_grade("S001", 85.5)
math_course.add_grade("S002", 78.3)
course_stats = math_course.get_course_statistics()
print(f"Math course statistics: {course_stats}")

# Test Case 6
total_enrollments = Course.get_total_enrollments()
print(f"Total enrollments across all courses: {total_enrollments}")
average_gpa = Student.get_average_gpa()
print(f"University average GPA: {average_gpa}")
top_students = Student.get_top_students(2)
print(f"Top 2 students: {top_students}")

# Test Case 7
for i in range(25):  # Math has 30 seats, 2 filled earlier
    temp_student = Student(f"S{100+i}", f"Student {i}", f"student{i}@uni.edu", "General")
    result = temp_student.enroll_in_course(math_course)
print(f"Course full status: {math_course.is_full()}")
print(f"Waitlist size: {len(math_course.waitlist)}")