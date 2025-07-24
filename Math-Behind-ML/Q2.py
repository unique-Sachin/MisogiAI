import random

# Number of simulations
num_trials = 10000

count_sum_7 = 0
count_sum_2 = 0
count_sum_gt_10 = 0

for _ in range(num_trials):
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    s = die1 + die2
    if s == 7:
        count_sum_7 += 1
    if s == 2:
        count_sum_2 += 1
    if s > 10:
        count_sum_gt_10 += 1

print(f"P(Sum = 7): {count_sum_7 / num_trials:.4f}")
print(f"P(Sum = 2): {count_sum_2 / num_trials:.4f}")
print(f"P(Sum > 10): {count_sum_gt_10 / num_trials:.4f}")
