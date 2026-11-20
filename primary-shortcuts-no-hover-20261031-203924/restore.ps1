$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' 'G:\Doc\ChatGPT\New project\primary-shortcuts-no-hover-20261031-203924' --restore
if ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }
