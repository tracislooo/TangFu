$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='回退/game/ui-backgrounds_assets_common.bundle';Before='a2392faba99831d94a600b6a3161cee3a45cb66ba39a21ebb02efbaedced3561';After='56ca2e55154070e5379cffbd2cc20f4a130d0135f127b4974436dd1cba544d32'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='回退/skin/ui-backgrounds_assets_common.bundle';Before='a2392faba99831d94a600b6a3161cee3a45cb66ba39a21ebb02efbaedced3561';After='56ca2e55154070e5379cffbd2cc20f4a130d0135f127b4974436dd1cba544d32'}
)
foreach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}
$written=@()
try{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}
Write-Output 'Complete.'
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination 'G:\Doc\ChatGPT\New project\current-custom-textures.json' -Force
