$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '6d116e98c667cc9f992c69a06ac8a0531eddef566628e92710542929b08df28d') { throw 'Bundle version mismatch.' }
$sourceBundle = Join-Path $PSScriptRoot 'ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $sourceBundle -Algorithm SHA256).Hash.ToLower() -ne '332276569a9220bec17c72b86093dcb1cb31b769bb5c2ab299152fc2e033381d') { throw 'Source bundle hash mismatch.' }
Copy-Item -LiteralPath $sourceBundle -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '332276569a9220bec17c72b86093dcb1cb31b769bb5c2ab299152fc2e033381d') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
