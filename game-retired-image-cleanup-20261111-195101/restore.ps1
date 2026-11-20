$ErrorActionPreference='Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }
if ((Get-FileHash -LiteralPath 'F:\Steam\steamapps\common\Football Manager 27\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle').Hash.ToLower() -ne '71582a107e3338a0c2df0dc03dab9ffb03ea05d5ee89bc3668137ea037f7f651') { throw 'Later changes detected' }
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\game-retired-image-cleanup-20261111-195101\backup.bundle' -Destination 'F:\Steam\steamapps\common\Football Manager 27\fm_Data\StreamingAssets\aa\StandaloneWindows64\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle' -Force
