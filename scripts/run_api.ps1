Write-Host "Starting FastAPI server..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
