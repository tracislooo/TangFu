$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetAA = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa'
$sourceAA = Join-Path $PSScriptRoot '回退/aa'
$recoveryAA = Join-Path $PSScriptRoot 'aa'
$globalTarget = Join-Path $targetAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
$catalogTarget = Join-Path $targetAA 'catalog.bin'
if ((Get-FileHash -LiteralPath $globalTarget -Algorithm SHA256).Hash.ToLower() -ne '13e650735b42e6e1c6f35457c347f73677f6a61cbbc263cc537b5be46f5c1543') { throw 'Global version mismatch.' }
if ((Get-FileHash -LiteralPath $catalogTarget -Algorithm SHA256).Hash.ToLower() -ne '2e3f18ac71ab37ca726d85eaa96714c96c43f31ab30f7d0d73a96add886fd29e') { throw 'Catalog version mismatch.' }
try {
    Copy-Item -LiteralPath (Join-Path $sourceAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $sourceAA 'catalog.bin') -Destination $catalogTarget -Force
} catch {
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'catalog.bin') -Destination $catalogTarget -Force
    throw
}
Write-Host 'Complete.'
