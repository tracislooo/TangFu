$ErrorActionPreference = 'Stop'
if ((Get-FileHash -LiteralPath 'F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle' -Algorithm SHA256).Hash.ToLower() -ne '6cfc78ae4b251ad20ef2e7334ad0acfe28be5d1a30b33af8adda3e0632c3c519') { throw 'Direct-background UI reference version mismatch.' }
if ((Get-FileHash -LiteralPath 'F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/catalog.bin' -Algorithm SHA256).Hash.ToLower() -ne 'c99d840aa8bea9731327e510034202fa944679c1a872698a49d8b45bffaaa7f8') { throw 'Direct-background catalog dependency version mismatch.' }
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$targetBundle = 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-backgrounds_assets_common.bundle'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'c2941b12696bbc8ff4048c2b0c39dde242c8f168428d70f4c8b42e15d1bd0a90') { throw 'Bundle version mismatch.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/ui-backgrounds_assets_common.bundle') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne 'b2bbb97be8da1f7e88a1c29df00cf131e3b545f70f64e4c3374dc05343662c63') { throw 'Installed bundle hash mismatch.' }
Write-Host 'Complete.'
