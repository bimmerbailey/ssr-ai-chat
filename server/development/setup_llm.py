import os

from huggingface_hub import hf_hub_download, snapshot_download

from app.config.settings import app_settings
from app.paths import models_cache_path, models_path

os.makedirs(models_path, exist_ok=True)
embedding_path = models_path / "embedding"

if not os.path.exists(embedding_path):
    print(f"Downloading embedding {app_settings.embedding_hf_model_name}")
    snapshot_download(
        repo_id=app_settings.embedding_hf_model_name,
        cache_dir=models_cache_path,
        local_dir=embedding_path,
    )
    print("Embedding model downloaded!")
    print("Downloading models for local execution...")

if not os.path.exists(f"{models_path}/{app_settings.llm_hf_model_file}"):
    # Download LLM and create a symlink to the model file
    hf_hub_download(
        repo_id=app_settings.llm_hf_repo_id,
        filename=app_settings.llm_hf_model_file,
        cache_dir=models_cache_path,
        local_dir=models_path,
    )
    print("LLM model downloaded!")
    print("Setup done")
