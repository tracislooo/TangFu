$ErrorActionPreference='Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\start-banner-video520-tfwx120.py' '--install' $PSScriptRoot
if($LASTEXITCODE -ne 0){throw 'Operation failed.'}
