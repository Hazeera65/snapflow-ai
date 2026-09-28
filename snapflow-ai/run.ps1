# SnapFlow AI - Run Script for Windows
# Run: .\run.ps1

Write-Host "================================================"
Write-Host "  SnapFlow AI - Starting Application"
Write-Host "================================================"
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "✗ Virtual environment not found. Run .\setup.ps1 first"
    exit 1
}

# Activate virtual environment
& "./venv/Scripts/Activate.ps1"

Write-Host "✓ Activating Python virtual environment..."

# Check if models are downloaded
Write-Host ""
Write-Host "✓ Checking for models..."
if (-not (Test-Path "models/mistral-7b-instruct")) {
    Write-Host "⚠ Models not found. Models will be downloaded on first use."
    Write-Host "  To download now: python scripts/download_models.py"
    Write-Host ""
}

# Start backend
Write-Host "✓ Starting FastAPI backend..."
Write-Host "  Backend: http://localhost:8000"
Write-Host "  API Docs: http://localhost:8000/docs"

$backendProcess = Start-Process -FilePath python -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload" -PassThru
$backendPID = $backendProcess.Id

Write-Host "  Backend PID: $backendPID"

# Wait for backend to start
Write-Host ""
Write-Host "⏳ Waiting for backend to start (5 seconds)..."
Start-Sleep -Seconds 5

# Check if backend started
$testBackend = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -ErrorAction SilentlyContinue
if (-not $testBackend) {
    Write-Host "✗ Backend failed to start. Check logs above."
    Stop-Process -Id $backendPID
    exit 1
}
Write-Host "✓ Backend started successfully"

# Start frontend
Write-Host ""
Write-Host "✓ Starting React frontend..."
Write-Host "  Frontend: http://localhost:5173"

cd frontend
$frontendProcess = Start-Process -FilePath npm -ArgumentList "run dev" -PassThru
$frontendPID = $frontendProcess.Id

Write-Host "  Frontend PID: $frontendPID"
cd ..

Write-Host ""
Write-Host "================================================"
Write-Host "  ✓ SnapFlow AI Started!"
Write-Host "================================================"
Write-Host ""
Write-Host "Access the application:"
Write-Host "  Web UI: http://localhost:5173"
Write-Host "  API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop the application"
Write-Host ""

# Wait for either process to exit
$running = $true
while ($running) {
    if (!(Get-Process -Id $backendPID -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "✗ Backend process ended"
        $running = $false
    }
    if (!(Get-Process -Id $frontendPID -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "✗ Frontend process ended"
        $running = $false
    }
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Shutting down..."
Stop-Process -Id $backendPID -ErrorAction SilentlyContinue
Stop-Process -Id $frontendPID -ErrorAction SilentlyContinue
Write-Host "Done"
