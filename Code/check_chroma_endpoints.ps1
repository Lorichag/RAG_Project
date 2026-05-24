$ErrorActionPreference = 'Continue'
$paths = @('/','/health','/openapi.json','/collections')
foreach ($p in $paths) {
    try {
        $uri = "http://localhost:8100$p"
        $r = Invoke-WebRequest -Uri $uri -Method GET -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Host "$p : $($r.StatusCode)"
    } catch {
        Write-Host "$p : ERROR"
    }
}
