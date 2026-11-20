$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$files = @(
    @{ Target = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'; Source = '回退/game/ui-backgrounds_assets_common.bundle'; Backup = 'ui-backgrounds_assets_common.bundle'; Before = 'b2bbb97be8da1f7e88a1c29df00cf131e3b545f70f64e4c3374dc05343662c63'; After = '4a6ac770b50b6c6e08021a00799d5aec5ebc58b6b7a01e12a0d72e95cc0c2aac' },
    @{ Target = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Source = '回退/game/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Backup = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Before = 'c6b3dcacd3a66a4d1de4f4ee553efe0f55ccdd679e6aaddcffe96bf6d630bcab'; After = '1426c06d078c165c6cc928e85c9f4c56cfb551883b061991aaca6a48a23451b5' },
    @{ Target = 'G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Source = '回退/skin/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Backup = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Before = 'c6b3dcacd3a66a4d1de4f4ee553efe0f55ccdd679e6aaddcffe96bf6d630bcab'; After = '1426c06d078c165c6cc928e85c9f4c56cfb551883b061991aaca6a48a23451b5' }
)
foreach ($item in $files) {
    if ((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before) { throw ('Bundle version mismatch: ' + $item.Target) }
    if ((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After) { throw 'Source bundle hash mismatch.' }
}
try {
    foreach ($item in $files) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force
        if ((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After) { throw 'Installed bundle hash mismatch.' }
    }
} catch {
    foreach ($item in $files) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Backup) -Destination $item.Target -Force }
    throw
}
Write-Host 'Complete.'
