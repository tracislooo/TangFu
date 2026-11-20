$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '6ddf4680d9b6850dc59f43d2ba1f3ccbb35e0f8e3e922a3f7530a750839c007d') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ui-backgrounds_assets_common.bundle') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '5d66fcdd715cdf9803ec759535346a9ea0a04d4b525ea46392f91e3f97f23253') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
