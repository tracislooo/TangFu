$ErrorActionPreference='Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' $PSScriptRoot --restore
if($LASTEXITCODE -ne 0){throw 'Operation failed'}
