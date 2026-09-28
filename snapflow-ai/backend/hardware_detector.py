"""
Hardware Detection Module for SnapFlow AI

Detects available AI accelerators, runtime support, and hardware capabilities.
Never fabricates hardware information - all detection is verified.
"""

import platform
import subprocess
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class HardwareStatus:
    """Represents detected hardware capabilities"""
    platform_name: str  # Windows, Linux, Darwin
    architecture: str  # ARM64, x86_64, etc.
    processor_name: str
    processor_brand: str
    
    # Snapdragon/Qualcomm specific
    is_snapdragon: bool
    snapdragon_model: Optional[str]
    
    # Runtime availability
    onnx_runtime_available: bool
    onnx_runtime_version: Optional[str]
    
    # Accelerators
    npu_available: bool
    npu_type: Optional[str]  # "QNN", "Hexagon", etc.
    gpu_available: bool
    gpu_type: Optional[str]  # "CUDA", "DirectML", "Metal", etc.
    
    # Capabilities
    available_backends: List[str]  # ["QNN", "GPU", "CPU"]
    preferred_backend: str  # Auto-selected best backend
    
    # Memory
    total_memory_gb: Optional[float]
    available_memory_gb: Optional[float]
    
    # Metadata
    detection_timestamp: str
    mode: str  # "Snapdragon Optimization Mode" or "Development Compatibility Mode"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class HardwareDetector:
    """Detects hardware capabilities for SnapFlow AI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = None
    
    def detect(self, force_refresh: bool = False) -> HardwareStatus:
        """
        Detect available hardware capabilities.
        
        Args:
            force_refresh: Force re-detection instead of using cache
            
        Returns:
            HardwareStatus with all detected capabilities
        """
        if self._cache is not None and not force_refresh:
            return self._cache
        
        # Detect basic platform info
        platform_name = platform.system()  # Windows, Linux, Darwin
        architecture = platform.machine()  # ARM64, x86_64, etc.
        processor_name = platform.processor()
        
        # Detect Snapdragon/Qualcomm
        is_snapdragon, snapdragon_model = self._detect_snapdragon(architecture, processor_name)
        
        # Detect ONNX Runtime
        onnx_available, onnx_version = self._detect_onnx_runtime()
        
        # Detect accelerators
        npu_available, npu_type = self._detect_npu(is_snapdragon)
        gpu_available, gpu_type = self._detect_gpu()
        
        # Determine available backends
        available_backends = self._determine_backends(npu_available, gpu_available)
        
        # Select preferred backend
        preferred_backend = self._select_preferred_backend(
            npu_available, gpu_available, architecture
        )
        
        # Get memory info
        total_mem, avail_mem = self._get_memory_info()
        
        # Determine mode
        mode = "Snapdragon Optimization Mode" if is_snapdragon else "Development Compatibility Mode"
        
        # Create status object
        status = HardwareStatus(
            platform_name=platform_name,
            architecture=architecture,
            processor_name=processor_name,
            processor_brand=self._detect_processor_brand(processor_name),
            is_snapdragon=is_snapdragon,
            snapdragon_model=snapdragon_model,
            onnx_runtime_available=onnx_available,
            onnx_runtime_version=onnx_version,
            npu_available=npu_available,
            npu_type=npu_type,
            gpu_available=gpu_available,
            gpu_type=gpu_type,
            available_backends=available_backends,
            preferred_backend=preferred_backend,
            total_memory_gb=total_mem,
            available_memory_gb=avail_mem,
            detection_timestamp=datetime.utcnow().isoformat(),
            mode=mode
        )
        
        self._cache = status
        self.logger.info(f"Hardware detection complete. Mode: {mode}")
        return status
    
    def _detect_snapdragon(self, architecture: str, processor_name: str) -> tuple[bool, Optional[str]]:
        """
        Detect if running on Snapdragon/Qualcomm processor.
        Only returns True if actually detected, never guesses.
        """
        try:
            # Check for ARM64 architecture (necessary but not sufficient)
            if "ARM64" not in architecture and "arm64" not in architecture:
                return False, None
            
            # Check processor name for Qualcomm/Snapdragon indicators
            proc_lower = processor_name.lower()
            if "qualcomm" in proc_lower or "snapdragon" in proc_lower:
                # Extract model if possible
                if "x" in proc_lower:  # Snapdragon X series
                    return True, "Snapdragon X Series"
                elif "8cx" in proc_lower or "8c" in proc_lower:
                    return True, "Snapdragon 8cx"
                else:
                    return True, "Snapdragon (model unknown)"
            
            # Try Windows Registry on ARM64 (Snapdragon detection)
            if platform.system() == "Windows" and "ARM64" in architecture:
                try:
                    import winreg
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
                    )
                    proc_name_reg, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                    if "Qualcomm" in proc_name_reg or "Snapdragon" in proc_name_reg:
                        return True, "Snapdragon (Registry Detected)"
                except Exception:
                    pass
            
            return False, None
            
        except Exception as e:
            self.logger.warning(f"Error detecting Snapdragon: {e}")
            return False, None
    
    def _detect_onnx_runtime(self) -> tuple[bool, Optional[str]]:
        """Detect if ONNX Runtime is available and get version"""
        try:
            import onnxruntime as ort
            version = ort.get_version_string()
            return True, version
        except ImportError:
            return False, None
        except Exception as e:
            self.logger.warning(f"Error detecting ONNX Runtime: {e}")
            return False, None
    
    def _detect_npu(self, is_snapdragon: bool) -> tuple[bool, Optional[str]]:
        """Detect if NPU/Hexagon is available (Snapdragon only)"""
        if not is_snapdragon:
            return False, None
        
        try:
            import onnxruntime as ort
            
            # Check for QNN execution provider (Qualcomm Neural Network)
            if hasattr(ort, "get_available_providers"):
                providers = ort.get_available_providers()
                
                # QNN is Qualcomm's execution provider for Snapdragon
                if "QNNExecutionProvider" in providers:
                    return True, "QNN (Qualcomm Neural Network)"
                
                # Check for Hexagon (older Snapdragon)
                if "HexagonExecutionProvider" in providers:
                    return True, "Hexagon"
            
            return False, None
            
        except Exception as e:
            self.logger.warning(f"Error detecting NPU: {e}")
            return False, None
    
    def _detect_gpu(self) -> tuple[bool, Optional[str]]:
        """Detect if GPU acceleration is available"""
        try:
            import onnxruntime as ort
            
            if hasattr(ort, "get_available_providers"):
                providers = ort.get_available_providers()
                
                # Check for CUDA (NVIDIA)
                if "CUDAExecutionProvider" in providers:
                    return True, "CUDA (NVIDIA)"
                
                # Check for DirectML (Windows)
                if "DmlExecutionProvider" in providers:
                    return True, "DirectML (Windows GPU)"
                
                # Check for CoreML (Apple)
                if "CoreMLExecutionProvider" in providers:
                    return True, "CoreML (Apple)"
            
            return False, None
            
        except Exception as e:
            self.logger.warning(f"Error detecting GPU: {e}")
            return False, None
    
    def _determine_backends(self, npu_available: bool, gpu_available: bool) -> List[str]:
        """Determine which backends are available"""
        backends = ["CPU"]  # CPU is always available
        
        if npu_available:
            backends.insert(0, "NPU")
        
        if gpu_available:
            backends.insert(0, "GPU")
        
        return backends
    
    def _select_preferred_backend(self, npu_available: bool, gpu_available: bool, 
                                  architecture: str) -> str:
        """Select the best available backend"""
        # NPU is preferred on Snapdragon
        if npu_available:
            return "NPU"
        
        # GPU is good if available
        if gpu_available:
            return "GPU"
        
        # CPU is the universal fallback
        return "CPU"
    
    def _detect_processor_brand(self, processor_name: str) -> str:
        """Extract processor brand from name"""
        proc_lower = processor_name.lower()
        
        if "qualcomm" in proc_lower or "snapdragon" in proc_lower:
            return "Qualcomm"
        elif "intel" in proc_lower:
            return "Intel"
        elif "amd" in proc_lower:
            return "AMD"
        elif "apple" in proc_lower:
            return "Apple"
        else:
            return "Unknown"
    
    def _get_memory_info(self) -> tuple[Optional[float], Optional[float]]:
        """Get total and available system memory in GB"""
        try:
            import psutil
            total = psutil.virtual_memory().total / (1024**3)
            available = psutil.virtual_memory().available / (1024**3)
            return round(total, 2), round(available, 2)
        except ImportError:
            return None, None
        except Exception as e:
            self.logger.warning(f"Error getting memory info: {e}")
            return None, None
    
    def get_providers_summary(self) -> Dict[str, bool]:
        """Get a summary of available ONNX Runtime providers"""
        try:
            import onnxruntime as ort
            
            if hasattr(ort, "get_available_providers"):
                providers = ort.get_available_providers()
                return {
                    "qnn": "QNNExecutionProvider" in providers,
                    "gpu_cuda": "CUDAExecutionProvider" in providers,
                    "gpu_dml": "DmlExecutionProvider" in providers,
                    "gpu_coreml": "CoreMLExecutionProvider" in providers,
                    "cpu": "CPUExecutionProvider" in providers,
                }
        except Exception as e:
            self.logger.warning(f"Error getting providers: {e}")
        
        return {"cpu": True}


# Global detector instance
_detector = None


def get_hardware_detector() -> HardwareDetector:
    """Get or create the global hardware detector"""
    global _detector
    if _detector is None:
        _detector = HardwareDetector()
    return _detector


def detect_hardware() -> HardwareStatus:
    """Convenience function to detect hardware"""
    return get_hardware_detector().detect()
