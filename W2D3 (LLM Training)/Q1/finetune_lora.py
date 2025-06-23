import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.training_args import TrainingArguments
from transformers.trainer import Trainer
from transformers.data.data_collator import DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType

# Load dataset (assuming .txt file with <|user|> and <|assistant|> tokens)
def load_sft_dataset(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return [{"text": line.strip()} for line in lines if line.strip()]

def tokenize(example, tokenizer):
    return tokenizer(example["text"], truncation=True, max_length=1024)

model_name = "EleutherAI/pythia-2.8b"  # or another small model
dataset_path = "sft_dataset.txt"

tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

raw_dataset = load_sft_dataset(dataset_path)
tokenized_dataset = [tokenize(ex, tokenizer) for ex in raw_dataset]

class SFTDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        return {k: torch.tensor(v) for k, v in self.data[idx].items()}

train_dataset = SFTDataset(tokenized_dataset)

model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=[
        "attention.query_key_value",
        "attention.dense",
        "mlp.dense_h_to_4h",
        "mlp.dense_4h_to_h"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)

training_args = TrainingArguments(
    output_dir="./lora-pythia-2.8b-sft",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    learning_rate=5e-5,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    report_to="none"
)

data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained("./lora-pythia-2.8b-sft")
tokenizer.save_pretrained("./lora-pythia-2.8b-sft") 