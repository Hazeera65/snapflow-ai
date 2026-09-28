"""
Model Registry for SnapFlow AI

Central registry for all AI models used in the application.
Enables easy swapping of models without changing application code.
"""

import logging
import json
from dataclasses import dataclass, asdict
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a single model"""
    model_id: str
    name: str
    task: str  # "embedding", "llm", "ocr", "speech", "vision"
    source: str  # "huggingface", "qualcomm_ai_hub", "onnx_model", "local"
    local_path: Optional[str]  # Path to downloaded model
    size_mb: Optional[float]
    
    # Runtime support
    supported_runtimes: List[str]  # ["onnx", "transformers", "ollama"]
    precision: str  # "fp32", "fp16", "int8", "int4"
    
    # Specs
    input_shape: Optional[Dict]
    output_shape: Optional[Dict]
    
    # Performance
    typical_latency_ms: Optional[float]  # CPU baseline
    preferred_accelerator: str  # "NPU", "GPU", "CPU"
    fallback_backend: str  # "CPU"
    
    # Metadata
    description: str
    qualcomm_ai_hub: bool  # Whether available on Qualcomm AI Hub
    ai_hub_model_id: Optional[str]  # Qualcomm AI Hub model ID if available
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class ModelRegistry:
    """Central registry for AI models"""
    
    def __init__(self, models_dir: Path = None):
        self.models_dir = models_dir or Path(__file__).parent.parent / "models"
        self.models_dir.mkdir(exist_ok=True)
        self._models: Dict[str, ModelConfig] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize default model registry"""
        
        # Embedding Model - Nomic Embed Text
        self._models["embeddings_nomic"] = ModelConfig(
            model_id="embeddings_nomic",
            name="Nomic Embed Text",
            task="embedding",
            source="huggingface",
            local_path=str(self.models_dir / "nomic-embed-text"),
            size_mb=30,
            supported_runtimes=["onnx", "transformers"],
            precision="fp32",
            input_shape={"type": "text", "max_length": 512},
            output_shape={"type": "float32", "dimensions": 384},
            typical_latency_ms=50,
            preferred_accelerator="NPU",
            fallback_backend="CPU",
            description="Lightweight embedding model, 384-dimensional vectors, optimized for retrieval",
            qualcomm_ai_hub=False,
            ai_hub_model_id=None
        )
        
        # LLM Model - Mistral 7B Instruct
        self._models["llm_mistral_7b"] = ModelConfig(
            model_id="llm_mistral_7b",
            name="Mistral 7B Instruct",
            task="llm",
            source="huggingface",
            local_path=str(self.models_dir / "mistral-7b-instruct"),
            size_mb=14500,  # Roughly for FP16
            supported_runtimes=["transformers", "onnx"],
            precision="fp32",
            input_shape={"type": "text", "max_tokens": 4096},
            output_shape={"type": "token_ids"},
            typical_latency_ms=2000,  # 2 seconds for ~100 tokens
            preferred_accelerator="NPU",
            fallback_backend="CPU",
            description="7B parameter instruction-tuned LLM, good quality/speed tradeoff",
            qualcomm_ai_hub=False,
            ai_hub_model_id=None
        )
        
        # OCR Model - PaddleOCR
        self._models["ocr_paddleocr"] = ModelConfig(
            model_id="ocr_paddleocr",
            name="PaddleOCR",
            task="ocr",
            source="huggingface",
            local_path=str(self.models_dir / "paddleocr"),
            size_mb=200,
            supported_runtimes=["onnx", "paddle"],
            precision="fp32",
            input_shape={"type": "image", "format": "numpy"},
            output_shape={"type": "text_with_boxes"},
            typical_latency_ms=1500,
            preferred_accelerator="NPU",
            fallback_backend="CPU",
            description="Fast and accurate OCR model, supports multiple languages",
            qualcomm_ai_hub=False,
            ai_hub_model_id=None
        )
        
        # Speech Recognition - Faster Whisper
        self._models["speech_whisper"] = ModelConfig(
            model_id="speech_whisper",
            name="Faster Whisper (base)",
            task="speech",
            source="huggingface",
            local_path=str(self.models_dir / "faster-whisper-base"),
            size_mb=140,
            supported_runtimes=["onnx", "transformers"],
            precision="fp32",
            input_shape={"type": "audio", "sample_rate": 16000},
            output_shape={"type": "text"},
            typical_latency_ms=1000,
            preferred_accelerator="CPU",  # Speech typically CPU or GPU
            fallback_backend="CPU",
            description="Optimized Whisper variant for speech recognition",
            qualcomm_ai_hub=False,
            ai_hub_model_id=None
        )
        
        # Vision/Image Understanding - CLIP
        self._models["vision_clip"] = ModelConfig(
            model_id="vision_clip",
            name="CLIP Vision Model",
            task="vision",
            source="huggingface",
            local_path=str(self.models_dir / "clip-vit-base-patch32"),
            size_mb=600,
            supported_runtimes=["onnx", "transformers"],
            precision="fp32",
            input_shape={"type": "image", "size": [224, 224]},
            output_shape={"type": "float32", "dimensions": 512},
            typical_latency_ms=300,
            preferred_accelerator="GPU",
            fallback_backend="CPU",
            description="Vision encoder from CLIP for image understanding",
            qualcomm_ai_hub=False,
            ai_hub_model_id=None
        )
        
        logger.info(f"Model registry initialized with {len(self._models)} models")
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Get a model configuration by ID"""
        return self._models.get(model_id)
    
    def get_models_by_task(self, task: str) -> List[ModelConfig]:
        """Get all models for a specific task"""
        return [m for m in self._models.values() if m.task == task]
    
    def list_all_models(self) -> List[ModelConfig]:
        """List all registered models"""
        return list(self._models.values())
    
    def register_model(self, model_config: ModelConfig) -> None:
        """Register a new model"""
        self._models[model_config.model_id] = model_config
        logger.info(f"Registered model: {model_config.model_id}")
    
    def get_model_for_task(self, task: str, backend: str = "CPU") -> Optional[ModelConfig]:
        """
        Get the best model for a task given a backend.
        Prioritizes models optimized for the given backend.
        """
        candidates = self.get_models_by_task(task)
        
        # First try to find model optimized for this backend
        for model in candidates:
            if model.preferred_accelerator == backend:
                return model
        
        # Otherwise return first available
        return candidates[0] if candidates else None
    
    def export_models_json(self, filepath: Path) -> None:
        """Export model registry to JSON"""
        data = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "models": [m.to_dict() for m in self._models.values()]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported models to {filepath}")
    
    def import_models_json(self, filepath: Path) -> None:
        """Import model registry from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for model_dict in data.get("models", []):
            config = ModelConfig(**model_dict)
            self.register_model(config)
        
        logger.info(f"Imported {len(data.get('models', []))} models from {filepath}")
    
    def get_download_size_estimate(self) -> Dict[str, float]:
        """Get total download size for all models in MB"""
        sizes = {}
        total = 0
        for model in self._models.values():
            if model.size_mb:
                sizes[model.model_id] = model.size_mb
                total += model.size_mb
        sizes["total_mb"] = total
        return sizes


# Global registry instance
_registry = None


def get_model_registry(models_dir: Path = None) -> ModelRegistry:
    """Get or create the global model registry"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry(models_dir)
    return _registry
