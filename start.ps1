# Stop script execution if a critical error occurs
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor DarkCyan
Write-Host "Starting Mental Health Companion App..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor DarkCyan

Write-Host "Cleaning up any old processes..."
# Windows equivalent of fuser: Get the network connection, find the PID, and kill it
$tcp8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($tcp8000) { Stop-Process -Id $tcp8000.OwningProcess -Force -ErrorAction SilentlyContinue }

$tcp8084 = Get-NetTCPConnection -LocalPort 8084 -ErrorAction SilentlyContinue
if ($tcp8084) { Stop-Process -Id $tcp8084.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "Starting backend server on port 8000..." -ForegroundColor Green
# Start-Process with -PassThru returns the process object so we can track its PID
$backendProcess = Start-Process -FilePath "uv" -ArgumentList "run run.py" -WorkingDirectory "$PWD\backend" -PassThru -NoNewWindow

Write-Host "Starting frontend server on port 8084..." -ForegroundColor Green
# Using 'python' instead of 'python3' for Windows compatibility
$frontendProcess = Start-Process -FilePath "python" -ArgumentList "-m http.server 8084" -WorkingDirectory "$PWD\frontend" -PassThru -NoNewWindow

Write-Host "==========================================" -ForegroundColor DarkCyan
Write-Host "✅ App is now running!" -ForegroundColor Green
Write-Host "🌐 Frontend UI: http://localhost:8084" -ForegroundColor Green
Write-Host "⚙️  Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop both servers safely." -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor DarkCyan

# The Windows equivalent of Bash's 'trap' and 'wait'
try {
    # Keeps the script running until both processes naturally exit (or user hits Ctrl+C)
    Wait-Process -Id $backendProcess.Id, $frontendProcess.Id
}
finally {
    # The 'finally' block acts like the INT trap. It triggers when Ctrl+C breaks the Wait-Process
    Write-Host "`nStopping servers..." -ForegroundColor Red
    if (-not $backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
    if (-not $frontendProcess.HasExited) { Stop-Process -Id $frontendProcess.Id -Force }
}