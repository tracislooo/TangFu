$ErrorActionPreference='Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\resize-start-banner-video390-tfwx240.py' '--install' $PSScriptRoot
if($LASTEXITCODE -ne 0){throw 'Operation failed.'}
