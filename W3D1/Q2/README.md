# Advanced Prompt Engineering Pipeline

This repository implements a **Tree-of-Thought (ToT)** reasoning engine, a **Self-Consistency** aggregator, and an **OPRO-style Prompt Optimizer** for solving structured reasoning tasks with Large Language Models (LLMs).

## Project Goals
1. Enable deliberate multi-step reasoning with look-ahead and back-tracking (ToT).
2. Improve answer reliability by sampling multiple diverse reasoning paths (Self-Consistency).
3. Automatically evolve prompts based on failure analysis and metric feedback (Prompt Optimizer).
4. Provide reproducible evaluation with quantifiable metrics.

## Directory Layout
```
├── README.md                   # Setup & usage instructions
├── requirements.txt            # Python dependencies
├── tasks/                      # Problem definitions + solutions
│   ├── math_word_problems.json
│   ├── logic_puzzles.json
│   ├── code_debugging.json
│   └── task_definitions.md
├── prompts/                    # Prompt templates (base + optimized)
│   ├── base_prompts/
│   │   ├── tot_system_prompt.txt
│   │   ├── self_consistency_prompt.txt
│   │   └── evaluation_prompt.txt
│   ├── optimized_prompts/      # Versioned prompt files
│   └── meta_optimizer_prompt.txt
├── src/                        # Pipeline code
│   ├── main.py
│   ├── tot_engine.py
│   ├── self_consistency.py
│   ├── prompt_optimizer.py
│   └── utils.py
├── logs/                       # Auto-generated logs (ignored by git)
│   ├── reasoning_trees/
│   ├── optimization_history/
│   └── performance_logs/
└── evaluation/                 # Evaluation outputs & analysis
    ├── test_results.json
    ├── metrics_analysis.py
    └── reflection_report.md
```

## Quickstart
1. **Install dependencies**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Set environment variables** (e.g., `OPENAI_API_KEY`) in a `.env` file or exported in your shell.
3. **Run the pipeline**
   ```bash
   python -m src.main --task_file tasks/math_word_problems.json
   ```

## Key Components
| Module | Purpose |
| ------ | ------- |
| `ToTEngine` | Maintains a tree of thoughts, performs breadth/depth search, and prunes low-quality branches. |
| `SelfConsistency` | Samples multiple reasoning paths, aggregates answers via majority vote, and calculates consistency. |
| `PromptOptimizer` | Detects failure patterns, auto-generates improved prompts, and versions them for tracking. |

## Evaluation Metrics
* **Task Accuracy**
* **Reasoning Coherence** (1-5 rubric)
* **Hallucination Rate**
* **Consistency Score**
* **Optimization Improvement**

## References
* Yao et al. (2023) "Tree of Thoughts: Deliberate Problem Solving with Large Language Models".
* Wang et al. (2022) "Self-Consistency Improves Chain of Thought Reasoning in Language Models".

---
Feel free to open issues or PRs for enhancements! 