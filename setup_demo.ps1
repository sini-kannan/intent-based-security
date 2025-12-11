# Quick Setup Script for Zero-Downtime Demo
# Run this first to set up the demo environment

Write-Host "Setting up Zero-Downtime Demo Environment..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Create demo container
Write-Host "[1/3] Creating demo-web container..." -ForegroundColor Blue
docker run -d --name demo-web nginx
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container created successfully" -ForegroundColor Green
} else {
    Write-Host "Container might already exist, trying to start it..." -ForegroundColor Yellow
    docker start demo-web
}

Start-Sleep -Seconds 2

# Step 2: Verify container is running
Write-Host ""
Write-Host "[2/3] Verifying container status..." -ForegroundColor Blue
$status = docker inspect -f '{{.State.Running}}' demo-web 2>$null
if ($status -eq "true") {
    Write-Host "✅ Container is running" -ForegroundColor Green
} else {
    Write-Host "❌ Container failed to start" -ForegroundColor Red
    exit 1
}

# Step 3: Test connectivity
Write-Host ""
Write-Host "[3/3] Testing network connectivity..." -ForegroundColor Blue
$testResult = docker exec demo-web ping -c 2 google.com 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Network connectivity OK" -ForegroundColor Green
} else {
    Write-Host "⚠️  Network test failed (this might be OK if ping is not installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run the demo with:" -ForegroundColor White
Write-Host "  .\demo_zero_downtime.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or manually test with:" -ForegroundColor White
Write-Host "  docker exec demo-web ping google.com" -ForegroundColor Yellow
