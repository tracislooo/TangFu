$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '4a6ac770b50b6c6e08021a00799d5aec5ebc58b6b7a01e12a0d72e95cc0c2aac') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/ui-backgrounds_assets_common.bundle') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '5d66fcdd715cdf9803ec759535346a9ea0a04d4b525ea46392f91e3f97f23253') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
