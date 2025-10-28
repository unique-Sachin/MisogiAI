# Write a one-line Python expression (no loops) that generates a list of all integers between 1 and 1000 that are:
# divisible by 7 or 9, but not both
# and are palindromic numbers (e.g., 121)

def checkPalNum(num):
    a = num
    b = 0
    while(a>0):
        b = b*10 + a%10
        a = a//10
    return num==b


integers = [x for x in range(1000) if x%7==0 or x%9==0 if not x%7==0 and x%9==0 if checkPalNum(x)]
print(integers)