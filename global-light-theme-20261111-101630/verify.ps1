$ErrorActionPreference='Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot --verify
if($LASTEXITCODE -ne 0){throw 'Operation failed; see error above.'}
