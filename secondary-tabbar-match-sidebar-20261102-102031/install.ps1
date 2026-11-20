$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' 'G:\Doc\ChatGPT\New project\secondary-tabbar-match-sidebar-20261102-102031'
if ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }
