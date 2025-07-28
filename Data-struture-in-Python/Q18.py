from collections import Counter, defaultdict
from pprint import pprint

# Post data (corrected structure)
posts = [
    {"id": 1, "user": "alice", "content": "Love Python programming!", "likes": 15, "tags": ["python", "coding"]},
    {"id": 2, "user": "bob", "content": "Great weather today", "likes": 8, "tags": ["weather", "life"]},
    {"id": 3, "user": "alice", "content": "Data structures are fun", "likes": 22, "tags": ["python", "learning"]},
]

# User data
users = {
    "alice": {"followers": 150, "following": 75},
    "bob": {"followers": 89, "following": 120},
}


tag_counter = Counter()
for post in posts:
    tag_counter.update(post["tags"])

print("Most Popular Tags:")
pprint(tag_counter.most_common())

user_likes = defaultdict(int)
for post in posts:
    user_likes[post["user"]] += post["likes"]

print("\nTotal Likes Per User:")
pprint(dict(user_likes))

top_posts = sorted(posts, key=lambda post: post["likes"], reverse=True)

print("\nTop Posts by Likes:")
for post in top_posts:
    print(f"Post ID: {post['id']}, User: {post['user']}, Likes: {post['likes']}")


    summary = {}
post_counts = defaultdict(int)
for post in posts:
    post_counts[post["user"]] += 1

for user, data in users.items():
    summary[user] = {
        "followers": data["followers"],
        "following": data["following"],
        "total_likes": user_likes[user],
        "post_count": post_counts[user],
    }

print("\nUser Activity Summary:")
pprint(summary)