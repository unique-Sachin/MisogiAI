# Corrected nested dictionary
school = {
    "Math": {
        "teacher": "Mr. Smith",
        "students": [("Alice", 85), ("Bob", 92), ("Carol", 78)]
    },
    "Science": {
        "teacher": "Ms. Johnson",
        "students": [("David", 88), ("Eve", 94), ("Frank", 82)]
    }
}

# 1. Print Teacher Names
print("Teacher names:")
for class_name, class_info in school.items():
    print(f"{class_name}: {class_info['teacher']}")
print()

# 2. Calculate Class Average Grades
print("Class average grades:")
for class_name, class_info in school.items():
    students = class_info["students"]
    grades = [grade for _, grade in students]  # tuple unpacking
    avg = sum(grades) / len(grades)
    print(f"{class_name}: {avg:.2f}")
print()

# 3. Find Top Student Across All Classes
all_students = []
for class_info in school.values():
    all_students.extend(class_info["students"])

top_student = max(all_students, key=lambda s: s[1])  # s is (name, grade)
print(f"Top student across all classes: {top_student[0]} with grade {top_student[1]}")
