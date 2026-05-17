import os

cache_path = os.path.join(os.getcwd(), "models", ".cache")
os.environ['HF_HOME'] = cache_path

os.makedirs(cache_path, exist_ok=True)
os.makedirs("./models/base", exist_ok=True)
os.makedirs("./models/lora", exist_ok=True)

from huggingface_hub import snapshot_download

print(f"Using cache directory: {cache_path}")

print("Downloading Base Model (Qwen2.5-3B)...")
snapshot_download(repo_id="Qwen/Qwen2.5-3B", local_dir="./models/base", token=False)

print("Downloading LoRA Adapter (brahX/Qwen2.5-3B-lora)...")
snapshot_download(repo_id="brahX/Qwen2.5-3B-lora", local_dir="./models/lora", token=False)

print("\n✅ Success! All files are now in your local 'models/' folder.")
print("You can now run your RAG pipeline without any internet/permission issues.")