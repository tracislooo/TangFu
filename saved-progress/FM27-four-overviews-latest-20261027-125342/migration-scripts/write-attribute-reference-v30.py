import hashlib,json
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project')
rows=[
('技术','传球',13,'Passing'),('技术','传中',12,'Crossing'),('技术','盯人',9,'Marking'),
('技术','技术',13,'Technique'),('技术','盘带',15,'Dribbling'),('技术','抢断',15,'Tackling'),
('技术','射门',8,'Finishing'),('技术','停球',13,'FirstTouch'),('技术','头球',11,'Heading'),('技术','远射',6,'LongShots'),
('定位球','罚点球',6,'PenaltyTaking'),('定位球','角球',8,'Corners'),('定位球','界外球',11,'LongThrows'),('定位球','任意球',5,'FreeKicks'),
('精神','才华',14,'Flair'),('精神','防守站位',11,'Positioning'),('精神','工作投入',15,'WorkRate'),
('精神','集中',14,'Concentration'),('精神','决断',13,'Decisions'),('精神','领导力',8,'Leadership'),
('精神','侵略性',14,'Aggression'),('精神','视野',14,'Vision'),('精神','团队合作',12,'Teamwork'),
('精神','无球跑动',14,'Movement'),('精神','意志力',14,'Determination'),('精神','勇敢',14,'Bravery'),
('精神','预判',12,'Anticipation'),('精神','镇定',13,'Composure'),
('身体','爆发力',15,'Acceleration'),('身体','弹跳',13,'JumpingReach'),('身体','灵活',14,'Agility'),
('身体','耐力',14,'Stamina'),('身体','平衡',11,'Balance'),('身体','强壮',11,'Strength'),
('身体','速度',16,'Pace'),('身体','体质',17,'NaturalFitness')]
goalkeeper=[('制空能力','AerialReach'),('指挥防守','CommandOfArea'),('沟通','Communication'),
    ('神经指数','Eccentricity'),('手控球','Handling'),('大脚开球','Kicking'),
    ('一对一','OneOnOnes'),('反应','Reflexes'),('出击倾向','RushingOut'),
    ('击球倾向','TendencyToPunch'),('手抛球','Throwing')]
gk_evidence=json.loads((R/'门将及左右脚原生调用证据-V30.json').read_text(encoding='utf-8'))
native_gk_paths={path.lower() for col in gk_evidence['goalkeeper_columns'] for path in col['paths']}
for cn,en in goalkeeper:
    assert 'binding.attribute'+en.lower() in native_gk_paths,en
feet=[('左脚数值','person.Footedness.LeftFootedness','数字'),
    ('右脚数值','person.Footedness.RightFootedness','数字'),
    ('左脚描述','person.Footedness.LeftFootednessString','本地化文字'),
    ('右脚描述','person.Footedness.RightFootednessString','本地化文字')]
native_foot_paths=set(next(x for x in gk_evidence['foot_ui'] if x['name']=='FootednessTile_4x2')['paths'])
for cn,path,kind in feet:
    field=path.split('.')[-1]
    assert field in gk_evidence['foot_registered_keys'],field
    if kind=='本地化文字':assert path.replace('person.','Player.',1) in native_foot_paths
hidden=[
('适应性','hidden-adaptability','AttributeAdaptability'),
('野心','hidden-ambition','AttributeAmbition'),
('发挥稳定性','hidden-consistency','Consistency'),
('争议性','hidden-controversy','AttributeControversy'),
('肮脏程度','hidden-dirtiness','Dirtiness'),
('大赛表现','hidden-important-matches','ImportantMatches'),
('受伤倾向','hidden-injury-proneness','InjuryProneness'),
('忠诚','hidden-loyalty','AttributeLoyalty'),
('抗压能力','hidden-pressure','AttributePressure'),
('职业素养','hidden-professionalism','AttributeProfessionalism'),
('体育精神','hidden-sportsmanship','AttributeSportsmanship'),
('自制力／脾气（Temperament）','hidden-temperament','AttributeTemperament'),
('多面性','hidden-versatility','Versatility')]
hidden_evidence=json.loads((R/'隐藏属性原生调用证据-V30.json').read_text(encoding='utf-8'))
native_player_rows={x['id']:x for x in next(x for x in hidden_evidence if x['name']=='PlayerTableFactory')['rows']}
for cn,column,field in hidden:
    assert 'binding.'+field+'.PropertyValue' in native_player_rows[column]['paths'],field
related=[('当前能力（CA）','person.PlayerCurrentAbility'),('潜在能力（PA）','person.PlayerPotentialAbility'),
    ('当前声望','person.PlayerCurrentReputation'),('本土声望','person.PlayerHomeReputation'),('世界声望','person.PlayerWorldReputation')]
keys=json.loads((R/'attribute-key-names-v30.json').read_text(encoding='utf-8'))
assert len(rows)==36
for category,cn,value,en in rows:assert 'Attribute'+en in keys,en
for cn,en in goalkeeper:assert 'Attribute'+en in keys,en
header='| 分类 | 属性 | 截图值 | 数字调用路径 |\n|---|---|---:|---|\n'
table=header+'\n'.join(f'| {category} | {cn} | {value} | `person.Attribute{en}.PropertyValue` |' for category,cn,value,en in rows)
table+='\n'+'\n'.join(f'| 门将专用 | {cn} | 未提供 | `person.Attribute{en}.PropertyValue` |' for cn,en in goalkeeper)
table+='\n'+'\n'.join(f'| 隐藏 | {cn} | 未提供 | `person.{field}.PropertyValue` |' for cn,column,field in hidden)
other='''
| 其他项目 | 截图显示 | 调用路径 |
|---|---|---|
| 守门能力 | 3/10 | `person.GoalkeepingRating` |
| 左脚数值 | 截图未直接给出数字 | `person.Footedness.LeftFootedness` |
| 右脚数值 | 截图未直接给出数字 | `person.Footedness.RightFootedness` |
| 左脚描述 | 不善 | `person.Footedness.LeftFootednessString` |
| 右脚描述 | 精准 | `person.Footedness.RightFootednessString` |
| 是否门将 | 布尔值 | `person.IsGoalkeeper` |

左右脚数值直接使用以上字段，不追加 .PropertyValue。
左右脚文字描述可以直接调用带 String 的字段，原生 FootednessTile_4x2 正在使用这两个字段。
此前“需要另外映射”的说明已修正。
门将共用的传球、停球、技术、精神、身体及隐藏属性，继续使用上表相同的数字路径。
'''
other+='\n| 相关隐藏数值 | report-max 调用路径 |\n|---|---|\n'+'\n'.join(f'| {cn} | `{path}` |' for cn,path in related)+'\n'
text='''# 球员属性数字调用对照（V30）

已将游戏目录的 global bundle 回退到 V30，并核对与 V30 成品 SHA256 相同。
当前 catalog.bin 是修改前版本；V35 尚未安装，所以无需再回退目录文件。
视觉函数包保留 v34 恢复的兼容原始函数内容。

以下数字来自用户截图，不是从存档直接读取。
本表准确适用范围：当前 V30 的 report-player-banner-max。
已读取游戏目录实际安装的资源：根 BindingExpect/UxmlSerializedData，rid 1003，
Parameters 定义 name=person、type.id=1145176065；另一个根参数是 localteam。
该面板没有声明 player 或 Player 参数，也没有把人物重新映射为这两个名字。
因此在这个面板中使用小写 person，不能把 person、player、Player 任意互换。
例如当前能力也是 `person.PlayerCurrentAbility`；后面的 PlayerCurrentAbility 是字段名。

`person.AttributePassing` 是属性对象；`.PropertyValue` 才是用于显示及整数运算的值。
此结构来自原生 AddSetPieceTakerDropdownRow 与 ColouredAttributeCell。
36 个 Attribute 字段名均已在当前 FM27 注册键表中核对；尚未在报告头逐条运行验证。
新增13项隐藏属性已逐条核对当前游戏 PlayerTableFactory 的原生数字路径。
新增11项门将专用属性，已逐条核对同一原生表中的属性对象路径，数字取 PropertyValue。
左右脚数值及描述字段已核对原生 FootednessTile_4x2 和当前字段注册表。
该表原生前缀为 binding，在 report-max 上使用已声明的 person；字段后缀按原文件保留。
截图没有隐藏属性数字，表中的“未提供”不代表0。

'''+table+'\n'+other+'''
## 相加和平均值

多个属性相加：游戏已有原生函数 `BindMultipleIntArgsAsSumToDestination`。
GUID：`a82e4cf3a34b1ae41b85cacd4f63208c`。
输入为多个 BindingPath 的列表，目标为 IBindingSetter；先写到临时数字绑定，再让 SIText 显示它。
因此不能把加号直接写进 `person.AttributePassing.PropertyValue` 调用路径里。
可直接使用当前函数包里的现成函数，无需修改函数包或新增目录记录。
这是根据原生函数结构确认的能力，尚未在自定义报告数字上运行验证。

例：传球13 + 视野14 + 技术13 = 40。
原生函数接收的三条数字路径为：
`person.AttributePassing.PropertyValue`、`person.AttributeVision.PropertyValue`、`person.AttributeTechnique.PropertyValue`。

任意组合平均值：求和后还要除以属性数量。
上述例子为40/3=13.333…，可约定显示13.33或四舍五入为13。
当前包内未发现直接处理任意属性组合平均值的现成 VisualFunction，需要额外的除法/格式化计算绑定。
仅把路径写成“(A+B+C)/3”不会执行数学运算；不应把未验证的自定义平均值说成现成可调用字段。

游戏原生球员对比页已有按分类计算的平均值：

| 分类 | 原生对比页平均值路径 |
|---|---|
| 技术 | `selectedleftplayer.AttributesComparisonTechnical.AttributeCategoryAverage` |
| 精神 | `selectedleftplayer.AttributesComparisonMental.AttributeCategoryAverage` |
| 身体 | `selectedleftplayer.AttributesComparisonPhysical.AttributeCategoryAverage` |
| 定位球 | `selectedleftplayer.AttributesComparisonSetPieces.AttributeCategoryAverage` |
| 门将 | `selectedleftplayer.AttributesComparisonGoalkeeping.AttributeCategoryAverage` |

这些路径来自 OnThePitchComparisonAttributesTab，`selectedleftplayer` 是该页绑定的球员。
它们属于游戏预设分类，不是任意选取两三项的平均；移到报告页使用仍需确认对应上下文。

## 核对来源

- 当前游戏 gameworld bundle：AddSetPieceTakerDropdownRow，PathID -224993782040584907。
- 当前游戏 gameworld bundle：ColouredAttributeCell；绑定数字为 binding.PropertyValue。
- 当前游戏 gameworld bundle：OnThePitchComparisonAttributesTab，PathID -1697797029161685654。
- 当前游戏 visualfunctions bundle：BindMultipleIntArgsAsSumToDestination，PathID 6543242224448985636。
- 当前游戏 global-metadata.dat：Attribute 字段注册键。
- 当前游戏 tablefactories bundle：PlayerTableFactory，PathID -6813643292728705340，原生hidden列数字路径。
- 当前游戏 gameworld bundle：FootednessTile_4x2，PathID -4339960523675953800，左右脚数值与文字绑定。
'''
p=R/'球员属性调用对照-V30.md';p.write_text(text,encoding='utf-8')
(R/'球员属性调用对照-V30.json').write_text(json.dumps({'scope':'V30 report-player-banner-max','root_binding':'person','root_binding_reference_type_id':1145176065,'root_binding_serialized_rid':1003,'attributes':[{'category':c,'name':n,'screenshot_value':v,'path':f'person.Attribute{e}.PropertyValue'} for c,n,v,e in rows],
    'hidden_attributes':[{'category':'隐藏','name':cn,'path':f'person.{field}.PropertyValue','native_source_column':col,'source_verified':True,'report_runtime_verified':False} for cn,col,field in hidden],
    'goalkeeper_attributes':[{'category':'门将专用','name':cn,'path':f'person.Attribute{en}.PropertyValue','native_source':'PlayerTableFactory','source_verified':True,'report_runtime_verified':False} for cn,en in goalkeeper],
    'footedness':[{'name':cn,'path':path,'value_kind':kind,'native_source':'FootednessTile_4x2'} for cn,path,kind in feet],
    'related_hidden_values':[{'name':cn,'path':path} for cn,path in related]},ensure_ascii=False,indent=2),encoding='utf-8')
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
global_name='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
assert (AA/'StandaloneWindows64'/global_name).read_bytes()==(R/'右侧四项联赛统计Actions右下-v30'/global_name).read_bytes()
record={'global_version':'v30','global_sha256':hashlib.sha256((AA/'StandaloneWindows64'/global_name).read_bytes()).hexdigest(),
    'catalog_sha256':hashlib.sha256((AA/'catalog.bin').read_bytes()).hexdigest(),'attribute_fields_checked':36,
    'changes_this_turn':'Restore global to v30; create reference tables only; no new UI arithmetic added.'}
(R/'回退V30前备份-20261014/回退确认.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=True));print(str(p).encode('unicode_escape').decode())
