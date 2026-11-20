$ErrorActionPreference='Stop'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:\Doc\ChatGPT\New project\fix-card-frame-blue.py' --rollback
if($LASTEXITCODE -ne 0){throw 'Failed.'}
