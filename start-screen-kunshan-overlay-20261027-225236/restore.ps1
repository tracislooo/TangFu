$ErrorActionPreference='Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\add-start-screen-kunshan-overlay.py' '--restore' $PSScriptRoot
if($LASTEXITCODE -ne 0){throw 'Operation failed.'}
