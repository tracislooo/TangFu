$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'd90e0dd98de8c85a5e2208a8a3a4ff82acef81b4e6a8d7c8ec79a93cda54e60c') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/ui-backgrounds_assets_common.bundle') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'c0704d073155911b7ad7221e0660438638446fbc2dd6a2c1bbd3c95a81bf42e7') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
