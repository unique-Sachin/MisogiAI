# List of student records: (student_id, name, grade, age)
students = [
    (101, "Alice", 85, 20),
    (102, "Bob", 92, 19),
    (103, "Carol", 78, 21),
    (104, "David", 88, 20)
]

highest_grade_student = max(students, key=lambda s: s[2])
print("Student with the highest grade:", highest_grade_student)

name_grade_list = [(name, grade) for (_, name, grade, _) in students]
print("Name-Grade list:", name_grade_list)

try:
    students[0][2] = 90
except TypeError as e:
    print("Error:", e)
    print("\nExplanation: Tuples are immutable, meaning their values cannot be changed after creation.\n"
          "This makes them ideal for storing fixed records like student data, ensuring data integrity.")
