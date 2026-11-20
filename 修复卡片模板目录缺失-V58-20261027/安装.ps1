$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\catalog.bin';Source='game-catalog.bin';Before='9088972d45c3b4d55345ac29d394a362acf68aa6381786a34bc65518877761f9';After='aca4d89d60707ad1f9698a330fccf136485d0673b11714be23e58855fac77422'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\catalog.bin';Source='skin-catalog.bin';Before='efeab63a78084fca7a6fbf850e37c0ca37a4d1eda2f9b71d58fd9727071f8cea';After='efeab63a78084fca7a6fbf850e37c0ca37a4d1eda2f9b71d58fd9727071f8cea'}
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='game-ui-backgrounds_assets_common.bundle';Before='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d';After='77f568302b598735580f53a9583f498f9bc66517847857cb7a3db8671fdda481'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='skin-ui-backgrounds_assets_common.bundle';Before='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d';After='77f568302b598735580f53a9583f498f9bc66517847857cb7a3db8671fdda481'}
)
foreach($item in $items){if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before){throw 'Target version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Package checksum mismatch.'}}
$written=@()
try{foreach($item in $items){$written+=@{Target=$item.Target;Bytes=[IO.File]::ReadAllBytes($item.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force;if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Install verification failed.'}}}catch{foreach($entry in $written){[IO.File]::WriteAllBytes($entry.Target,$entry.Bytes)};throw}
Write-Output 'Complete.'
