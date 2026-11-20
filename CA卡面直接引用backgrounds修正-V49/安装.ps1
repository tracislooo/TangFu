$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$files = @(
    @{ Target = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Source = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Backup = '回退/game/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Before = 'c6b3dcacd3a66a4d1de4f4ee553efe0f55ccdd679e6aaddcffe96bf6d630bcab'; After = '6cfc78ae4b251ad20ef2e7334ad0acfe28be5d1a30b33af8adda3e0632c3c519' },
    @{ Target = 'G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Source = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Backup = '回退/skin/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'; Before = 'c6b3dcacd3a66a4d1de4f4ee553efe0f55ccdd679e6aaddcffe96bf6d630bcab'; After = '6cfc78ae4b251ad20ef2e7334ad0acfe28be5d1a30b33af8adda3e0632c3c519' },
    @{ Target = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\catalog.bin'; Source = 'catalog.bin'; Backup = '回退/game/catalog.bin'; Before = '45649f67110ac7a3b67af1cb26cbd6a65e22151ca5193d77931f47dbd8b326d6'; After = 'c99d840aa8bea9731327e510034202fa944679c1a872698a49d8b45bffaaa7f8' }
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
