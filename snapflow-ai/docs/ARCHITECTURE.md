# SnapFlow AI - System Architecture

## Overview

SnapFlow AI is a privacy-first, on-device multimodal AI copilot designed for Snapdragon-powered Windows PCs. The system processes documents, images, and voice input using local AI inference, with dynamic hardware acceleration detection.

## Core Principles

1. **Privacy First**: All documents and AI processing remain local by default
2. **Hardware-Aware**: Dynamic detection and utilization of NPU/GPU/CPU
3. **Graceful Degradation**: CPU fallback when accelerators unavailable
4. **Verifiable**: No fake benchmarks, actual measured latencies
5. **Modular**: Model and backend swapping without application rewrites

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Desktop Application                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Frontend (React/TS)                  │  │
│  │  ┌─────────────┬──────────┬─────────┬────────────┐   │  │
│  │  │  Dashboard  │Documents │Assistant│  Benchmarks│   │  │
│  │  └─────────────┴──────────┴─────────┴────────────┘   │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │ HTTP/WebSocket                   │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │              Backend (FastAPI/Python)               │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │   API Layer                                  │   │  │
│  │  │  /upload, /query, /benchmark, /hardware      │   │  │
│  │  └──────────┬───────────────────────────────────┘   │  │
│  │             │                                        │  │
│  │  ┌──────────▼────────┬──────────────┬────────────┐  │  │
│  │  │ Document Pipeline │ RAG System   │ AI Backend │  │  │
│  │  │ ┌──────────────┐  │ ┌──────────┐ │ ┌────────┐ │  │  │
│  │  │ │ Parse/OCR    │  │ │ Retrieval│ │ │Hardware│ │  │  │
│  │  │ │ Chunking     │  │ │ Scoring  │ │ │Detector│ │  │  │
│  │  │ │ Embedding    │  │ │ Ranking  │ │ │Backend │ │  │  │
│  │  │ └──────────────┘  │ └──────────┘ │ │Selector│ │  │  │
│  │  └──────────────────┴──────────────┴────────────┘  │  │
│  │             │                                        │  │
│  │  ┌──────────▼────────────────────────────────────┐  │  │
│  │  │   Model Registry & Inference Layer            │  │  │
│  │  │  ┌──────────┬──────────┬──────────────────┐   │  │  │
│  │  │  │ OCR/Vision│ Embedding│ LLM Inference   │   │  │  │
│  │  │  │ Model     │ Model    │ Model           │   │  │  │
│  │  │  └──────────┴──────────┴──────────────────┘   │  │  │
│  │  └──────────┬───────────────────────────────────┘  │  │
│  │             │                                        │  │
│  │  ┌──────────▼────────────────────────────────────┐  │  │
│  │  │   Execution Backends                          │  │  │
│  │  │  ┌──────────┬──────────┬──────────────────┐   │  │  │
│  │  │  │ ONNX CPU │ ONNX GPU │ Qualcomm QNN     │   │  │  │
│  │  │  │ (fallback)│ (if avail)│ NPU (if avail) │   │  │  │
│  │  │  └──────────┴──────────┴──────────────────┘   │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │             │                                        │  │
│  │  ┌──────────▼────────────────────────────────────┐  │  │
│  │  │   Local Storage                               │  │  │
│  │  │  ┌────────┬────────┬────────────────────────┐  │  │  │
│  │  │  │SQLite  │ FAISS  │ Document Files        │  │  │  │
│  │  │  │Meta    │ Vector │ (Indexed)             │  │  │  │
│  │  │  │Data    │ DB     │                       │  │  │  │
│  │  │  └────────┴────────┴────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Local Machine (No Cloud Required for Core Features)
```

---

## Component Details

### 1. Hardware Detection Layer

**Location**: `backend/hardware_detector.py`

Detects:
- Windows ARM64 architecture
- CPU capabilities
- Qualcomm NPU presence
- Available AI runtimes
- ONNX Runtime provider availability

**Output**:
```python
{
    "platform": "Windows",
    "architecture": "ARM64",
    "processor": "Snapdragon X...",
    "qualcomm_npu": true,
    "npu_runtime": "QNN",
    "available_backends": ["QNN", "GPU", "CPU"],
    "onnx_runtime_version": "1.16.0",
    "gpu_available": false
}
```

### 2. Model Registry

**Location**: `backend/model_registry.py`

Central registry for all AI models:

```python
ModelRegistry:
  - OCR models
  - Embedding models
  - LLM models
  - Vision models
  - Speech models

Each contains:
  - model_id
  - source
  - local_path
  - supported_runtimes
  - precision (fp32, fp16, int8)
  - input_spec
  - output_spec
  - preferred_accelerator
  - fallback_backend
```

Models selected:
- **Embeddings**: Nomic Embed Text (small, efficient)
- **LLM**: Mistral 7B Instruct (via ONNX if available, else HuggingFace)
- **OCR**: PaddleOCR (open-source, fast)
- **Speech**: Faster Whisper (OpenAI Whisper, optimized)

### 3. Execution Backend Abstraction

**Location**: `backend/backends/`

```python
AIBackend (Abstract)
  ├── CPUBackend (ONNX Runtime - always available)
  ├── QualcommNPUBackend (QNN - Snapdragon only)
  └── GPUBackend (ONNX Runtime CUDA/DirectML)
```

Each backend implements:
```python
def load_model(model_path: str) -> Model
def infer(input_data: Any) -> InferenceResult
def get_metrics() -> HardwareMetrics
```

### 4. Document Processing Pipeline

**Flow**:
```
Document Upload
    ↓
File Validation (type, size)
    ↓
Parsing (PDF, DOCX, images, text)
    ↓
OCR/Text Extraction (if image-based)
    ↓
Chunking (semantic-aware)
    ↓
Embedding Generation (local model)
    ↓
Vector Storage (FAISS)
    ↓
Metadata Indexing (SQLite)
    ↓
Ready for Retrieval
```

**Chunking Strategy**:
- Token-based splitting (optimal for LLM context)
- Overlap for context preservation
- Semantic boundaries preserved
- Page/section metadata attached

### 5. RAG (Retrieval-Augmented Generation)

**Flow**:
```
User Question
    ↓
Embed question (same model as documents)
    ↓
Semantic search in FAISS (top-k retrieval)
    ↓
Rank by relevance + metadata
    ↓
Limit to context window
    ↓
Format context with source citations
    ↓
Pass to Local LLM with system prompt
    ↓
LLM generates grounded answer
    ↓
Post-process & format response
    ↓
Return answer + sources
```

**Safety**:
- If no relevant documents found: "I couldn't find information..."
- Source attribution mandatory
- LLM constrained with system prompt to cite sources

### 6. Local LLM Integration

**Options**:
1. **ONNX Runtime Inference** (if model available in ONNX format)
2. **HuggingFace Transformers** (CPU fallback)
3. **Ollama integration** (if user has Ollama installed locally)

**Model**: Mistral 7B Instruct
- Compact (fits in 8GB RAM)
- Fast inference
- Good quality responses
- ONNX-convertible

### 7. Image & Vision Processing

**Pipeline**:
```
Image Upload
    ↓
Validation & preprocessing
    ↓
OCR (PaddleOCR)
    ↓
Vision Understanding (if model available)
    ↓
Structured text output
    ↓
Store in knowledge base
    ↓
Available for queries
```

### 8. Voice Processing

**Pipeline**:
```
Audio Recording/Upload
    ↓
Speech-to-Text (Faster Whisper)
    ↓
Transcription display
    ↓
Process as text query
    ↓
Generate response
    ↓
Optional: Text-to-Speech for response
```

### 9. Task Extraction System

**Flow**:
```
Document Analyzed
    ↓
LLM extracts tasks with prompt
    ↓
Structured output:
  - task description
  - owner (if mentioned)
  - deadline (if mentioned)
  - priority (inferred)
  - source document
    ↓
Store in SQLite
    ↓
Track: Pending/Complete/Overdue
```

### 10. Benchmarking System

**Measured Metrics**:
- Model load time
- First inference latency
- Subsequent inference latency
- Backend used (NPU/GPU/CPU)
- Tokens processed
- Throughput
- Memory usage (if available)

**Output**:
```json
{
  "operation": "embedding_generation",
  "model": "nomic-embed-text",
  "backend": "CPU",
  "latency_ms": 125,
  "items_processed": 50,
  "throughput": "400 tokens/sec",
  "memory_mb": 342,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Storage**: Local JSON + CSV export

---

## Data Storage

### SQLite Schema

```sql
-- Documents
CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  filename TEXT,
  upload_date TIMESTAMP,
  file_type TEXT,
  source_path TEXT,
  status TEXT
);

-- Chunks
CREATE TABLE chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT,
  content TEXT,
  chunk_index INT,
  page_number INT,
  tokens INT,
  FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Embeddings metadata
CREATE TABLE embeddings_metadata (
  chunk_id TEXT PRIMARY KEY,
  embedding_model TEXT,
  generated_date TIMESTAMP,
  FOREIGN KEY (chunk_id) REFERENCES chunks(id)
);

-- Tasks
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  description TEXT,
  owner TEXT,
  deadline DATE,
  priority TEXT,
  status TEXT,
  source_document_id TEXT,
  created_date TIMESTAMP,
  FOREIGN KEY (source_document_id) REFERENCES documents(id)
);

-- Benchmark results
CREATE TABLE benchmarks (
  id TEXT PRIMARY KEY,
  operation TEXT,
  model TEXT,
  backend TEXT,
  latency_ms FLOAT,
  memory_mb FLOAT,
  timestamp TIMESTAMP
);
```

### Vector Storage (FAISS)

- Index file: `data/faiss_index.bin`
- ID mapping: `data/faiss_id_map.json`
- Dimension: Embedding model output size (384 for Nomic Embed)
- Type: Flat L2 (optimized for small-medium datasets)

---

## API Layer (FastAPI)

### Key Endpoints

```
POST /api/documents/upload
  Upload PDF, image, or document

POST /api/documents/analyze
  Trigger OCR/vision processing

GET /api/documents/list
  List indexed documents

POST /api/query
  Execute RAG query

POST /api/images/analyze
  Vision/OCR on uploaded image

POST /api/voice/transcribe
  Speech-to-text

GET /api/hardware/status
  Get hardware detection results

POST /api/benchmark/run
  Execute benchmark suite

GET /api/tasks/list
  List extracted tasks

POST /api/tasks/extract
  Extract tasks from document
```

---

## Frontend Structure

### Pages

1. **Dashboard** - Hardware status, quick stats
2. **Documents** - Upload, list, manage documents
3. **Assistant** - Query interface, RAG results
4. **Images** - Image upload, OCR, vision
5. **Voice** - Voice recording, transcription
6. **Tasks** - Task management
7. **Benchmarks** - Performance metrics
8. **Hardware** - Detailed hardware info
9. **Privacy** - Privacy policy & settings
10. **Settings** - Configuration

### State Management

- React Context for global state
- Local storage for user preferences
- Real-time WebSocket updates for benchmarks

---

## Deployment & Installation

### System Requirements

**Minimum (CPU Fallback)**:
- Windows 10/11
- 8 GB RAM
- 10 GB disk space
- Python 3.10+
- Node.js 18+

**Recommended (Snapdragon)**:
- Snapdragon X Series processor
- 16 GB RAM
- SSD storage
- Latest Windows 11

### Installation Steps

1. Clone repository
2. Run setup script (PowerShell)
3. Download models (~2-4 GB depending on selection)
4. Initialize database
5. Launch application

---

## Model Deployment

### ONNX Runtime Strategy

Models converted to ONNX format for:
- Consistency across platforms
- QNN execution provider on Snapdragon
- Efficient CPU inference as fallback

### Qualcomm AI Hub Integration

Research and document:
- Available optimized models
- QNN runtime integration
- Model conversion pipeline
- Validation on Snapdragon hardware (future)

---

## Privacy & Security

### Data Handling

- **Documents**: Stored locally in `data/documents/`
- **Embeddings**: Stored locally in FAISS index
- **Tasks**: Stored in local SQLite database
- **No cloud uploads**: All inference local
- **No telemetry**: No tracking by default

### File Security

- File type validation
- Size limits enforced
- Filename sanitization
- Path traversal prevention

---

## Error Handling & Fallback

### Graceful Degradation

| Feature | Primary | Fallback | Unavailable |
|---------|---------|----------|------------|
| Embedding | ONNX NPU | ONNX CPU | Cannot embed |
| LLM Inference | ONNX NPU | HuggingFace CPU | Manual input |
| OCR | Fast QNN | CPU | Manual text |
| Speech | Faster Whisper | Whisper CPU | Manual text |

### User Feedback

- Clear error messages
- Automatic backend fallback
- Status indicators in UI
- No silent failures

---

## Performance Optimization

### Caching

- Model loading cached (in-memory)
- Embedding cache for repeated queries
- Retrieval result cache (short-lived)

### Batch Processing

- Multiple documents simultaneously
- Vectorized operations where possible
- Async I/O for file operations

### Memory Management

- Model unloading when not in use
- Streaming large file processing
- Configurable batch sizes

---

## Testing Strategy

### Unit Tests

- Document parsing correctness
- Chunk boundary correctness
- Embedding generation
- Task extraction
- Hardware detection

### Integration Tests

- End-to-end RAG pipeline
- Backend switching
- API endpoints
- File upload/processing

### Manual Testing

- Demo workflow
- Snapdragon hardware (if available)
- CPU fallback
- Edge cases (corrupted PDF, empty documents)

---

## Roadmap

**Phase 1** (MVP): Core RAG + hardware detection
**Phase 2**: Image intelligence + voice
**Phase 3**: Snapdragon/QNN optimization
**Phase 4**: Advanced features (agents, multimodal)

---

## Technical Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| FastAPI | Type-safe, async, modern Python framework |
| React + TypeScript | Professional UI, type safety |
| FAISS | Lightweight, efficient vector search |
| SQLite | Zero-configuration, local database |
| ONNX Runtime | Universal inference, Snapdragon support |
| Mistral 7B | Compact LLM, good quality |
| Nomic Embed | Small, efficient embeddings |

---

## Metrics for Success

1. ✓ Real working application (not prototype)
2. ✓ No fabricated benchmarks (measured latencies)
3. ✓ Honest hardware reporting (no fake Snapdragon claims)
4. ✓ Core workflow functions without cloud
5. ✓ Clear differentiation from web chatbots
6. ✓ Professional documentation
7. ✓ Deployable to Snapdragon (architecture ready)
8. ✓ Judges can demo in 60 seconds
