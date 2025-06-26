# Task Definitions

This file documents the schema for each task JSON file.

```jsonc
{
  "problem": "<string: problem statement>",
  "answer": "<string: expected final answer>",
  "difficulty": "<string: easy | medium | hard>",
  "source": "<string: reference or URL>"
}
```

Each task set (e.g., `math_word_problems.json`) must be an array of objects following the schema above. 