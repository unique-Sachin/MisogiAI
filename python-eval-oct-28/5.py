import json

file = "sales.json"

openedFile = open(file).read()

parsed = json.loads(openedFile)

ansDict = {}

for i in parsed:
    ansDict[i["item"]] =  i["price"] * i["qty"]


with open("report.txt",'w') as file:
    file.write(json.dumps(ansDict))