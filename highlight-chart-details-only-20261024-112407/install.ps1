$ErrorActionPreference = 'Stop'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:/Doc/ChatGPT/New project/install-match-ui-patch.py' $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw 'Patch installation failed; see the preceding diagnostic.' }
