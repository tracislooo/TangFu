$ErrorActionPreference="Stop"
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }
$items=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot "manifest.json") | ConvertFrom-Json
foreach ($item in $items.files) { if ((Get-FileHash -LiteralPath $item.path -Algorithm SHA256).Hash.ToLower() -ne $item.installed_sha256) { throw "Current files changed; merge rollback instead of overwriting." } }
foreach ($item in $items.files) { Copy-Item -LiteralPath $item.backup -Destination $item.path -Force }