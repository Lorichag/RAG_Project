$ErrorActionPreference = "Stop"
Write-Host "Démarrage des services Docker..."
docker compose up --build
