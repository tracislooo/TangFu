$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '5b2f7ecab64856086864ce6ddabc9111924b3d41c35af9008c9109147011f3fe') { throw 'Bundle version mismatch.' }
$sourceBundle = Join-Path $PSScriptRoot '回退/ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $sourceBundle -Algorithm SHA256).Hash.ToLower() -ne 'bd0b3ce77e5694bfad20e0a483380995a4df3121ebdd96970811f7fb8218aa3e') { throw 'Source bundle hash mismatch.' }
Copy-Item -LiteralPath $sourceBundle -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'bd0b3ce77e5694bfad20e0a483380995a4df3121ebdd96970811f7fb8218aa3e') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
