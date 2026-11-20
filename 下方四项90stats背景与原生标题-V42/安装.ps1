$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '35b106588ff194c6b48edf5163d7a994d3c5690b96dc5589a2c9df5c9ee9e8e7') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle') -Destination $targetBundle -Force
Write-Host 'Complete.'
