import random

def analyze_numbers(nums: list[int]) -> dict:
    if len(nums) ==0 or str in nums:
        raise ValueError("Empty List")
    
    mean = sum(nums)/len(nums)
    median = sorted(nums)[len(nums)//2]
    numsObj = {}
    for i in nums:
        if i not in numsObj:
            numsObj[i] = 1
        else:
            numsObj[i] +=1
    count = 0
    mode = None
    for k in numsObj:
        if numsObj[k]>count:
            count = numsObj[k]
            mode = k


    return {"mean": mean, "median": median, "mode": mode}

nums = [random.randint(0,100) for _ in range(10)]

print(analyze_numbers(nums))