# Start the Backend Server
Write-Host "Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload"

# Start the Frontend Development Server
Write-Host "Starting Frontend Development Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd dashboard; npm start"

# Start the Security Monitor
Write-Host "Starting Security Monitor..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python monitor_loop.py"

# Display helpful information
Write-Host "`nApplication is starting up..." -ForegroundColor Cyan
Write-Host "Backend API:    http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend App:   http://localhost:3000" -ForegroundColor Yellow
Write-Host "API Docs (Swagger UI): http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`nNote: The frontend will open automatically in your default browser once it's ready." -ForegroundColor White
