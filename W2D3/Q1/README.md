# LLM Fine-Tuning Evaluation

This project demonstrates how to evaluate the responses of a base language model and a fine-tuned model on a set of prompts. The results are saved in a Markdown file for easy comparison.

## Files

- `evaluate_sft.py`: Script to generate and compare responses from the base and fine-tuned models.
- `finetune_lora.py`: Script for fine-tuning a model using LoRA (Low-Rank Adaptation).
- `sft_dataset.txt`: Dataset used for supervised fine-tuning.
- `before_after.md`: Output file containing the prompts and responses from both models.

## Requirements

- Python 3.8+
- [transformers](https://huggingface.co/docs/transformers/index) library

Install dependencies with:

```bash
pip install transformers
```

## Usage

1. **Fine-tune the model (optional):**
   - Use `finetune_lora.py` to fine-tune your base model with your dataset.
   - The fine-tuned model should be saved in a directory (e.g., `./lora-pythia-2.8b-sft`).

2. **Run the evaluation script:**
   - Execute the following command:

   ```bash
   python evaluate_sft.py
   ```

3. **View results:**
   - The script will print responses to the console and save them in `before_after.md` for comparison.

## Customization

- Edit the `prompts` list in `evaluate_sft.py` to test different questions.
- Change the model paths in the script to use different base or fine-tuned models.

## License

This project is for educational purposes. 