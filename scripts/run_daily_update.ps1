param([string]$Python = 'python', [string]$Repository = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference = 'Stop'
$logDir = Join-Path $Repository 'local-data'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir 'daily-update.log'
"[$(Get-Date -Format o)] Starting local listing update" | Add-Content -LiteralPath $log -Encoding UTF8
try {
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $outlookOutput = & (Join-Path $PSScriptRoot 'collect_outlook_alerts.ps1') 2>&1 | Out-String
    [IO.File]::AppendAllText($log, $outlookOutput, $utf8)
    Push-Location $Repository
    try {
        $updateOutput = & $Python (Join-Path $PSScriptRoot 'update_local_listings.py') 2>&1 | Out-String
        $pythonExitCode = $LASTEXITCODE
        [IO.File]::AppendAllText($log, $updateOutput, $utf8)
        if ($pythonExitCode -ne 0) { throw "Local listing updater exited with code $pythonExitCode" }

        $jsonLine = ($updateOutput -split "`r?`n" | Where-Object { $_.Trim().StartsWith('{') } | Select-Object -Last 1)
        if ($jsonLine) {
            $status = $jsonLine | ConvertFrom-Json
            $hasListingInput = [int]$status.mailFilesScanned -gt 0 -or [int]$status.imapAlertsScanned -gt 0 -or [int]$status.ddpropertyRssListings -gt 0
            if (@($status.sourceErrors).Count -gt 0 -and -not $hasListingInput) {
                $sources = @($status.sourceErrors) -join '; '
                throw "No listing source succeeded. $sources"
            }
        }
    }
    finally { Pop-Location }
    "[$(Get-Date -Format o)] Update finished with exit code $LASTEXITCODE" | Add-Content -LiteralPath $log -Encoding UTF8
} catch {
    "[$(Get-Date -Format o)] Update failed: $($_.Exception.Message)" | Add-Content -LiteralPath $log -Encoding UTF8
    exit 1
}
