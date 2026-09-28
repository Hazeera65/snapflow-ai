#!/usr/bin/env python3
"""
Download AI models for SnapFlow AI

Downloads ~3-4 GB of models for:
- Embeddings (Nomic Embed Text)
- LLM (Mistral 7B)
- OCR (PaddleOCR)
- Speech (Faster Whisper)

Run: python scripts/download_models.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import AutoTokenizer, AutoModel
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Model definitions
MODELS = [
    {
        "name": "Nomic Embed Text",
        "model_id": "nomic-ai/nomic-embed-text-v1.5",
        "local_name": "nomic-embed-text",
        "size_mb": 30,
        "task": "embeddings"
    },
    {
        "name": "Mistral 7B Instruct",
        "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
        "local_name": "mistral-7b-instruct",
        "size_mb": 14500,
        "task": "llm",
        "note": "Large model, will take time to download"
    },
    {
        "name": "PaddleOCR",
        "model_id": "paddleocr",
        "local_name": "paddleocr",
        "size_mb": 200,
        "task": "ocr",
        "skip": True,
        "note": "Installed via paddleocr package"
    },
    {
        "name": "Faster Whisper (base)",
        "model_id": "openai/whisper-base",
        "local_name": "faster-whisper-base",
        "size_mb": 140,
        "task": "speech",
        "skip": True,
        "note": "Installed via faster-whisper package"
    }
]

def download_model(model_config):
    """Download a single model"""
    
    if model_config.get("skip"):
        logger.info(f"⊘ {model_config['name']} ({model_config.get('note', '')})")
        return True
    
    model_id = model_config["model_id"]
    local_name = model_config["local_name"]
    local_path = MODELS_DIR / local_name
    
    logger.info(f"")
    logger.info(f"{'='*60}")
    logger.info(f"Downloading: {model_config['name']}")
    logger.info(f"Model ID: {model_id}")
    logger.info(f"Size: ~{model_config['size_mb']} MB")
    logger.info(f"Location: {local_path}")
    logger.info(f"{'='*60}")
    
    try:
        if local_path.exists():
            logger.info(f"✓ {local_name} already exists")
            return True
        
        # Download tokenizer and model
        logger.info(f"Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        
        logger.info(f"Downloading model (this may take several minutes)...")
        model = AutoModel.from_pretrained(
            model_id,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        # Save to local path
        logger.info(f"Saving to {local_path}...")
        local_path.mkdir(parents=True, exist_ok=True)
        
        tokenizer.save_pretrained(str(local_path))
        model.save_pretrained(str(local_path))
        
        logger.info(f"✓ {model_config['name']} downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to download {model_config['name']}: {e}")
        return False


def main():
    """Download all models"""
    
    print()
    print("="*60)
    print("SnapFlow AI - Model Download")
    print("="*60)
    print()
    print(f"Models directory: {MODELS_DIR}")
    print()
    
    total_size = sum(m.get("size_mb", 0) for m in MODELS if not m.get("skip"))
    print(f"Total download size: ~{total_size} MB (~{total_size/1024:.1f} GB)")
    print()
    print("WARNING: This will take significant time and bandwidth.")
    print("Models are stored locally and not uploaded to cloud.")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("Cancelled.")
        return
    
    print()
    
    successful = 0
    failed = 0
    
    for model_config in MODELS:
        try:
            if download_model(model_config):
                successful += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            logger.warning("Download interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error downloading {model_config['name']}: {e}")
            failed += 1
    
    print()
    print("="*60)
    print("Download Summary")
    print("="*60)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print()
    
    if failed == 0:
        print("✓ All models downloaded successfully!")
        print()
        print("You can now start SnapFlow AI with:")
        print("  .\run.ps1")
    else:
        print("✗ Some models failed to download.")
        print("Check error messages above and retry.")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Download cancelled.")
        sys.exit(1)
