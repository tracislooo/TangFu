$ErrorActionPreference = 'Stop'
$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore
if ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }
