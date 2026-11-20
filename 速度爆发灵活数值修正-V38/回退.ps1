$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'c32aa52889f5585f6a3db3e365e48e4b507bcdae5538b82f71727219b330e56e') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
Write-Host 'Complete.'
