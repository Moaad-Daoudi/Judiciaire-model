from huggingface_hub import HfApi
import os

TOKEN = os.getenv("HK_TOKEN")

# Config
REPO_ID = "moaaddaoudi/judiciaire-model"
LOCAL_FOLDER = "./atlas-deploy"         

api = HfApi()

print("Uploading deployment folder to Hugging Face Space...")
api.upload_folder(
    folder_path=LOCAL_FOLDER,
    repo_id=REPO_ID,
    repo_type="space",
    token=TOKEN
)
print("Upload complete! Go to your Hugging Face Space to see the build progress.")