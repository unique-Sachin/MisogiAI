import pandas as pd
from itertools import combinations

# Load the answers.csv file
df = pd.read_csv('answers.csv')

pairs = []

# Group by prompt
groups = df.groupby('prompt')
for prompt, group in groups:
    # Sort answers by rank (ascending: best first)
    sorted_group = group.sort_values('rank')
    answers = sorted_group['answer'].tolist()
    ranks = sorted_group['rank'].tolist()
    # Generate all pairs (i, j) where i < j (i.e., lower rank is chosen)
    for i in range(len(answers)):
        for j in range(i+1, len(answers)):
            pairs.append({
                'chosen': answers[i],
                'rejected': answers[j]
            })

# Save to pairs.csv
pairs_df = pd.DataFrame(pairs)
pairs_df.to_csv('pairs.csv', index=False) 