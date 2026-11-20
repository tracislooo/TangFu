$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetAA = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa'
$targetBundle = Join-Path $targetAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
$targetCatalog = Join-Path $targetAA 'catalog.bin'
if ((Get-FileHash -LiteralPath $targetBundle).Hash.ToLower() -ne '3c9e616f58f5471a6378d60077b1aa6e9cff0d970fe71170c67718022ad95ad4') { throw 'Global version mismatch.' }
if ((Get-FileHash -LiteralPath $targetCatalog).Hash.ToLower() -ne '32236b9b239de42a0561704dd4c49753c23c21ed0a40c4d7ce570175591c8c8a') { throw 'Catalog version mismatch.' }
try {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/aa/catalog.bin') -Destination $targetCatalog -Force
} catch {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'aa/catalog.bin') -Destination $targetCatalog -Force
 throw
}
Write-Host 'Complete.'
