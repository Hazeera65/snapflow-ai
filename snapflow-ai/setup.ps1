# SnapFlow AI - Setup Script for Windows
# Run: .\setup.ps1

Write-Host "================================================"
Write-Host "  SnapFlow AI - Setup Script"
Write-Host "  Private On-Device AI Copilot"
Write-Host "================================================"
Write-Host ""

# Check Python
Write-Host "✓ Checking Python..."
$python = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python 3.10+ not found. Please install Python."
    exit 1
}
Write-Host "  Found: $python"

# Check Node.js
Write-Host "✓ Checking Node.js..."
$node = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Node.js 18+ not found. Please install Node.js."
    exit 1
}
Write-Host "  Found Node.js $node"

# Create Python virtual environment
Write-Host ""
Write-Host "✓ Creating Python virtual environment..."
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "  Created venv/"
} else {
    Write-Host "  venv/ already exists"
}

# Activate virtual environment
Write-Host "✓ Activating virtual environment..."
& "./venv/Scripts/Activate.ps1"

# Install Python dependencies
Write-Host ""
Write-Host "✓ Installing Python dependencies..."
Write-Host "  This may take several minutes..."
pip install --upgrade pip setuptools wheel
cd backend
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install Python dependencies"
    exit 1
}
Write-Host "  Python dependencies installed"
cd ..

# Install Node dependencies
Write-Host ""
Write-Host "✓ Installing Node.js dependencies..."
cd frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install Node dependencies"
    exit 1
}
Write-Host "  Node dependencies installed"
cd ..

# Create data directories
Write-Host ""
Write-Host "✓ Creating data directories..."
New-Item -ItemType Directory -Force -Path "data/documents" > $null
New-Item -ItemType Directory -Force -Path "data/benchmarks" > $null
New-Item -ItemType Directory -Force -Path "models" > $null
Write-Host "  Data directories created"

# Download models
Write-Host ""
Write-Host "✓ Model download instructions:"
Write-Host "  Run: python scripts/download_models.py"
Write-Host "  (This will download ~3-4 GB of models)"

Write-Host ""
Write-Host "================================================"
Write-Host "  ✓ Setup Complete!"
Write-Host "================================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Download models: python scripts/download_models.py"
Write-Host "  2. Start application: .\run.ps1"
Write-Host "  3. Open http://localhost:5173"
Write-Host ""
