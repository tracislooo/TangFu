$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot 'full-sidebar-rollback/installer.py') (Join-Path $PSScriptRoot 'full-sidebar-rollback') --restore
if ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }
