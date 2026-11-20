$ErrorActionPreference='Stop'
$workspace='G:DocChatGPTNew project'
$status=Join-Path $workspace 'club-stadium-id-required-20261106status.txt'
'waiting-for-game-exit' | Set-Content -LiteralPath $status
while(Get-Process -Name fm -ErrorAction SilentlyContinue){Start-Sleep -Seconds 5}
try {
 & 'C:Users	raci.cachecodex-runtimescodex-primary-runtimedependenciespythonpython.exe' (Join-Path $workspace 'install-independent-resource-patch.py') (Join-Path $workspace 'club-stadium-native-name-20261106-094251') --restore
 if($LASTEXITCODE){throw 'Hash-protected rollback failed. No further actions.'}
 $p=Join-Path $workspace 'current-club-overview.json'
 $idx=Get-Content -LiteralPath $p -Raw | ConvertFrom-Json
 $idx.manifest=Join-Path $workspace 'club-stadium-context-fix-20261106-092602manifest.json'
 $idx.verification=$idx.manifest
 $idx.restore=Join-Path $workspace 'club-stadium-context-fix-20261106-092602estore.ps1'
 $idx.stadium_image_binding='selectedstadium.UniqueId -> tf27/stadium/id/<id>/background -> local JPG/PNG'
 $idx.runtime_verified=$false
 $idx | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $p -Encoding utf8
 'name-matching-removed-id-binding-restored-runtime-unresolved' | Set-Content -LiteralPath $status
} catch {
 ('failed: '+$_.Exception.Message) | Set-Content -LiteralPath $status
}
