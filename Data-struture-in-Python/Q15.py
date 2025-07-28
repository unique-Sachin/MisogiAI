# Data
students = ["Alice", "Bob", "Carol", "David", "Eve"]
scores = [185, 92, 78, 88, 95]

# 1. Create a Numbered List of Students
print("Numbered List of Students:")
for i, student in enumerate(students, start=1):
    print(f"{i}. {student}")
print()

# 2. Pair Students with Their Scores Using enumerate()
print("Students and Their Scores:")
for i, (student, score) in enumerate(zip(students, scores)):
    print(f"{i}. {student} - {score}")
print()

# 3. Find Positions of High Scorers (score > 90)
print("Positions of Students Who Scored Above 90:")
high_scorers_indices = [i for i, score in enumerate(scores) if score > 90]
print(high_scorers_indices)
print()

# 4. Map Positions to Student Names
print("Position to Student Name Mapping:")
position_to_student = {i: name for i, name in enumerate(students)}
print(position_to_student)