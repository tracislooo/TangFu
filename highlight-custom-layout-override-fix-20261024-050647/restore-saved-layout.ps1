$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager before restoring the saved match layout.' }
$targetPath = 'C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/MatchExperienceHumanGridComposition-Large'
if (Test-Path -LiteralPath $targetPath) {
    $backupPath = Join-Path $PSScriptRoot ('layout-before-restore-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
    Copy-Item -LiteralPath $targetPath -Destination $backupPath
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'MatchExperienceHumanGridComposition-Large') -Destination $targetPath -Force
Write-Output 'Saved custom match layout restored.'
