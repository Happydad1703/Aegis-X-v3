Write-Host "GET http://localhost:8000/api/health"
(iwr http://localhost:8000/api/health).Content
