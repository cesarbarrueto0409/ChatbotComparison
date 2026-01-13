# PowerShell script for Docker development commands

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("up", "down", "restart", "logs", "build", "shell")]
    [string]$Action
)

switch ($Action) {
    "up" {
        Write-Host "Starting development containers with hot reload..." -ForegroundColor Green
        docker-compose up --build -d
        Write-Host "Containers started! API available at http://localhost:3000" -ForegroundColor Green
        Write-Host "Use 'docker-dev.ps1 logs' to see logs" -ForegroundColor Yellow
    }
    "down" {
        Write-Host "Stopping containers..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "Containers stopped!" -ForegroundColor Green
    }
    "restart" {
        Write-Host "Restarting containers..." -ForegroundColor Yellow
        docker-compose restart
        Write-Host "Containers restarted!" -ForegroundColor Green
    }
    "logs" {
        Write-Host "Showing logs (Ctrl+C to exit)..." -ForegroundColor Blue
        docker-compose logs -f api
    }
    "build" {
        Write-Host "Rebuilding containers..." -ForegroundColor Yellow
        docker-compose build --no-cache
        Write-Host "Build complete!" -ForegroundColor Green
    }
    "shell" {
        Write-Host "Opening shell in API container..." -ForegroundColor Blue
        docker-compose exec api bash
    }
}