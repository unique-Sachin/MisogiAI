# Visitor sets (corrected)
monday_visitors = {"user1", "user2", "user3", "user4", "user5"}
tuesday_visitors = {"user2", "user4", "user6", "user7"}
wednesday_visitors = {"user1", "user3", "user6", "user9", "user10"}

# 1. Unique Visitors Across All Days
unique_visitors = monday_visitors | tuesday_visitors | wednesday_visitors
print(f"Total unique visitors: {len(unique_visitors)}")

# 2. Returning Visitors on Tuesday
returning_tuesday = monday_visitors & tuesday_visitors
print(f"Returning visitors on Tuesday: {returning_tuesday}")

# 3. New Visitors Each Day
new_monday = monday_visitors  # All are new on Monday
new_tuesday = tuesday_visitors - monday_visitors
new_wednesday = wednesday_visitors - (monday_visitors | tuesday_visitors)
print(f"New visitors on Monday: {new_monday}")
print(f"New visitors on Tuesday: {new_tuesday}")
print(f"New visitors on Wednesday: {new_wednesday}")

# 4. Loyal Visitors (all three days)
loyal_visitors = monday_visitors & tuesday_visitors & wednesday_visitors
print(f"Loyal visitors (all three days): {loyal_visitors}")

# 5. Daily Visitor Overlap Analysis
print(f"Monday-Tuesday overlap: {monday_visitors & tuesday_visitors}")
print(f"Tuesday-Wednesday overlap: {tuesday_visitors & wednesday_visitors}")
print(f"Monday-Wednesday overlap: {monday_visitors & wednesday_visitors}")
