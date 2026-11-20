$ErrorActionPreference = 'Stop'
$src = 'K:/桌面'
$out = 'G:/Doc/ChatGPT/New project/头像居中修改'
$names = @(
 'report-player-banner-max-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7--4194025542157271532.json',
 'inlineStyle-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7-8045407476604796436.json',
 'PlayerReportHeader-CAB-1ab8e16d7264cd64aba00192bdf91ea2-5775949770471550939.json',
 'inlineStyle-CAB-1ab8e16d7264cd64aba00192bdf91ea2--1940069326759809061.json'
)
$docs = @($names | ForEach-Object { Get-Content -LiteralPath (Join-Path $src $_) -Raw | ConvertFrom-Json -AsHashtable })
$b,$bs,$h,$hs = $docs
function Copy-Object($obj) { return ($obj | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable) }
function Map-Refs($doc) { $map=@{}; foreach($r in $doc.references.RefIds){$map[[long]$r.rid]=$r}; return $map }
function Remap-Rids($obj,$map) {
 if($obj -is [System.Collections.IDictionary]) {
  foreach($key in @($obj.Keys)) { if($key -eq 'rid' -and $map.ContainsKey([long]$obj[$key])){$obj[$key]=$map[[long]$obj[$key]]} else {Remap-Rids $obj[$key] $map} }
 } elseif($obj -is [System.Collections.IList]) {foreach($item in $obj){Remap-Rids $item $map}}
}
$script:nextRid=2000
$script:nextId=2000000000
function Clone-Refs($sourceMap,$ids,$target) {
 $ridMap=@{}; foreach($id in $ids){$ridMap[[long]$id]=$script:nextRid; $script:nextRid++}
 foreach($id in $ids){
  $r=Copy-Object $sourceMap[[long]$id]; Remap-Rids $r $ridMap
  if($r.data.ContainsKey('m_Id')){
   $script:nextId++; $oldId=$r.data.m_Id; $r.data.m_Id=$script:nextId
   $serializedRid=$sourceMap[[long]$id].data.m_SerializedData.rid
   foreach($sid in $ids){if($sid -eq $serializedRid){$ridMap["assetId:$sid"]=$script:nextId}}
  }
  $target.references.RefIds += ,$r
 }
 $targetMap=Map-Refs $target
 foreach($sid in $ids){if($ridMap.ContainsKey("assetId:$sid")){$targetMap[[long]$ridMap[[long]$sid]].data.uxmlAssetId=$ridMap["assetId:$sid"]}}
 return $ridMap
}
function Set-Children($map,$parent,$children) {
 $map[[long]$parent].data.m_Children.Array=@($children | ForEach-Object {@{rid=[long]$_}})
 foreach($child in $children){$map[[long]$child].data.m_Parent.rid=[long]$parent}
}
function Add-Property($id,$type,$index) {
 return @{m_Id=$id;m_CustomName='';m_Line=-1;m_Values=@{Array=@(@{m_ValueType=$type;valueIndex=$index})}}
}
function Add-Rule($style,$properties) {
 $index=$style.m_Rules.Array.Count
 $style.m_Rules.Array += ,@{m_ComplexSelectors=@{Array=@()};m_Properties=@{Array=@($properties)};line=-1}
 return $index
}
function String-Index($style,$value) {
 $index=[array]::IndexOf($style.strings.Array,$value)
 if($index -lt 0){$index=$style.strings.Array.Count;$style.strings.Array += $value}
 return $index
}
function Dimension-Index($style,$value,$unit=1) {
 $index=$style.dimensions.Array.Count;$style.dimensions.Array += ,@{unit=$unit;value=[double]$value};return $index
}
$hm=Map-Refs $h
$portraitIds=@(1010,1014,1013,1018,1017,1022)
$portrait=Clone-Refs $hm $portraitIds $b
$b.m_Usings.Array += ,(Copy-Object ($h.m_Usings.Array | Where-Object alias -eq 'PersonPicture'))
$bm=Map-Refs $b
$frame=[long]$portrait[1010L]
$bm[$frame].data.m_Classes.Array=@('row-direction-normal','align-items-center','justify-content-center','align-self-center')
$zero=Dimension-Index $bs 0
$percent=Dimension-Index $bs 100 2
$center=String-Index $bs 'center'
$row=String-Index $bs 'row'
$start=String-Index $bs 'flex-start'
$end=String-Index $bs 'flex-end'
$hidden=String-Index $bs 'hidden'
$portraitWidth=Dimension-Index $bs 220
$portraitGap=Dimension-Index $bs 16
$frameRule=Add-Rule $bs @((Add-Property 262149 2 1),(Add-Property 131105 3 $portraitWidth),(Add-Property 131097 3 $portraitWidth),(Add-Property 131095 3 $portraitWidth),(Add-Property 131073 7 $center),(Add-Property 131074 7 $center),(Add-Property 131088 7 $center),(Add-Property 131091 3 $portraitGap),(Add-Property 131092 3 $portraitGap),(Add-Property 458768 7 $hidden))
$bm[$frame].data.m_RuleIndex=$frameRule
# Constrain the original template and its remapper to the reserved portrait width.
foreach($portraitChild in @([long]$portrait[1013L],[long]$portrait[1017L])){
 $bm[$portraitChild].data.m_RuleIndex=Add-Rule $bs @((Add-Property 131105 3 $percent),(Add-Property 131097 3 $zero),(Add-Property 131095 3 $portraitWidth),(Add-Property 131073 7 $center),(Add-Property 131088 7 $center))
}
# Equal flexible side panes keep the portrait on the banner's horizontal center.
$leftClone=Clone-Refs $bm @(1006,1011) $b
$bm=Map-Refs $b
$left=[long]$leftClone[1006L]
$bm[$left].data.m_Classes.Array=@('row-direction-normal','align-items-center')
$bm[[long]$leftClone[1011L]].data.name='CenteredPortraitLeftPane'
$paneProperties=@((Add-Property 262149 2 0),(Add-Property 131085 2 0),(Add-Property 131097 3 $zero),(Add-Property 131083 7 $row),(Add-Property 131073 7 $center),(Add-Property 131091 3 $zero),(Add-Property 131092 3 $zero),(Add-Property 131099 3 $zero),(Add-Property 131100 3 $zero),(Add-Property 458768 7 $hidden))
$bm[$left].data.m_RuleIndex=Add-Rule $bs ($paneProperties + (Add-Property 131088 7 $start))
$bm[1008L].data.m_RuleIndex=Add-Rule $bs ($paneProperties + (Add-Property 131088 7 $end))
$bm[1004L].data.m_RuleIndex=Add-Rule $bs @((Add-Property 131083 7 $row),(Add-Property 131073 7 $center),(Add-Property 131105 3 $percent),(Add-Property 131097 3 $zero),(Add-Property 131091 3 $zero),(Add-Property 131092 3 $zero),(Add-Property 131099 3 $zero),(Add-Property 131100 3 $zero))
# Let the existing information columns shrink inside their respective side pane.
foreach($section in @(1006,1007,1016,1018,1020,1022)){
 $oldIndex=$bm[[long]$section].data.m_RuleIndex
 $props=@();if($oldIndex -ge 0){$props=@($bs.m_Rules.Array[$oldIndex].m_Properties.Array | Where-Object {$_.m_Id -notin @(262149,131082,131084,131085,131097)})}
 $bm[[long]$section].data.m_RuleIndex=Add-Rule $bs ($props + @((Add-Property 262149 2 0),(Add-Property 131085 2 0),(Add-Property 131097 3 $zero),(Add-Property 458768 7 $hidden)))
}
Set-Children $bm $left @(1006,1007,1015,1016)
Set-Children $bm 1008 @(1017,1018,1019,1020,1021,1022)
Set-Children $bm 1004 @($left,$frame,1008)
# The user's revised request sets the original left portrait to zero width.
$hz=Dimension-Index $hs 0
$hp=Dimension-Index $hs 100 2
$hh=String-Index $hs 'hidden'
$hs.floats.Array += 1.0
$hg=$hs.floats.Array.Count-1
$hm[1010L].data.m_RuleIndex=Add-Rule $hs @((Add-Property 262149 2 0),(Add-Property 131105 3 $hz),(Add-Property 131097 3 $hz),(Add-Property 131095 3 $hz),(Add-Property 262150 3 $hz),(Add-Property 262151 3 $hz),(Add-Property 458768 7 $hh))
# Make the banner's width equal the full header width, with no left portrait offset.
foreach($ancestor in @(1002,1004,1006,1008,1011,1015,1019,1023,1027)){
 $oldIndex=$hm[[long]$ancestor].data.m_RuleIndex
 $props=@();if($oldIndex -ge 0){$props=@($hs.m_Rules.Array[$oldIndex].m_Properties.Array | Where-Object {$_.m_Id -notin @(262149,131105,131097,131091,131092,131099,131100)})}
 $props += @((Add-Property 131105 3 $hp),(Add-Property 131097 3 $hz),(Add-Property 131091 3 $hz),(Add-Property 131092 3 $hz),(Add-Property 131099 3 $hz),(Add-Property 131100 3 $hz))
 if($ancestor -eq 1011){$props += (Add-Property 131084 2 $hg);$props += (Add-Property 131082 3 $hz)}
 $hm[[long]$ancestor].data.m_RuleIndex=Add-Rule $hs $props
}
function Assert-Tree($doc,$style) {
 $map=Map-Refs $doc
 if($map.Count -ne $doc.references.RefIds.Count){throw 'Duplicate reference IDs'}
 $assetIds=@{}
 foreach($r in $doc.references.RefIds){$d=$r.data;if(!$d.ContainsKey('m_FullTypeName')){continue}
  if($assetIds.ContainsKey($d.m_Id)){throw 'Duplicate element IDs'};$assetIds[$d.m_Id]=$true
  foreach($child in $d.m_Children.Array){if(!$map.ContainsKey([long]$child.rid)){throw 'Missing child'};if($map[[long]$child.rid].data.m_Parent.rid -ne $r.rid){throw 'Parent mismatch'}}
  if($d.m_Parent.rid -ge 0 -and $r.rid -notin $map[[long]$d.m_Parent.rid].data.m_Children.Array.rid){throw 'Unlisted child'}
  if($d.m_RuleIndex -ge $style.m_Rules.Array.Count){throw 'Invalid style rule'}
  if($d.m_SerializedData.rid -ge 0 -and $map[[long]$d.m_SerializedData.rid].data.uxmlAssetId -ne $d.m_Id){throw 'Serialized element ID mismatch'}
 }
 foreach($rule in $style.m_Rules.Array){foreach($prop in $rule.m_Properties.Array){foreach($v in $prop.m_Values.Array){$arrayName=switch($v.m_ValueType){2{'floats'}3{'dimensions'}4{'colors'}7{'strings'}default{$null}};if($arrayName -and $v.valueIndex -ge $style[$arrayName].Array.Count){throw 'Style value index out of range'}}}}
}
Assert-Tree $b $bs
Assert-Tree $h $hs
$before=Get-Content -LiteralPath (Join-Path $src $names[0]) -Raw | ConvertFrom-Json -AsHashtable
foreach($r in $before.references.RefIds){if($r.rid -in @(1004,1006,1007,1008,1015,1016,1018,1020,1022)){continue};if(($r | ConvertTo-Json -Depth 100 -Compress) -cne ($bm[[long]$r.rid] | ConvertTo-Json -Depth 100 -Compress)){throw "Unexpected modification: $($r.rid)"}}
New-Item -ItemType Directory -Path $out -Force | Out-Null
for($i=0;$i -lt $docs.Count;$i++){
 $path=Join-Path $out $names[$i]
 [System.IO.File]::WriteAllText($path,($docs[$i] | ConvertTo-Json -Depth 100),[System.Text.UTF8Encoding]::new($false))
 $reloaded=Get-Content -LiteralPath $path -Raw | ConvertFrom-Json -AsHashtable
 if(($reloaded | ConvertTo-Json -Depth 100 -Compress) -cne ($docs[$i] | ConvertTo-Json -Depth 100 -Compress)){throw 'JSON round-trip changed data'}
}
'Verified all four JSON files, references, hierarchy, styles, serialization IDs, original content, and JSON round trips.'
$out
