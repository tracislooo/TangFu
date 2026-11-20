$ErrorActionPreference='Stop'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:\Doc\ChatGPT\New project\remove-player-top-v74.py' --install
if($LASTEXITCODE -ne 0){throw 'Install failed.'}
