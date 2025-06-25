# EdTech Math Tutor LLM Agent

A CLI-based tutoring assistant that uses `deepseek/deepseek-r1-0528-qwen3-8b` (served locally via LM Studio) to provide step-by-step math help for grades 6-10.

---
## Project status
* **Phase 1 – Core structure & CLI** ✅  
* **Phase 2 – Prompt engineering + automated evaluation** ✅  
* **Phase 3 – Analysis & hallucination tracking** ✅

---
## Quick start
```bash
# 1 – set up Python 3.8+ virtual-env
python -m venv .venv && source .venv/bin/activate

# 2 – install dependencies
pip install -r requirements.txt

# 3 – launch LM Studio and load the model "deepseek/deepseek-r1-0528-qwen3-8b"
#     (Start the OpenAI-compatible server, e.g. http://localhost:1234/v1)

# 4 – ask a single question
python -m src.main --prompt_type zero-shot --question "What is 35% of 160?"
```

---
## Evaluation workflow
```bash
# Generate model outputs for the test set (writes eval_results_*.json & output_logs.json)
python -m src.evaluator --input evaluation/input_queries.json

# Aggregate all previous runs, compute significance tests, update analysis_report.md
python -m src.analyzer --results_dir evaluation
```

Artifacts:
* `evaluation/output_logs.json` – rolling log of every model interaction.  
* `evaluation/eval_results_<timestamp>.json` – immutable snapshot of each evaluation run.  
* `evaluation/analysis_report.md` – human-readable summaries & statistical tables.

---
## Hallucination tracking
Examples of failure or truncation are documented in `hallucination_log.md`.  Please add new cases whenever the model:
1. Gives mathematically incorrect results.  
2. Fails to follow format instructions.  
3. Hallucinates unsupported concepts.

---
## Useful environment variables
| Variable              | Purpose                                                      | Default                      |
|-----------------------|--------------------------------------------------------------|------------------------------|
| `LM_STUDIO_BASE_URL`  | Base URL of LM Studio's OpenAI-compatible endpoint           | `http://localhost:1234/v1`   |
| `LM_MODEL_NAME`       | Model name to query                                          | `deepseek/deepseek-r1-0528-qwen3-8b` |
| `OPENAI_API_KEY`      | Dummy string if OpenAI SDK insists on an API key             | `dummy`                      |

---
## Directory layout
```
├── README.md              ← you are here
├── requirements.txt       ← Python deps (incl. scipy for Phase 3 stats)
├── domain_analysis.md     ← problem decomposition & user personas
├── prompts/               ← 4 prompt templates (zero, few, cot, meta)
├── evaluation/            ← test queries, run logs, analysis outputs
│   ├── input_queries.json
│   ├── output_logs.json
│   └── analysis_report.md
├── hallucination_log.md   ← catalogue of failure cases
└── src/                   ← application code
    ├── main.py            ← CLI entry-point
    ├── utils.py           ← helpers for prompts, API calls, logging
    ├── evaluator.py       ← automated prompt-type evaluation
    └── analyzer.py        ← aggregate stats & significance tests
```

---
## Next milestones
* Expand `input_queries.json` (≥50 questions across all topics).
* Add `tests/` suite with `pytest` for utility functions.
* Implement ambiguity-detection fallback ("Could you clarify…?").
* Generate visual plots of accuracy trends. 