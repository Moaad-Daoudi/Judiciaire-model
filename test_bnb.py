import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
print("Testing BitsAndBytesConfig...")
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
try:
    model = AutoModelForCausalLM.from_pretrained(
        "unsloth/Qwen2.5-3B-Instruct-bnb-4bit",
        quantization_config=bnb_config,
        device_map="auto"
    )
    print("Success!")
except Exception as e:
    print(e)
