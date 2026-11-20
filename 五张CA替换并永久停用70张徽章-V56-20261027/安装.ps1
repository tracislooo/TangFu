$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle';Source='ui-backgrounds_assets_common.bundle';Before='09ff554a9898c6c072c86b2c58c5f7a0fc03c0685b20085239d14ade512e26ad';After='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d'}
@{Target='F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';Source='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';Before='ac549c0fc2da378ea2a3e3d571e96e88a0503593511bb70a9f2ed28142bd7221';After='f1f2892866010902bf9266de1da43929925df962b2504e168217c441aedcb71b'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-backgrounds_assets_common.bundle';Source='ui-backgrounds_assets_common.bundle';Before='09ff554a9898c6c072c86b2c58c5f7a0fc03c0685b20085239d14ade512e26ad';After='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d'}
@{Target='G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';Source='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';Before='ac549c0fc2da378ea2a3e3d571e96e88a0503593511bb70a9f2ed28142bd7221';After='f1f2892866010902bf9266de1da43929925df962b2504e168217c441aedcb71b'}
)
foreach($item in $items){
 if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before){throw ('Target version mismatch: '+$item.Target)}
 if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Package hash mismatch.'}
}
$written=@()
try{
 foreach($item in $items){$written+=@{Target=$item.Target;Bytes=[IO.File]::ReadAllBytes($item.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force;if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Installed hash mismatch.'}}
}catch{foreach($entry in $written){[IO.File]::WriteAllBytes($entry.Target,$entry.Bytes)};throw}
Write-Output 'Complete.'
