# Xe-Bot Startup Script
# Run this from PowerShell to start both servers

Write-Host "Starting Xe-Bot..." -ForegroundColor Cyan

# Start Backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'D:\spm stuff\task\xe-bot\.venv\Scripts\python.exe' 'E:\Task\xe-bot\server.py'"

# Wait for backend to start
Start-Sleep -Seconds 2

# Start Frontend in new window  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'E:\Task\xe-bot\frontend'; npm run dev"

Write-Host ""
Write-Host "Xe-Bot is starting up!" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening browser in 5 seconds..." -ForegroundColor Cyan

Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
