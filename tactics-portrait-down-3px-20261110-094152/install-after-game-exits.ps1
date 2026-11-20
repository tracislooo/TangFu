$status = Join-Path $PSScriptRoot 'automatic-install-status.txt'
Set-Content -LiteralPath $status -Value 'Waiting for Football Manager to exit normally.'
while (Get-Process -Name fm -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 3 }
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\shift-tactics-portrait-down.py' --install $PSScriptRoot *> (Join-Path $PSScriptRoot 'automatic-install.log')
if ($LASTEXITCODE -eq 0) { Set-Content -LiteralPath $status -Value 'Installed and verified.' }
else { Set-Content -LiteralPath $status -Value 'Installation stopped. See automatic-install.log.' }
