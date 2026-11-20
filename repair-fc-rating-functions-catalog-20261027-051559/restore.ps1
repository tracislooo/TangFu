$ErrorActionPreference = "Stop"
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\repair-fc-rating-functions-catalog-20261027-051559\backup-game\catalog.bin' -Destination 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\catalog.bin' -Force
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\repair-fc-rating-functions-catalog-20261027-051559\backup-game\catalog.hash' -Destination 'F:\Steam\steamapps\common\Project Taco\fm_Data\StreamingAssets\aa\catalog.hash' -Force
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\repair-fc-rating-functions-catalog-20261027-051559\backup-skin\catalog.bin' -Destination 'G:\Doc\FM Skin Builder\skins\tf27-01\packages\catalog.bin' -Force
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\repair-fc-rating-functions-catalog-20261027-051559\backup-skin\catalog.hash' -Destination 'G:\Doc\FM Skin Builder\skins\tf27-01\packages\catalog.hash' -Force