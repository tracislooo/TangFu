$ErrorActionPreference='Stop'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:\Doc\ChatGPT\New project\add-patchplayerbggreen-v79.py' --install
if($LASTEXITCODE -ne 0){throw 'Operation failed.'}
