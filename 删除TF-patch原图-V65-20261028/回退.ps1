$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='回退/game/ui-backgrounds_assets_common.bundle';Before='86dbe16a5ce77a8c2319aab4552fd6e220a7f1d920ac098c1886cd9e78e23434';After='9a71df88cb399a18c818f06b018f72b04458d898c463f7565fee02b885040eec'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='回退/skin/ui-backgrounds_assets_common.bundle';Before='86dbe16a5ce77a8c2319aab4552fd6e220a7f1d920ac098c1886cd9e78e23434';After='9a71df88cb399a18c818f06b018f72b04458d898c463f7565fee02b885040eec'}
)
foreach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Target version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}
$written=@()
try{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination 'G:\Doc\ChatGPT\New project\current-custom-textures.json' -Force
