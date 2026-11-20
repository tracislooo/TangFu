$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetAA = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa'
$targetBundle = Join-Path $targetAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
$targetCatalog = Join-Path $targetAA 'catalog.bin'
if ((Get-FileHash -LiteralPath $targetBundle).Hash.ToLower() -ne 'c32aa52889f5585f6a3db3e365e48e4b507bcdae5538b82f71727219b330e56e') { throw 'Global version mismatch.' }
if ((Get-FileHash -LiteralPath $targetCatalog).Hash.ToLower() -ne '2e3f18ac71ab37ca726d85eaa96714c96c43f31ab30f7d0d73a96add886fd29e') { throw 'Catalog version mismatch.' }
try {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'aa/catalog.bin') -Destination $targetCatalog -Force
} catch {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/aa/catalog.bin') -Destination $targetCatalog -Force
 throw
}
Write-Host 'Complete.'
