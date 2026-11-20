$ErrorActionPreference = 'Stop'
Start-Sleep -Seconds 45
$shutdownNote = 'Normal shutdown requested at ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Set-Content -LiteralPath 'G:/Doc/ChatGPT/New project/match-ui-layout-refinement-20261023-142923/shutdown-status.txt' -Value $shutdownNote -Encoding UTF8
& "$env:SystemRoot\System32\shutdown.exe" /s /t 0
if ($LASTEXITCODE -ne 0) {
    Add-Content -LiteralPath 'G:/Doc/ChatGPT/New project/match-ui-layout-refinement-20261023-142923/shutdown-status.txt' -Value ('Shutdown returned exit code ' + $LASTEXITCODE) -Encoding UTF8
}
