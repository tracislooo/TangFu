$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetAA = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa'
$sourceAA = Join-Path $PSScriptRoot 'aa'
$recoveryAA = Join-Path $PSScriptRoot '回退/aa'
$globalTarget = Join-Path $targetAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
$catalogTarget = Join-Path $targetAA 'catalog.bin'
if ((Get-FileHash -LiteralPath $globalTarget -Algorithm SHA256).Hash.ToLower() -ne 'b7d00babf119fefd7da78d1c56714cf3d9b6a0044b250633b072a408a8c2300f') { throw 'Global version mismatch.' }
if ((Get-FileHash -LiteralPath $catalogTarget -Algorithm SHA256).Hash.ToLower() -ne 'f06e97609bdfb3063ce0d81581d8b2013ce9818c35ec63f5995994200d348650') { throw 'Catalog version mismatch.' }
try {
    Copy-Item -LiteralPath (Join-Path $sourceAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $sourceAA 'catalog.bin') -Destination $catalogTarget -Force
} catch {
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'catalog.bin') -Destination $catalogTarget -Force
    throw
}
Write-Host 'Complete.'
