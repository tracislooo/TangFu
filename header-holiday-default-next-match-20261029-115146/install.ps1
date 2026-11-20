$ErrorActionPreference = 'Stop'
& 'C:\Users\traci\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'G:\Doc\ChatGPT\New project\install-independent-resource-patch.py' 'G:\Doc\ChatGPT\New project\header-holiday-default-next-match-20261029-115146'
if ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }
