$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='回退/game/ui-backgrounds_assets_common.bundle';Before='3c5fd3e0fe56fa81e0a397d263500ee0b1ef0d33109902d2c21ccb22a6e149da';After='cbcdd2405f557668a3cc919dbf257635aa801097ba1054565604ac2e5242a7c0'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='回退/skin/ui-backgrounds_assets_common.bundle';Before='3c5fd3e0fe56fa81e0a397d263500ee0b1ef0d33109902d2c21ccb22a6e149da';After='cbcdd2405f557668a3cc919dbf257635aa801097ba1054565604ac2e5242a7c0'}
)
foreach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}
$written=@()
try{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}
Write-Output 'Complete.'
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination 'G:\Doc\ChatGPT\New project\current-custom-textures.json' -Force
