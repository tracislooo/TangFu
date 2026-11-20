$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' 'G:\Doc\ChatGPT\New project\primary-nav-font70-20261101-112732'
if ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }
