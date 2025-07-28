grades = [85, 92, 78, 90, 88, 76, 94, 89, 87, 91]

slicedGrade = grades[2:7]

# print(slicedGrade)

listComprehension = [x for x in grades if x>85]
# print(listComprehension)

grades[3] = 95

grades.extend([33,55,65])
# print(grades)

grades.sort(reverse=True)
print(grades[:5])