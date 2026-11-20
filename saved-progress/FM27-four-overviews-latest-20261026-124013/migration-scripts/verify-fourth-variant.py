from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
out=Path('fourth-left-large-portrait-no-hidden-20261022-132051');game=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
o={x.path_id:x for x in UnityPy.load(str(game/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
d=o[-940000000012000].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
def sd(i):return r.get(r[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
names={i:sd(i).get('name','') for i in r if 'm_SerializedData' in r[i].get('data',{})}
assert not any(n=='RightHiddenAttributesPanel' for n in names.values())
assert not any(n=='FC_CardFrame' for n in names.values())
assert len([n for n in names.values() if n=='PersonPictureFrame'])==1
assert len([n for n in names.values() if n=='RightMiddleTacticalEffectiveness'])==1
assert len([n for n in names.values() if n=='OverviewTitledProsConsIcons'])==1
assert len([n for n in names.values() if n=='AttributeSpiderChart'])==1
host=o[7857044477279960178].read_typetree();hr={x['rid']:x for x in host['references']['RefIds']}
v=next(x['data'] for x in hr.values() if x.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
titles=[x['m_scopeValue']['m_serializedData'] for x in v['ValueVariables'] if x['m_name'].endswith('VariantTitle')]
assert len(titles)==4
assert 'String|左边版大头像+非隐藏|' in titles
base={x.path_id:x for x in UnityPy.load(str(out/'backup-game'/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
for i in [-930000000001001,-930000000001000,-930000000001003,-930000000001002,-940000000010000,-940000000010001]:assert o[i].get_raw_data()==base[i].get_raw_data()
print(json.dumps({'verified':True,'selector_versions':titles,'first_three_pages_unchanged':True,'fourth_contains_native_photo_status_feet_pros_cons_tactics':True},ensure_ascii=False))
