# Hallucination Log

Document examples where the tutor produced incorrect or hallucinated information.

| Timestamp | Prompt Type | Question | Model Answer | Correct Answer | Notes |
|-----------|------------|----------|--------------|----------------|-------|
| 2025-06-25 | zero-shot | If a fair coin is tossed twice, what is the probability of getting exactly one head? | Explained correctly (0.5 as 1/2) but did **not** include the numeric string "0.5" → automatic checker marked it wrong | 0.5 | Formatting mismatch; model gave fraction instead of decimal.
| 2025-06-25 | few-shot | What is the area of a circle with radius 5 cm? (Use π = 3.14) | Long, unfinished explanation—never delivered the final numeric area | 78.5 | Truncated response; model stopped before answer.
| 2025-06-25 | meta | Solve for x: 2x + 3 = 11. | Chose zero-shot strategy internally but response cut off mid-solution; final answer missing "x = 4" | x = 4 | Response truncated—likely token limit or early stop.
| 2025-06-25 | zero-shot | What is 35% of 160? | Response stopped mid-explanation, never stated final answer 56 | 56 | Truncated; no final answer provided.
| 2025-06-25 | zero-shot (phi-4) | What is 3/4 + 1/8? | Response string was empty | 7/8 | Complete failure; produced no answer.
| 2025-06-25 | zero-shot (phi-4) | What is 25% of 80? | Long internal planning text; never formatted final steps/answer | 20 | Chain-of-thought leak & missing answer.
| 2025-06-25 | cot (phi-4) | What is 25% of 80? | Repeated instruction loop; no cleaned explanation or answer | 20 | Failed to strip internal reasoning, violated format.
