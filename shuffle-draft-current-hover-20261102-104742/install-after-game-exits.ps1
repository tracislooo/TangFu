$ErrorActionPreference = 'Stop'
$statusPath = Join-Path $PSScriptRoot 'automatic-install-status.txt'
$logPath = Join-Path $PSScriptRoot 'automatic-install.log'
Set-Content -LiteralPath $statusPath -Value 'Waiting for Football Manager to exit normally.' -Encoding UTF8
while ($true) {
    while (Get-Process -Name fm -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
    & 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:/Doc/ChatGPT/New project/install-independent-resource-patch.py' $PSScriptRoot *> $logPath
    if ($LASTEXITCODE -eq 0) {
        Set-Content -LiteralPath $statusPath -Value ('Installed and verified at ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) -Encoding UTF8
        break
    }
    if (Get-Process -Name fm -ErrorAction SilentlyContinue) { continue }
    Set-Content -LiteralPath $statusPath -Value 'Installation stopped. See automatic-install.log; resource files may have changed.' -Encoding UTF8
    break
}
