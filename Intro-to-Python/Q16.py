def checkValidAge():
    try:
        age = input("Enter you age (1-129):")
        if age.isalpha():
            raise ValueError("Please input a valid number")
        age = int(age)
        if age<1 or age>120:
            raise ValueError("Out of range. Enter number 1-120")
        print(f"You enterd a valid age {age}")
        return
    except Exception as e:
        print(e)
        checkValidAge()
    

checkValidAge()