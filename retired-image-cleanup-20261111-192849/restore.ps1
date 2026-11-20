$ErrorActionPreference='Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }
if ((Get-FileHash -LiteralPath 'G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle').Hash.ToLower() -ne '0bab66a1cf0d2cb08f12fa81a2ea4c97ad0419c9cc5063e845f53cd08c0cdd7f') { throw 'Later changes detected' }
Copy-Item -LiteralPath 'G:\Doc\ChatGPT\New project\retired-image-cleanup-20261111-192849\backup.bundle' -Destination 'G:\Doc\FM Skin Builder\skins\tf27-01\packages\ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle' -Force
