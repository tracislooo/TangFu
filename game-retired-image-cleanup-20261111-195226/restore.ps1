$ErrorActionPreference='Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }
if ((Get-FileHash -LiteralPath 'F:\Steam\steamapps\common\Football Manager 27\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle').Hash.ToLower() -ne 'f0c924e0936d0fc56308f6baf5e7049e05ba3e2c1bfbf629bf1dfb58dc57752f') { throw 'Later changes detected' }
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\game-retired-image-cleanup-20261111-195226\backup.bundle' -Destination 'F:\Steam\steamapps\common\Football Manager 27\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle' -Force
