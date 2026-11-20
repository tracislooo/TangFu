$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'ecdb6d81244a60ddfdec385210a3c960dcb7a218649222b22298694e16eefade') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
Write-Host 'Complete.'
