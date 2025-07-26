from collections import defaultdict

class GradeManager:
    def __init__(self):
        """
        Initialize the grade manager with appropriate defaultdict structures
        Use defaultdict to avoid key existence checks
        """
        # student_grades[student][subject] = list of grades
        self.student_grades = defaultdict(lambda: defaultdict(list))
        # subject_grades[subject] = list of (student, grade)
        self.subject_grades = defaultdict(list)

    def add_grade(self, student_name, subject, grade):
        """
        Add a grade for a student in a specific subject 
        """
        self.student_grades[student_name][subject].append(grade)
        self.subject_grades[subject].append((student_name, grade))

    def get_student_average(self, student_name):
        """
        Calculate average grade for a student across all subjects 
        """
        if student_name not in self.student_grades:
            return 0.0
        total, count = 0, 0
        for grades in self.student_grades[student_name].values():
            total += sum(grades)
            count += len(grades)
        return total / count if count > 0 else 0.0

    def get_subject_statistics(self, subject):
        """
        Get statistics for a specific subject across all students
        """
        grades = [grade for _, grade in self.subject_grades.get(subject, [])]
        if not grades:
            return {
                "average": 0.0,
                "highest": 0.0,
                "lowest": 0.0,
                "student_count": 0
            }
        return {
            "average": sum(grades) / len(grades),
            "highest": max(grades),
            "lowest": min(grades),
            "student_count": len(set(student for student, _ in self.subject_grades[subject]))
        }

    def get_top_students(self, n=3):
        """
        Get top N students based on their overall average 
        """
        averages = [
            (student, self.get_student_average(student))
            for student in self.student_grades
        ]
        # Sort by average in descending order
        return sorted(averages, key=lambda x: x[1], reverse=True)[:n]

    def get_failing_students(self, passing_grade=60):
        """
        Get students who are failing (average below passing grade)
        """
        return [
            (student, avg)
            for student, avg in (
                (student, self.get_student_average(student))
                for student in self.student_grades
            )
            if avg < passing_grade
        ]

# Test your implementation
manager = GradeManager()

# Add sample grades
grades_data = [
    ("Bob", "Math", 15),
    ("Cal", "Science", 6),
    ("Alice", "English", 78),
    ("Alice", "Science", 68),
    ("Bob", "English", 82),
    ("Bob", "Math", 95),
    ("Charlie", "Science", 88),
    ("Charlie", "History", 91),
    ("Diana", "Science", 62),
    ("Diana", "English", 70),
    ("Eve", "Math", 88),
    ("Eve", "Science", 94),
    ("Eve", "English", 85),
    ("Eve", "History", 89)
]

for student, subject, grade in grades_data:
    manager.add_grade(student, subject, grade)

# Test all methods
print("Alice's average:", manager.get_student_average("Alice"))
print("Math statistics:", manager.get_subject_statistics("Math"))
print("Top 3 students:", manager.get_top_students(3))
print("Failing students (below 75):", manager.get_failing_students(75))