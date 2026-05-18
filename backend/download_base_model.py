import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. Define where you want the files to go
save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "base")
os.makedirs(save_path, exist_ok=True)

# 2. Define the model
model_id = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"

print(f"Downloading base model to: {save_path}")
print("This will take a few minutes...")

# 3. Download and Save
# This will pull from HuggingFace and save permanently to your local folder
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print("✅ Base model saved locally!")