$ErrorActionPreference = "Stop"
Write-Host "Verification de l'application RAG..."

# Tester les imports specifiques a l'application
$test_code = @"
from app.config import settings
from app.main import app
from app.ingest import IngestPipeline
from app.retrieve import RetrievalService
from app.generate import GenerationService
print('OK: Application imports successful')
"@

try {
    python -c $test_code
    Write-Host "Application configuree et prete a demarrer!"
} catch {
    Write-Host "Erreur lors du test de l'application"
    Write-Host $_
    exit 1
}
