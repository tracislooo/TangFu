$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager before replacing files.' }
$targetAA = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa'
$sourceAA = Join-Path $PSScriptRoot '回退/aa'
$recoveryAA = Join-Path $PSScriptRoot 'aa'
$catalogTarget = Join-Path $targetAA 'catalog.bin'
$globalTarget = Join-Path $targetAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
if ((Get-FileHash -LiteralPath $catalogTarget -Algorithm SHA256).Hash.ToLower() -ne '2695dae55be8874ce88eab0681a6c0244d1e1de158184632e64932a289774a93') { throw 'Catalog changed. Do not overwrite a different game version.' }
if ((Get-FileHash -LiteralPath $globalTarget -Algorithm SHA256).Hash.ToLower() -ne '7993605e9a90d046db93aec86c708c4e8cc1acecdbb86792dce33fb68c5373ea') { throw 'Global bundle changed. Please check the installed version.' }
if ((Get-FileHash -LiteralPath (Join-Path $targetAA 'StandaloneWindows64/ui-visualfunctions_assets_all.bundle') -Algorithm SHA256).Hash.ToLower() -ne '3aa259ab3b4621828cd4f74fd9ec387e971da80788912129ac5588e09fe3dc2d') { throw 'The visual functions bundle does not match the v34 recovery version.' }
try {
    Copy-Item -LiteralPath (Join-Path $sourceAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $sourceAA 'catalog.bin') -Destination $catalogTarget -Force
} catch {
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'catalog.bin') -Destination $catalogTarget -Force
    throw
}
Write-Host 'Complete. Start the game to verify.'
