$ErrorActionPreference='Stop'
& 'C:\Users\traci\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' $PSScriptRoot --restore
if($LASTEXITCODE -ne 0){throw 'Operation failed.'}
