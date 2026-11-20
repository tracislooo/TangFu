$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}

$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='回退/game/ui-backgrounds_assets_common.bundle';Before='a27ee5134dbda92c80df7d81dad1903b37ef5949d9c8d64648489e8c5d3cf998';After='3c5fd3e0fe56fa81e0a397d263500ee0b1ef0d33109902d2c21ccb22a6e149da'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='回退/skin/ui-backgrounds_assets_common.bundle';Before='a27ee5134dbda92c80df7d81dad1903b37ef5949d9c8d64648489e8c5d3cf998';After='3c5fd3e0fe56fa81e0a397d263500ee0b1ef0d33109902d2c21ccb22a6e149da'}
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_.bundle';Source='回退/game/ui-backgrounds_assets_.bundle';Before='63b1f5c0cd50ea51cec167deaa1408dc97168a754b899a99b08c4ddf022640e8';After='e28cf9e3d09e1c8738b966dd210255d9f98e1b068605df356f0a36e7ba1346c9'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_.bundle';Source='回退/skin/ui-backgrounds_assets_.bundle';Before='63b1f5c0cd50ea51cec167deaa1408dc97168a754b899a99b08c4ddf022640e8';After='e28cf9e3d09e1c8738b966dd210255d9f98e1b068605df356f0a36e7ba1346c9'}
)
foreach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}
$written=@()
try{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination 'G:\Doc\ChatGPT\New project\current-custom-textures.json' -Force
