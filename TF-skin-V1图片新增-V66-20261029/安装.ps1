$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='ui-backgrounds_assets_common.bundle';Before='86dbe16a5ce77a8c2319aab4552fd6e220a7f1d920ac098c1886cd9e78e23434';After='cfe9cfd1a538fb4322ef98660c4246e5e02e942b07cb7c4255e7fc4cdd5ae754'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='ui-backgrounds_assets_common.bundle';Before='86dbe16a5ce77a8c2319aab4552fd6e220a7f1d920ac098c1886cd9e78e23434';After='cfe9cfd1a538fb4322ef98660c4246e5e02e942b07cb7c4255e7fc4cdd5ae754'}
)
foreach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}
$written=@()
try{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}
Write-Output 'Complete.'
& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'G:\Doc\ChatGPT\New project\finish-tf-skin-v1-v66.py' --commit
if($LASTEXITCODE -ne 0){throw 'Registry update failed.'}
