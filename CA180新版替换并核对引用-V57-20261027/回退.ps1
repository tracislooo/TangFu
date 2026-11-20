$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='回退/game/ui-backgrounds_assets_common.bundle';Before='77f568302b598735580f53a9583f498f9bc66517847857cb7a3db8671fdda481';After='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='回退/skin/ui-backgrounds_assets_common.bundle';Before='77f568302b598735580f53a9583f498f9bc66517847857cb7a3db8671fdda481';After='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d'}
)
foreach($item in $items){if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before){throw 'Target version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Source hash mismatch.'}}
$written=@()
try{foreach($item in $items){$written+=@{Target=$item.Target;Bytes=[IO.File]::ReadAllBytes($item.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force;if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Installed hash mismatch.'}}}catch{foreach($entry in $written){[IO.File]::WriteAllBytes($entry.Target,$entry.Bytes)};throw}
Write-Output 'Complete.'
