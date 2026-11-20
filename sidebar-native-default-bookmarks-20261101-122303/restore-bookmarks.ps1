$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot --restore
if ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }
