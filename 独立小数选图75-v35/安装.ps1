$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager before replacing files.' }
$targetAA = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa'
$sourceAA = Join-Path $PSScriptRoot 'aa'
$recoveryAA = Join-Path $PSScriptRoot '回退/aa'
$catalogTarget = Join-Path $targetAA 'catalog.bin'
$globalTarget = Join-Path $targetAA 'StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
if ((Get-FileHash -LiteralPath $catalogTarget -Algorithm SHA256).Hash.ToLower() -ne 'f06e97609bdfb3063ce0d81581d8b2013ce9818c35ec63f5995994200d348650') { throw 'Catalog changed. Do not overwrite a different game version.' }
if ((Get-FileHash -LiteralPath $globalTarget -Algorithm SHA256).Hash.ToLower() -ne 'b4f100d38693e3eee731823b3b22d43d63d5d7280d5b213b17fa6c6b9e76da0e') { throw 'Global bundle changed. Please check the installed version.' }
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
