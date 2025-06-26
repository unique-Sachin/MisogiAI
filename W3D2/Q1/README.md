# Model Comparison CLI

Evaluate three pre-selected model tiers (Base, Instruct, Fine-tuned) with a single command-line tool.

| Tier | Model | Served via |
|------|-----------------------------|------------------------------|
| Base | `google/gemma-3-12b`        | LM Studio (OpenAI-compatible REST) |
| Instruct | `mistralai/Mistral-7B-Instruct-v0.3` | Hugging Face `InferenceClient` (provider = novita) |
| Fine-tuned | `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` | Hugging Face `InferenceClient` (novita) |

---

## Quick start

```bash
# install deps
pip install -r requirements.txt

# single prompt
python compare_models.py --prompt "Explain quantum teleportation in one sentence."

# list of prompts (see input.json) and save everything to results.json
python compare_models.py \
  --prompt-file input.json \
  --output-file results.json
```

After each prompt the script prints the three model outputs + timing and finally emits a JSON blob. If `--output-file` is provided the JSON is written to disk.

`comparisons.md` shows a human-friendly summary table; update it by re-running the script then regenerating the markdown (or edit manually).

---

## Environment variables

Put these in a `.env` file (automatically loaded) or export them:

```env
# LM Studio / OpenAI-compatible endpoint for Gemma
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio   # any non-empty string

# Hugging Face Novita token for Mistral + DeepSeek
HF_TOKEN=hf_your_access_token
```

---

## Notes

* Gemma runs locally in LM Studio; latency depends on your hardware.
* Instruct and Fine-tuned models are hosted via Hugging Face Inference API and require a valid token.
* `results.json` structure uses the prompt text as the top-level key.
* The Base model may exhibit longer latency because it is served locally; see `comparisons.md` for additional commentary.

```bash
pip install -r requirements.txt

# Basic usage – run default line-up
python compare_models.py --prompt "Explain quantum teleportation at a high-school level."

# Pick your own models
python compare_models.py \
  --prompt "Write an SQL query that lists the top 10 products by revenue." \
  --base-model "openai:davinci-002" \
  --instruct-model "anthropic:claude-3-sonnet-20240229" \
  --ft-model "hf:HuggingFaceH4/zephyr-7b-beta" 
```

Environment variables required for hosted providers (and LM Studio):

* `OPENAI_API_KEY` – OpenAI secret key (set to any value for LM Studio, e.g. `lm-studio`)
* `ANTHROPIC_API_KEY` – Anthropic secret key
* `OPENAI_BASE_URL` – Optional. Point this to a custom OpenAI-compatible endpoint such as `http://localhost:1234/v1` when using LM Studio.

Local models are downloaded from the Hugging Face Hub (or can be provided as a local folder/path). They run on CPU by default; pass `--device cuda` to run on GPU (CUDA) or `--device mps` for Apple Silicon.

Outputs
-------
For each tier the tool prints:

* The raw text response
* Latency in seconds

At the end a JSON summary is emitted – perfect for piping into other scripts.

```json
{
  "base": {
    "provider": "hf",
    "model": "meta-llama/Llama-2-7b-hf",
    "latency_sec": 12.3,
    "response": "…"
  },
  "instruct": { … },
  "ft": { … }
}
```

Feel free to swap models, adjust sampling parameters, or extend the script (e.g. add token usage / cost estimates).

Running a local LM Studio model (e.g. `microsoft/phi-4-reasoning-plus`)
-------------------------------------------------------------

1. In LM Studio, start the model and copy the local server URL (default `http://localhost:1234`).
2. Export environment vars so the OpenAI SDK speaks to that endpoint:

```bash
export OPENAI_BASE_URL="http://localhost:1234/v1"
export OPENAI_API_KEY="lm-studio"  # any non-empty string
```

3. Invoke the CLI referencing the model name exactly as shown in LM Studio:

```bash
python compare_models.py --base-model "openai:microsoft/phi-4-reasoning-plus" --prompt "Hello!"
```

Because LM Studio mimics the OpenAI Chat Completions API, no other code changes are needed. 