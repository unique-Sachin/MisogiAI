from datasets import Dataset
from trl import RewardTrainer, RewardConfig
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

# Load pairs data for reward modeling
pairs_df = pd.read_csv("pairs.csv")
dataset = Dataset.from_pandas(pairs_df)

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Set pad_token to eos_token if not set
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1)
model.config.pad_token_id = tokenizer.pad_token_id

config = RewardConfig(
    output_dir="reward_model",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    learning_rate=5e-5,
    fp16=False,
    bf16=False,
    logging_steps=5,
    save_steps=50,
    max_steps=100
)

trainer = RewardTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    processing_class=tokenizer
)

trainer.train()
trainer.save_model("reward_model") 