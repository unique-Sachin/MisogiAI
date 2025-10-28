students = [
    {"name": "Alice", "marks": [80, 75, 90]},
    {"name": "Bob", "marks": [70, 60, 65]},
    {"name": "Charlie", "marks": [95, 85, 100]},
    {"name": "David", "marks": [60, 70, 80]}
]

ans = {
    "A":set(),
    "B":set(),
    "C":set()
}

for k in students:
    marks = k['marks']
    avg = round(sum(marks)/len(marks))
    if avg>85 or avg ==85:
        ans["A"].add(k['name'])
    elif avg>70 or avg ==70 and avg < 85:
        ans["B"].add(k['name'])
    else:
        ans["C"].add(k['name'])

print(ans)