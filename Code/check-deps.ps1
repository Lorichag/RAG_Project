$ErrorActionPreference = "Stop"
Write-Host "Vérification des dépendances..."

$packages = @(
    'fastapi',
    'uvicorn', 
    'pydantic',
    'sqlalchemy',
    'psycopg',
    'minio',
    'requests'
)

$ok = 0
$errors = @()

foreach ($pkg in $packages) {
    try {
        python -c "import $pkg; print('  OK: $pkg')"
        $ok++
    } catch {
        $errors += $pkg
        Write-Host "  ERREUR: $pkg"
    }
}

Write-Host ""
Write-Host "Résultat: $ok/$($packages.Count) packages"
if ($errors.Count -gt 0) {
    Write-Host "Packages manquants: $($errors -join ', ')"
    exit 1
} else {
    Write-Host "Toutes les dépendances sont installées!"
    exit 0
}
