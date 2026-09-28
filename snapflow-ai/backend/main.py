"""
SnapFlow AI - FastAPI Backend

Main application server with endpoints for:
- Document upload and processing
- RAG queries
- Hardware monitoring
- Benchmarking
- Task extraction
"""

import logging
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json
from datetime import datetime

from hardware_detector import detect_hardware, HardwareStatus
from model_registry import get_model_registry
from backends import get_backend_selector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SnapFlow AI",
    description="Private On-Device Multimodal AI Copilot",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
hardware_status: Optional[HardwareStatus] = None
model_registry = get_model_registry()
backend_selector = get_backend_selector()


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    document_id: Optional[str] = None


class HardwareStatusResponse(BaseModel):
    platform: str
    architecture: str
    processor: str
    is_snapdragon: bool
    snapdragon_model: Optional[str]
    available_backends: List[str]
    preferred_backend: str
    mode: str
    npu_available: bool
    gpu_available: bool
    total_memory_gb: Optional[float]
    timestamp: str


class ModelsListResponse(BaseModel):
    total_models: int
    models: List[dict]
    total_download_mb: float


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    global hardware_status
    
    logger.info("Starting SnapFlow AI backend")
    
    # Detect hardware
    hardware_status = detect_hardware()
    logger.info(f"Hardware detection complete: {hardware_status.mode}")
    logger.info(f"Available backends: {hardware_status.available_backends}")
    logger.info(f"Preferred backend: {hardware_status.preferred_backend}")
    
    # Log model registry
    models = model_registry.list_all_models()
    logger.info(f"Model registry loaded with {len(models)} models")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SnapFlow AI",
        "version": "0.1.0",
        "status": "ready"
    }


@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/hardware/status", response_model=HardwareStatusResponse)
async def get_hardware_status():
    """Get current hardware capabilities"""
    if hardware_status is None:
        raise HTTPException(status_code=500, detail="Hardware not detected")
    
    return HardwareStatusResponse(
        platform=hardware_status.platform_name,
        architecture=hardware_status.architecture,
        processor=hardware_status.processor_name,
        is_snapdragon=hardware_status.is_snapdragon,
        snapdragon_model=hardware_status.snapdragon_model,
        available_backends=hardware_status.available_backends,
        preferred_backend=hardware_status.preferred_backend,
        mode=hardware_status.mode,
        npu_available=hardware_status.npu_available,
        gpu_available=hardware_status.gpu_available,
        total_memory_gb=hardware_status.total_memory_gb,
        timestamp=hardware_status.detection_timestamp
    )


@app.get("/api/models", response_model=ModelsListResponse)
async def list_models():
    """List all available models"""
    models = model_registry.list_all_models()
    sizes = model_registry.get_download_size_estimate()
    
    return ModelsListResponse(
        total_models=len(models),
        models=[m.to_dict() for m in models],
        total_download_mb=sizes.get("total_mb", 0)
    )


@app.get("/api/backends")
async def list_backends():
    """List available execution backends"""
    available = backend_selector.get_available_backends()
    
    return {
        "available_backends": available,
        "total": len(available)
    }


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    
    # Validate file type
    allowed_types = {"application/pdf", "text/plain", "image/png", "image/jpeg"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported"
        )
    
    # Validate file size (max 50 MB)
    max_size = 50 * 1024 * 1024
    
    try:
        # Save file
        docs_dir = Path(__file__).parent.parent / "data" / "documents"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = docs_dir / file.filename
        content = await file.read()
        
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 50 MB)")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Uploaded document: {file.filename}")
        
        return {
            "status": "success",
            "filename": file.filename,
            "size_bytes": len(content),
            "path": str(file_path),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def execute_query(request: QueryRequest):
    """Execute a RAG query"""
    
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # This is a placeholder - full RAG implementation in Phase 2
        return {
            "question": request.question,
            "answer": "RAG system not yet implemented. This is a placeholder response.",
            "sources": [],
            "confidence": 0.0,
            "backend": hardware_status.preferred_backend if hardware_status else "CPU",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/benchmark/run")
async def run_benchmark():
    """Run inference benchmarks"""
    
    try:
        results = []
        
        # Get available backends
        available_backends = backend_selector.get_available_backends()
        
        for backend_name in available_backends:
            backend = backend_selector.get_backend(backend_name)
            
            if backend:
                # Record that we've checked this backend
                results.append({
                    "backend": backend_name,
                    "available": True,
                    "status": "ready"
                })
        
        return {
            "status": "benchmarks_available",
            "backends_tested": results,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Detailed benchmarks will run in Phase 2"
        }
    
    except Exception as e:
        logger.error(f"Error running benchmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/list")
async def list_tasks():
    """List extracted tasks"""
    
    # Placeholder - full implementation in Phase 2
    return {
        "tasks": [],
        "pending": 0,
        "completed": 0,
        "overdue": 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/privacy/policy")
async def get_privacy_policy():
    """Get privacy information"""
    
    return {
        "privacy_first": True,
        "claims": [
            "Documents stay on device",
            "AI inference runs locally when supported",
            "No document uploaded to cloud servers",
            "Local knowledge base only",
            "No mandatory cloud API key required"
        ],
        "data_storage": {
            "documents": "Local filesystem (data/documents/)",
            "embeddings": "Local FAISS index (data/)",
            "tasks": "Local SQLite database (data/)",
            "benchmarks": "Local JSON files (data/benchmarks/)"
        }
    }


@app.get("/api/info")
async def get_info():
    """Get application information"""
    
    return {
        "name": "SnapFlow AI",
        "version": "0.1.0",
        "description": "Private On-Device Multimodal Work Copilot",
        "github": "https://github.com/yourusername/snapflow-ai",
        "features": {
            "document_processing": True,
            "rag_retrieval": True,
            "image_ocr": True,
            "voice_input": False,  # Phase 3
            "task_extraction": True,
            "hardware_acceleration": True,
            "benchmarking": True
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Custom general exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def main():
    """Run the server"""
    port = int(os.getenv("SNAPFLOW_PORT", 8000))
    host = os.getenv("SNAPFLOW_HOST", "127.0.0.1")
    
    logger.info(f"Starting SnapFlow AI server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
