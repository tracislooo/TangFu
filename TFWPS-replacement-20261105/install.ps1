$ErrorActionPreference='Stop'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:\Doc\ChatGPT\New project\replace-tfwps-v78.py' --install
if($LASTEXITCODE -ne 0){throw 'Failed.'}
