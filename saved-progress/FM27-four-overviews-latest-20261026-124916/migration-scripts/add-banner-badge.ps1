param([ValidateRange(-1,10000)][int]$ExternalIndex=-1,[ValidateSet('Below','LeftTest')][string]$Placement='Below')
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$out=Join-Path $root $(if($Placement -eq 'LeftTest'){'头像左侧图片测试'}else{'头像下方图片'})
$bannerName='report-player-banner-max-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7--4194025542157271532.json'
$styleName='inlineStyle-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7-8045407476604796436.json'
function Clone($v){return ($v | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable)}
function Prop($id,$type,$index){return @{m_Id=$id;m_CustomName='';m_Line=-1;m_Values=@{Array=@(@{m_ValueType=$type;valueIndex=$index})}}}
function AddString($s,$v){$i=[array]::IndexOf($s.strings.Array,$v);if($i -lt 0){$i=$s.strings.Array.Count;$s.strings.Array += $v};return $i}
function AddDim($s,$v){$i=$s.dimensions.Array.Count;$s.dimensions.Array += ,@{unit=1;value=[double]$v};return $i}
$b=Get-Content -LiteralPath (Join-Path $root $bannerName) -Raw | ConvertFrom-Json -AsHashtable
$s=Get-Content -LiteralPath (Join-Path $root $styleName) -Raw | ConvertFrom-Json -AsHashtable
$original=Clone $b
$map=@{};foreach($r in $b.references.RefIds){$map[[long]$r.rid]=$r}
$frame=$b.references.RefIds | Where-Object {$_.data.m_SerializedData -and $map[[long]$_.data.m_SerializedData.rid].data.name -eq 'PersonPictureFrame'}
if(@($frame).Count -ne 1){throw 'Expected one portrait frame'}
$node=Clone $map[1006L]
$serialized=Clone $map[1011L]
$rid=([long]($b.references.RefIds.rid | Measure-Object -Maximum).Maximum)+1
$id=([long]($b.references.RefIds.data.m_Id | Measure-Object -Maximum).Maximum)+1
if($id -gt [int]::MaxValue){throw 'Element ID out of range'}
$assetIndex=$s.assets.Array.Count
$fileId=if($ExternalIndex -lt 0){'待确认：Externals显示编号加1'}else{$ExternalIndex+1}
$s.assets.Array += ,@{m_FileID=$fileId;m_PathID=[long]98980767289610141}
$width=AddDim $s 180
$height=AddDim $s 40
$gap=AddDim $s 8
$zero=AddDim $s 0
$center=AddString $s 'center'
$column=AddString $s 'column'
$fit=AddString $s 'scale-to-fit'
$parentRid=$frame.rid
$rule=$s.m_Rules.Array.Count
$s.m_Rules.Array += ,@{line=-1;m_ComplexSelectors=@{Array=@()};m_Properties=@{Array=@(
 (Prop 458753 6 $assetIndex),(Prop 131105 3 $width),(Prop 131087 3 $height),
 (Prop 131097 3 $zero),(Prop 131085 2 1),(Prop 131093 3 $gap),
 (Prop 131074 7 $center),(Prop 262153 7 $fit)
)}}
if($Placement -eq 'LeftTest'){
 # Place a diagnostic image on the root's final drawing layer, outside flex flow.
 # The original centered portrait frame and its height remain untouched.
 $parentRid=1004L
 $half=$s.dimensions.Array.Count;$s.dimensions.Array += ,@{unit=2;value=50.0}
 $offset=AddDim $s 126
 $testHeight=AddDim $s 80
 $absolute=AddString $s 'absolute'
 $border=AddDim $s 2
 $borderColor=$s.colors.Array.Count;$s.colors.Array += ,@{r=0.0;g=1.0;b=1.0;a=1.0}
 $backColor=$s.colors.Array.Count;$s.colors.Array += ,@{r=0.08;g=0.08;b=0.08;a=1.0}
 $s.m_Rules.Array[$rule].m_Properties.Array=@(
  (Prop 458753 6 $assetIndex),(Prop 131105 3 $width),(Prop 131087 3 $testHeight),
  (Prop 131102 7 $absolute),(Prop 131103 3 $half),(Prop 131092 3 $offset),
  (Prop 131074 7 $center),(Prop 262153 7 $fit),
  (Prop 262148 3 $border),(Prop 262146 4 $borderColor),(Prop 458752 4 $backColor)
 )
}
$node.rid=$rid;$node.data.m_Id=[int]$id;$node.data.m_Parent.rid=$parentRid
$node.data.m_Children.Array=@();$node.data.m_RuleIndex=$rule
$node.data.m_Classes.Array=@();$node.data.m_SerializedData.rid=$rid+1
$serialized.rid=$rid+1;$serialized.data.uxmlAssetId=[int]$id
$serialized.data.name='PlayerAbilityBadge';$serialized.data.pickingMode=1;$serialized.data.pickingMode_UxmlAttributeFlags=1
$b.references.RefIds += @($node,$serialized)
if($Placement -eq 'LeftTest'){
 $map[1004L].data.m_Children.Array += ,@{rid=$rid}
}else{
 $frame.data.m_Children.Array += ,@{rid=$rid}
 $frame.data.m_Classes.Array=@($frame.data.m_Classes.Array | Where-Object {$_ -ne 'row-direction-normal'})
 $frameRule=$s.m_Rules.Array[$frame.data.m_RuleIndex]
 $frameRule.m_Properties.Array=@($frameRule.m_Properties.Array | Where-Object m_Id -ne 131083)
 $frameRule.m_Properties.Array += ,(Prop 131083 7 $column)
}
# Keep all existing information and avatar image bindings intact.
foreach($r in $original.references.RefIds){if(($Placement -eq 'Below' -and $r.rid -eq $frame.rid) -or ($Placement -eq 'LeftTest' -and $r.rid -eq 1004)){continue};if(($r | ConvertTo-Json -Depth 100 -Compress) -cne ($map[[long]$r.rid] | ConvertTo-Json -Depth 100 -Compress)){throw "Unexpected change: $($r.rid)"}}
$map=@{};foreach($r in $b.references.RefIds){if($map.ContainsKey([long]$r.rid)){throw 'Duplicate rid'};$map[[long]$r.rid]=$r}
foreach($r in $b.references.RefIds){if(!$r.data.ContainsKey('m_Id')){continue};foreach($c in $r.data.m_Children.Array){if($map[[long]$c.rid].data.m_Parent.rid -ne $r.rid){throw 'Parent mismatch'}};if($r.data.m_SerializedData.rid -ge 0 -and $map[[long]$r.data.m_SerializedData.rid].data.uxmlAssetId -ne $r.data.m_Id){throw 'Serialized ID mismatch'}}
if($s.assets.Array[$assetIndex].m_PathID -ne [long]98980767289610141){throw 'PathID lost precision'}
foreach($r in $s.m_Rules.Array){foreach($p in $r.m_Properties.Array){foreach($v in $p.m_Values.Array){$key=switch($v.m_ValueType){2{'floats'}3{'dimensions'}4{'colors'}6{'assets'}7{'strings'}default{$null}};if($key -and $v.valueIndex -ge $s[$key].Array.Count){throw 'Style index out of range'}}}}
New-Item -ItemType Directory -Path $out -Force | Out-Null
$bannerOutput=if($ExternalIndex -lt 0){$bannerName+'.template'}else{$bannerName}
$styleOutput=if($ExternalIndex -lt 0){$styleName+'.template'}else{$styleName}
foreach($pair in @(@($bannerOutput,$b),@($styleOutput,$s))){$path=Join-Path $out $pair[0];[System.IO.File]::WriteAllText($path,($pair[1] | ConvertTo-Json -Depth 100),[System.Text.UTF8Encoding]::new($false));$reload=Get-Content -LiteralPath $path -Raw | ConvertFrom-Json -AsHashtable;if(($reload | ConvertTo-Json -Depth 100 -Compress) -cne ($pair[1] | ConvertTo-Json -Depth 100 -Compress)){throw 'Round trip mismatch'}}
if($ExternalIndex -lt 0){'Prepared and verified layout and style templates. Externals index is required to create importable JSON.'}else{'Verified badge placement, texture reference, exact 64-bit PathID, hierarchy, untouched avatar and original information; m_FileID='+($ExternalIndex+1)}
