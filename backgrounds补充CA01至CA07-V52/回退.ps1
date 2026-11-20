$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '321b77fade2275e3381a2d6934473aae77b07ae09ec0f257815e284493edbbf7') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/ui-backgrounds_assets_common.bundle') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '6c79aa10c7bfc4bed2bb20c20379236363d5788a43a20a9fa72912885792db31') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
