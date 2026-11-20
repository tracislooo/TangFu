$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/center-avatar.ps1"
$pictureName='PersonPicture-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7--4696340654933359536.json'
$pictureStyleName='inlineStyle-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7-3569960969388672080.json'
$picture=Get-Content -LiteralPath (Join-Path $src $pictureName) -Raw | ConvertFrom-Json -AsHashtable
$pictureBefore=Copy-Object $picture
$pictureStyle=Get-Content -LiteralPath (Join-Path $src $pictureStyleName) -Raw | ConvertFrom-Json -AsHashtable
$styleBefore=Copy-Object $pictureStyle
$pictureMap=Map-Refs $picture
$fitIndex=String-Index $pictureStyle 'scale-to-fit'
$scaleIndex=$pictureStyle.floats.Array.Count
$pictureStyle.floats.Array += 0.95
$changedSerialized=@()
$changedRules=@()
foreach($node in $picture.references.RefIds){
 if($node.data.m_FullTypeName -ne 'SI.Bindable.SIImage'){continue}
 $ruleIndex=$node.data.m_RuleIndex
 $rule=$pictureStyle.m_Rules.Array[$ruleIndex]
 $fitProperty=$rule.m_Properties.Array | Where-Object m_Id -eq 262153
 if(!$fitProperty){throw 'Expected image scale mode style is missing'}
 $fitProperty.m_Values.Array=@(@{m_ValueType=7;valueIndex=$fitIndex})
 $scaleProperty=Add-Property 327681 2 $scaleIndex
 $scaleProperty.m_Values.Array += ,@{m_ValueType=2;valueIndex=$scaleIndex}
 $rule.m_Properties.Array += ,$scaleProperty
 $serializedRid=[long]$node.data.m_SerializedData.rid
 $data=$pictureMap[$serializedRid].data
 # Both the base Image and the custom SIImage now explicitly use ScaleToFit.
 $data.scaleMode=2
 $data.scaleMode_UxmlAttributeFlags=1
 $data.ScaleMode=2
 $data.ScaleMode_UxmlAttributeFlags=1
 $changedSerialized += $serializedRid
 $changedRules += $ruleIndex
}
if($changedSerialized.Count -ne 4){throw 'Expected four SIImage branches'}
foreach($r in $pictureBefore.references.RefIds){
 $actual=Copy-Object $pictureMap[[long]$r.rid]
 if($r.rid -in $changedSerialized){
  foreach($key in @('scaleMode','scaleMode_UxmlAttributeFlags','ScaleMode','ScaleMode_UxmlAttributeFlags')){$actual.data[$key]=$r.data[$key]}
 }
 if(($actual | ConvertTo-Json -Depth 100 -Compress) -cne ($r | ConvertTo-Json -Depth 100 -Compress)){throw "Unexpected template change: $($r.rid)"}
}
for($i=0;$i -lt $styleBefore.m_Rules.Array.Count;$i++){
 $actual=Copy-Object $pictureStyle.m_Rules.Array[$i]
 if($i -in $changedRules){
  $actual.m_Properties.Array=@($actual.m_Properties.Array | Where-Object m_Id -ne 327681)
  ($actual.m_Properties.Array | Where-Object m_Id -eq 262153).m_Values=Copy-Object (($styleBefore.m_Rules.Array[$i].m_Properties.Array | Where-Object m_Id -eq 262153).m_Values)
 }
 if(($actual | ConvertTo-Json -Depth 100 -Compress) -cne ($styleBefore.m_Rules.Array[$i] | ConvertTo-Json -Depth 100 -Compress)){throw "Unexpected style change: $i"}
}
foreach($i in $changedRules){
 $props=$pictureStyle.m_Rules.Array[$i].m_Properties.Array
 $fit=$props | Where-Object m_Id -eq 262153
 if($pictureStyle.strings.Array[$fit.m_Values.Array[0].valueIndex] -ne 'scale-to-fit'){throw 'Image still uses cropping'}
 $scale=$props | Where-Object m_Id -eq 327681
 if($scale.m_Values.Array.Count -ne 2){throw 'Expected two scale axes'}
 foreach($axis in $scale.m_Values.Array){if($pictureStyle.floats.Array[$axis.valueIndex] -ne 0.95){throw 'Incorrect image scale'}}
}
foreach($rule in $pictureStyle.m_Rules.Array){foreach($prop in $rule.m_Properties.Array){foreach($v in $prop.m_Values.Array){
 $arrayName=switch($v.m_ValueType){2{'floats'}3{'dimensions'}4{'colors'}7{'strings'}default{$null}}
 if($arrayName -and ($v.valueIndex -lt 0 -or $v.valueIndex -ge $pictureStyle[$arrayName].Array.Count)){throw 'Invalid image style index'}
}}}
foreach($pair in @(@($pictureName,$picture),@($pictureStyleName,$pictureStyle))){
 $path=Join-Path $out $pair[0]
 [System.IO.File]::WriteAllText($path,($pair[1] | ConvertTo-Json -Depth 100),[System.Text.UTF8Encoding]::new($false))
 $loaded=Get-Content -LiteralPath $path -Raw | ConvertFrom-Json -AsHashtable
 if(($loaded | ConvertTo-Json -Depth 100 -Compress) -cne ($pair[1] | ConvertTo-Json -Depth 100 -Compress)){throw 'Picture JSON round-trip changed data'}
}
Compress-Archive -LiteralPath (Get-ChildItem -LiteralPath $out -File).FullName -DestinationPath "$out.zip" -Force
'Verified four actual image nodes use ScaleToFit and 95% scale. Containers, picture bindings and unrelated styles are unchanged. Package now includes six JSON files.'
