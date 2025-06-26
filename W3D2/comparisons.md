# Model Comparison Summary

Below is a concise side-by-side comparison of the three fixed models on five diverse prompts. Each cell shows the first ~60 characters of the model's answer (enough to sense style and depth).

| Prompt | Base – Gemma-3-12B | Instruct – Mistral-7B-Instruct | Fine-Tuned – DeepSeek-R1-Qwen3-8B |
| --- | --- | --- | --- |
| Summarise classical vs. quantum computing | Classical computers, like the ones we use daily, store… | Classical computing uses binary digits (bits) to… | <think> First, the user asked for a summary of key diff… |
| Translate "Have a great day" | Okay, here are translations of "Have a great day" into… | Translation in Japanese: 今今日も元気でおるから… | <think> Hmm, the user wants me to translate "Have a great… |
| Second-highest salary SQL | ```sql SELECT MAX(salary) FROM Employees WHERE salary <… | SELECT MAX(salary) as max1, MAX(salary) FILTER (WHE… | <think> We are going to find the second highest salary.… |
| Explain overfitting to a 10-y-o | Okay, imagine you're studying for a spelling test… | Overfitting is when a computer program (like a robot)… | <think> Okay, the user wants me to explain overfitting… |
| Sunrise haiku | Golden light ascends, Peaks ablaze with morning hues… | The mountains' slumber ends, Dawn's light paints a new… | <think> Hmm, the user wants a haiku about a sunrise over… |

*(Full answers are in `results.json`)*

## When to use each tier

• **Base – Gemma-3-12B (LM Studio)**
  * Pros: Runs locally; cheapest; minimal RLHF makes it good for unbiased data generation.
  * Cons: Needs carefully crafted prompts; longer latency; may miss instruction nuances. (taking longer latency also caused due to local model used as base)

• **Instruct – Mistral-7B-Instruct-v0.3**
  * Pros: Strong general-purpose chat model; follows tasks cleanly with concise output; fast.
  * Cons: Not domain-specialised; sometimes short on depth.

• **Fine-tuned – DeepSeek-R1-Qwen3-8B**
  * Pros: Richer, more verbose answers with reasoning (**<think>** blocks); helpful for educational or analytical contexts.
  * Cons: Verbosity can be excessive for production; slightly higher latency; behaviour tailored to its fine-tune dataset (may stray from strict instructions).

### Practical guidance

| Scenario | Recommended tier |
| --- | --- |
| Quick Q&A, casual chat, code snippets | **Instruct** |
| Need chain-of-thought / elaborate reasoning | **Fine-tuned** |
| Bulk text generation or experimentation with prompt engineering | **Base** |

---

*Generated automatically from `results.json` using `compare_models.py`.* 