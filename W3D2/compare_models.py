import argparse
import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple, List, Optional, Any

# Third-party deps – only import when needed to avoid heavy startup
try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None  # type: ignore

# Transformers is optional until we actually need local inference
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline as hf_pipeline  # type: ignore
except ImportError:  # pragma: no cover
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    hf_pipeline = None  # type: ignore

# Load .env (if present) early so env-vars are available even when not exported
try:
    from dotenv import load_dotenv  # type: ignore

    env_path = Path(__file__).with_suffix('.env') if (Path.cwd() / '.env').exists() else None
    if env_path and env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Fallback: just call load_dotenv() to read default .env in cwd if any
        load_dotenv()
except ImportError:
    # python-dotenv not installed; assume vars are exported already.
    pass


# ---------------------------------------------------------------------------
# Hard-coded lineup per user request
# ---------------------------------------------------------------------------

BASE_MODEL_ID = "google/gemma-3-12b"  # via LM Studio (OpenAI-compatible REST)
INSTRUCT_MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"  # via HF InferenceClient
FT_MODEL_ID = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"  # via HF InferenceClient

# ---------------------------------------------------------------------------

###############################################################################
# Providers helpers                                                            #
###############################################################################

def _require(pkg, name: str):
    if pkg is None:
        print(
            f"ERROR: Attempted to use {name} but the package is not installed.",
            file=sys.stderr,
        )
        sys.exit(1)


def call_openai(model_id: str, prompt: str, temperature: float = 0.7) -> Tuple[str, float]:
    _require(openai, "openai")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY env var not set.")

    base_url = os.getenv("OPENAI_BASE_URL")
    print(f"base_url: {base_url}")
    if base_url:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)  # type: ignore[attr-defined]
    else:
        client = openai.OpenAI(api_key=api_key)  # type: ignore[attr-defined]
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    latency = time.perf_counter() - start
    content = (response.choices[0].message.content or "") if response.choices else ""
    return content, latency


def call_anthropic(model_id: str, prompt: str, temperature: float = 0.7) -> Tuple[str, float]:
    _require(anthropic, "anthropic")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY env var not set.")

    client = anthropic.Anthropic(api_key=api_key)  # type: ignore[attr-defined]
    start = time.perf_counter()
    response = client.messages.create(
        model=model_id,
        max_tokens=1024,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    latency = time.perf_counter() - start
    content = response.content[0].text if response.content else ""  # type: ignore[attr-defined]
    return content, latency


# ---------------- Hugging Face InferenceClient (Novita) --------------------
try:
    from huggingface_hub import InferenceClient  # type: ignore
except ImportError:  # pragma: no cover
    InferenceClient = None  # type: ignore


def call_hf_novita(model_id: str, prompt: str, temperature: float = 0.7) -> Tuple[str, float]:
    _require(InferenceClient, "huggingface_hub")

    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN env var not set.")

    client = InferenceClient(provider="novita", api_key=token)  # type: ignore
    start = time.perf_counter()
    completion = client.chat.completions.create(  # type: ignore[attr-defined]
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    latency = time.perf_counter() - start
    content = str(completion.choices[0].message.content)  # type: ignore[attr-defined]
    return content, latency


###############################################################################
# Local HF models                                                              #
###############################################################################

@lru_cache(maxsize=8)
def _load_local_pipeline(model_id: str, device: str = "cpu"):
    _require(hf_pipeline, "transformers")
    print(f"Loading local model '{model_id}'…", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(model_id)  # type: ignore
    model = AutoModelForCausalLM.from_pretrained(model_id)  # type: ignore
    gen_pipe = hf_pipeline(
        "text-generation",
        model=model,
        tokenizer=tok,
        device=device,
        max_new_tokens=512,
    )  # type: ignore[call-arg]
    return gen_pipe


def call_local(model_id: str, prompt: str, temperature: float = 0.7, device: str = "cpu") -> Tuple[str, float]:
    gen_pipe = _load_local_pipeline(model_id, device)
    start = time.perf_counter()
    outputs = gen_pipe(prompt, do_sample=True, temperature=temperature, num_return_sequences=1)  # type: ignore
    latency = time.perf_counter() - start
    text = outputs[0].get("generated_text", "") if isinstance(outputs, list) else str(outputs)
    return text, latency


###############################################################################
# Main comparison logic                                                        #
###############################################################################

def run_comparison(prompt: str, temperature: float = 0.7):
    results = {}

    # BASE model via LM Studio (OpenAI API)
    print(f"\n=== Running BASE model [gemma-3-12b via LM Studio] ===")
    try:
        base_resp, base_lat = call_openai(BASE_MODEL_ID, prompt, temperature)
    except Exception as exc:
        base_resp, base_lat = f"ERROR: {exc}", None
    results["base"] = {
        "model": BASE_MODEL_ID,
        "latency_sec": base_lat,
        "response": base_resp,
    }
    print(base_resp)
    if base_lat is not None:
        print(f"--- Latency: {base_lat:.2f}s\n")

    # INSTRUCT model via HF InferenceClient
    print(f"\n=== Running INSTRUCT model [{INSTRUCT_MODEL_ID}] ===")
    try:
        instruct_resp, instruct_lat = call_hf_novita(INSTRUCT_MODEL_ID, prompt, temperature)
    except Exception as exc:
        instruct_resp, instruct_lat = f"ERROR: {exc}", None
    results["instruct"] = {
        "model": INSTRUCT_MODEL_ID,
        "latency_sec": instruct_lat,
        "response": instruct_resp,
    }
    print(instruct_resp)
    if instruct_lat is not None:
        print(f"--- Latency: {instruct_lat:.2f}s\n")

    # Fine-tuned model via HF InferenceClient
    print(f"\n=== Running FINE-TUNED model [{FT_MODEL_ID}] ===")
    try:
        ft_resp, ft_lat = call_hf_novita(FT_MODEL_ID, prompt, temperature)
    except Exception as exc:
        ft_resp, ft_lat = f"ERROR: {exc}", None
    results["ft"] = {
        "model": FT_MODEL_ID,
        "latency_sec": ft_lat,
        "response": ft_resp,
    }
    print(ft_resp)
    if ft_lat is not None:
        print(f"--- Latency: {ft_lat:.2f}s\n")

    # JSON Summary
    print("\n=== SUMMARY (JSON) ===")
    print(json.dumps(results, indent=2))

    return results


###############################################################################
# CLI                                                                         #
###############################################################################

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compare Base / Instruct / Fine-tuned models across providers.",
    )
    p_group = p.add_mutually_exclusive_group(required=True)
    p_group.add_argument("--prompt", help="Prompt to send to the models.")
    p_group.add_argument("--prompt-file", help="Path to JSON file containing a list of prompts.")

    p.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (0-2).",
    )
    p.add_argument("--output-file", help="Write all results to given JSON file.")
    return p


def main(argv: Optional[List[str]] = None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.prompt_file:
        import json, pathlib
        path = pathlib.Path(args.prompt_file)
        if not path.exists():
            print(f"Prompt file '{path}' not found.", file=sys.stderr)
            sys.exit(1)
        prompts = json.loads(path.read_text())
        if not isinstance(prompts, list):
            print("Prompt file must contain a JSON array of strings.", file=sys.stderr)
            sys.exit(1)
        aggregated = {}
        for idx, prm in enumerate(prompts, 1):
            print(f"\n########## PROMPT {idx} ##########\n{prm}\n")
            res = run_comparison(prompt=prm, temperature=args.temperature)
            aggregated[prm] = res
        print("\n========= ALL RESULTS =========")
        print(json.dumps(aggregated, indent=2))
        results_data = aggregated
    else:
        results_data = run_comparison(prompt=args.prompt, temperature=args.temperature)

    if args.output_file:
        import pathlib, json as _json
        path_out = pathlib.Path(args.output_file)
        path_out.write_text(_json.dumps(results_data, indent=2))
        print(f"\nSaved results to {path_out.resolve()}")


if __name__ == "__main__":
    main() 