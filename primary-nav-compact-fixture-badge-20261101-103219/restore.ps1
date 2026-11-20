$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' 'G:\Doc\ChatGPT\New project\primary-nav-compact-fixture-badge-20261101-103219' --restore
if ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }
