from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.pipelines import pipeline
import pandas as pd

model_name = "gpt2"  # You can change this to another base model if desired
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

prompts = [
    "Tell me a joke about cats.",
    "Summarize the plot of Romeo and Juliet.",
    "Write a short essay on the importance of exercise.",
    "Describe a sunset in one sentence.",
    "Give advice for someone starting a new job."
]

all_results = []
for prompt in prompts:
    outputs = generator(
        prompt,
        num_return_sequences=4,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        max_new_tokens=60,
        return_full_text=False
    )
    if isinstance(outputs, list):
        for i, out in enumerate(outputs):
            print(f"Prompt: {prompt}\nCandidate {i+1}: {out['generated_text']}\n")
            all_results.append({"prompt": prompt, "answer": out["generated_text"]})
    else:
        print(f"Warning: No outputs for prompt: {prompt}")

# Save to CSV for manual ranking
df = pd.DataFrame(all_results)
df["rank"] = ""  # To be filled manually
df.to_csv("answers.csv", index=False) 