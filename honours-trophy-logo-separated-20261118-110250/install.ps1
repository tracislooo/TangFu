$ErrorActionPreference='Stop'
& 'C:\Users\traci\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot
if($LASTEXITCODE -ne 0){throw 'Operation failed.'}
