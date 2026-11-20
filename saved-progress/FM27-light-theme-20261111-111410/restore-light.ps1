$ErrorActionPreference='Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' (Join-Path $PSScriptRoot 'switch-theme.py') --light
if($LASTEXITCODE -ne 0){throw 'Theme switch failed; see the error above.'}
