# EdTech Math Tutor LLM Agent

A command-line tutoring assistant that leverages `deepseek/deepseek-r1-0528-qwen3-8b` (served locally via LM Studio) to provide step-by-step help with mathematics for students in grades 6-10.

---

## Quick start

```bash
# 1 — create & activate a virtual-env (Python 3.8+)
python -m venv .venv
source .venv/bin/activate

# 2 — install dependencies
pip install -r requirements.txt

# 3 — start LM Studio and load the model "deepseek/deepseek-r1-0528-qwen3-8b"
#    Ensure the OpenAI-compatible server is running (e.g. http://localhost:1234/v1)

# 4 — run the tutor
python -m src.main --prompt_type zero-shot --question "What is 35% of 160?"
```

---

## Repository layout

```
├── README.md               ← you are here
├── domain_analysis.md      ← problem & requirement notes
├── prompts/                ← prompt templates
│   ├── zero_shot.txt
│   ├── few_shot.txt
│   ├── cot_prompt.txt
│   └── meta_prompt.txt
├── evaluation/             ← test inputs & automated results
│   ├── input_queries.json
│   ├── output_logs.json
│   └── analysis_report.md
├── src/                    ← application code
│   ├── main.py
│   └── utils.py
├── hallucination_log.md    ← examples of failure cases
└── requirements.txt
```

---

## Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LM_STUDIO_BASE_URL` | Base URL of the LM Studio OpenAI-compatible endpoint | `http://localhost:1234/v1` |
| `LM_MODEL_NAME` | Model name to query | `deepseek/deepseek-r1-0528-qwen3-8b` |

The OpenAI client does not require an API key when connecting to LM Studio, but some versions insist on one being set. If that is the case, set `OPENAI_API_KEY` to any dummy string.

---

## Development tasks

1. Phase 1 – core structure & CLI integration (current).
2. Phase 2 – design and evaluate prompt strategies.
3. Phase 3 – collect metrics and document findings.

Refer to `domain_analysis.md` and the `/prompts` directory for implementation guidelines. 