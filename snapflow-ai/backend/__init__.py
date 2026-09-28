"""
SnapFlow AI Backend Package

Core backend modules for AI inference, document processing, and system monitoring.
"""

from .hardware_detector import detect_hardware, get_hardware_detector, HardwareStatus
from .model_registry import get_model_registry, ModelConfig, ModelRegistry
from .backends import get_backend_selector, BackendSelector

__version__ = "0.1.0"
__all__ = [
    "detect_hardware",
    "get_hardware_detector",
    "HardwareStatus",
    "get_model_registry",
    "ModelConfig",
    "ModelRegistry",
    "get_backend_selector",
    "BackendSelector"
]
