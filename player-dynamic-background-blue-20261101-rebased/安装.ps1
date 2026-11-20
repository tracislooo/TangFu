$ErrorActionPreference='Stop'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:\Doc\ChatGPT\New project\fix-dynamic-player-background-blue.py' --output-dir 'player-dynamic-background-blue-20261101-rebased' --install
if($LASTEXITCODE -ne 0){throw 'Install failed.'}
