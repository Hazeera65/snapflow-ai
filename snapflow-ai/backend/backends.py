"""
Backend Abstraction Layer for SnapFlow AI

Provides unified interface for different execution backends:
- ONNX Runtime (CPU, NPU via QNN, GPU via DirectML/CUDA)
- HuggingFace Transformers (CPU fallback)
- Optional GPU acceleration

Each backend handles its own model loading, inference, and performance tracking.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class InferenceMetrics:
    """Metrics from a single inference operation"""
    operation: str
    model_id: str
    backend: str
    latency_ms: float
    timestamp: str
    backend_info: str
    tokens_processed: Optional[int] = None
    memory_mb: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AIBackend(ABC):
    """Abstract base class for AI execution backends"""
    
    def __init__(self, backend_name: str):
        self.backend_name = backend_name
        self.logger = logging.getLogger(f"backend.{backend_name}")
        self.metrics_history: List[InferenceMetrics] = []
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available in current environment"""
        pass
    
    @abstractmethod
    def load_model(self, model_path: str, model_config: Dict) -> None:
        """Load a model for inference"""
        pass
    
    @abstractmethod
    def infer(self, input_data: Any, **kwargs) -> Any:
        """Run inference on loaded model"""
        pass
    
    @abstractmethod
    def unload_model(self) -> None:
        """Unload model and free resources"""
        pass
    
    def record_metric(self, operation: str, model_id: str, latency_ms: float, 
                     tokens: Optional[int] = None, memory_mb: Optional[float] = None) -> InferenceMetrics:
        """Record inference metrics"""
        metric = InferenceMetrics(
            operation=operation,
            model_id=model_id,
            backend=self.backend_name,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat(),
            backend_info=self._get_backend_info(),
            tokens_processed=tokens,
            memory_mb=memory_mb
        )
        self.metrics_history.append(metric)
        return metric
    
    def _get_backend_info(self) -> str:
        """Get human-readable backend information"""
        return self.backend_name
    
    def get_metrics_history(self) -> List[Dict]:
        """Get all recorded metrics"""
        return [m.to_dict() for m in self.metrics_history]
    
    def export_metrics(self, filepath: Path) -> None:
        """Export metrics to JSON file"""
        data = {
            "backend": self.backend_name,
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_inferences": len(self.metrics_history),
            "metrics": [m.to_dict() for m in self.metrics_history]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Exported {len(self.metrics_history)} metrics to {filepath}")


class ONNXCPUBackend(AIBackend):
    """ONNX Runtime CPU Backend - Universal fallback"""
    
    def __init__(self):
        super().__init__("ONNX-CPU")
        self.session = None
        self.model_path = None
    
    def is_available(self) -> bool:
        """Check if ONNX Runtime is installed"""
        try:
            import onnxruntime as ort
            # CPU is always available
            return "CPUExecutionProvider" in ort.get_available_providers()
        except ImportError:
            return False
    
    def load_model(self, model_path: str, model_config: Dict) -> None:
        """Load ONNX model"""
        try:
            import onnxruntime as ort
            
            self.model_path = model_path
            
            # Create session with CPU provider
            session_options = ort.SessionOptions()
            session_options.log_severity_level = 3  # Error only
            
            self.session = ort.InferenceSession(
                model_path,
                providers=["CPUExecutionProvider"],
                sess_options=session_options
            )
            
            self.logger.info(f"Loaded ONNX model from {model_path} on CPU backend")
        
        except Exception as e:
            self.logger.error(f"Failed to load ONNX model: {e}")
            raise
    
    def infer(self, input_data: Any, **kwargs) -> Any:
        """Run inference"""
        if self.session is None:
            raise RuntimeError("Model not loaded")
        
        try:
            start_time = time.perf_counter()
            output = self.session.run(None, input_data)
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            return {
                "output": output,
                "latency_ms": latency_ms,
                "backend": self.backend_name
            }
        
        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            raise
    
    def unload_model(self) -> None:
        """Unload model"""
        self.session = None
        self.model_path = None


class ONNXQNNBackend(AIBackend):
    """ONNX Runtime QNN Backend for Qualcomm Snapdragon NPU"""
    
    def __init__(self):
        super().__init__("ONNX-QNN")
        self.session = None
        self.model_path = None
    
    def is_available(self) -> bool:
        """Check if QNN execution provider is available"""
        try:
            import onnxruntime as ort
            return "QNNExecutionProvider" in ort.get_available_providers()
        except ImportError:
            return False
    
    def load_model(self, model_path: str, model_config: Dict) -> None:
        """Load ONNX model for QNN execution"""
        try:
            import onnxruntime as ort
            
            self.model_path = model_path
            
            # Create session with QNN provider
            session_options = ort.SessionOptions()
            session_options.log_severity_level = 3
            
            # QNN is preferred, CPU as fallback
            self.session = ort.InferenceSession(
                model_path,
                providers=["QNNExecutionProvider", "CPUExecutionProvider"],
                sess_options=session_options
            )
            
            self.logger.info(f"Loaded ONNX model from {model_path} on QNN backend")
        
        except Exception as e:
            self.logger.error(f"Failed to load model on QNN backend: {e}")
            raise
    
    def infer(self, input_data: Any, **kwargs) -> Any:
        """Run inference on QNN"""
        if self.session is None:
            raise RuntimeError("Model not loaded")
        
        try:
            start_time = time.perf_counter()
            output = self.session.run(None, input_data)
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Check which provider was actually used
            provider_used = "QNN" if "QNNExecutionProvider" in [p[0] for p in self.session.get_providers()] else "CPU"
            
            return {
                "output": output,
                "latency_ms": latency_ms,
                "backend": self.backend_name,
                "provider": provider_used
            }
        
        except Exception as e:
            self.logger.error(f"QNN inference failed: {e}")
            raise
    
    def unload_model(self) -> None:
        """Unload model"""
        self.session = None
        self.model_path = None


class HuggingFaceCPUBackend(AIBackend):
    """HuggingFace Transformers CPU Backend - Universal Python fallback"""
    
    def __init__(self):
        super().__init__("HuggingFace-CPU")
        self.model = None
        self.tokenizer = None
        self.model_name = None
    
    def is_available(self) -> bool:
        """Check if transformers library is available"""
        try:
            import transformers
            return True
        except ImportError:
            return False
    
    def load_model(self, model_path: str, model_config: Dict) -> None:
        """Load HuggingFace model"""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            self.model_name = model_config.get("model_name", model_path)
            
            # Try to load from local path first, then from HuggingFace
            self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            
            self.logger.info(f"Loaded HuggingFace model: {self.model_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to load HuggingFace model: {e}")
            raise
    
    def infer(self, input_data: Any, **kwargs) -> Any:
        """Run inference"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            start_time = time.perf_counter()
            
            # Handle different input types
            if isinstance(input_data, str):
                # Text input - embedding
                inputs = self.tokenizer(input_data, return_tensors="pt", truncation=True)
                output = self.model(**inputs)
            else:
                # Raw tensor input
                output = self.model(input_data)
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            return {
                "output": output,
                "latency_ms": latency_ms,
                "backend": self.backend_name
            }
        
        except Exception as e:
            self.logger.error(f"HuggingFace inference failed: {e}")
            raise
    
    def unload_model(self) -> None:
        """Unload model"""
        self.model = None
        self.tokenizer = None


class BackendSelector:
    """Selects and manages execution backends"""
    
    def __init__(self):
        self.logger = logging.getLogger("backend.selector")
        self.backends: Dict[str, AIBackend] = {}
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize all available backends"""
        
        # Always initialize ONNX CPU (universal fallback)
        onnx_cpu = ONNXCPUBackend()
        if onnx_cpu.is_available():
            self.backends["onnx-cpu"] = onnx_cpu
            self.logger.info("ONNX CPU backend available")
        
        # Initialize QNN if available (Snapdragon)
        qnn = ONNXQNNBackend()
        if qnn.is_available():
            self.backends["qnn"] = qnn
            self.logger.info("QNN backend available (Snapdragon NPU)")
        
        # Initialize HuggingFace CPU fallback
        hf_cpu = HuggingFaceCPUBackend()
        if hf_cpu.is_available():
            self.backends["transformers-cpu"] = hf_cpu
            self.logger.info("HuggingFace CPU backend available")
    
    def get_available_backends(self) -> List[str]:
        """List all available backends"""
        return list(self.backends.keys())
    
    def select_backend(self, preferred: str = None, task: str = None) -> AIBackend:
        """
        Select best backend for the task
        
        Args:
            preferred: Preferred backend name
            task: Task type (embedding, llm, ocr, etc.)
        
        Returns:
            Selected backend
        """
        # If preferred backend specified and available, use it
        if preferred and preferred in self.backends:
            return self.backends[preferred]
        
        # Prefer order: QNN > ONNX-CPU > HuggingFace-CPU
        priority_order = ["qnn", "onnx-cpu", "transformers-cpu"]
        
        for backend_name in priority_order:
            if backend_name in self.backends:
                return self.backends[backend_name]
        
        # Fallback to first available
        if self.backends:
            backend = next(iter(self.backends.values()))
            self.logger.warning(f"Using fallback backend: {backend.backend_name}")
            return backend
        
        raise RuntimeError("No AI backends available")
    
    def get_backend(self, name: str) -> Optional[AIBackend]:
        """Get a specific backend by name"""
        return self.backends.get(name)


# Global backend selector instance
_selector = None


def get_backend_selector() -> BackendSelector:
    """Get or create global backend selector"""
    global _selector
    if _selector is None:
        _selector = BackendSelector()
    return _selector
