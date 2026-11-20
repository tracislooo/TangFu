exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
LN='ui-tileslayouts_assets_all.bundle'
assert (GAME/LN).read_bytes()==(SKIN/LN).read_bytes()
e=UnityPy.load(str(GAME/LN));d=next(o for o in e.objects if o.path_id==3901662990989568885).read_typetree()
for c in d['m_gridComponents']:
 h=8 if c['m_elementID']=='PlayerAttributesBlock' else 2;y=0 if h==8 else 8
 assert c['m_location']['height']==c['m_minSize']['y']==c['m_maxSize']['y']==h
 assert c['m_location']['y']==y and all(cfg['Size']['y']==h for cfg in c['m_gridElementConfigs'])
assert max(c['m_location']['y']+c['m_location']['height'] for c in d['m_gridComponents'])==10
hd=objects[5775949770471550939].read_typetree();hr={r['rid']:r for r in hd['references']['RefIds']};hs=objects[hd['inlineSheet']['m_PathID']].read_typetree()
a=next(r for r in hr.values() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
assert 'buttons-button-primary-default' in a['data']['m_Classes']
assert not any(p['m_Id'] in [458752,262146] for p in hs['m_Rules'][a['data']['m_RuleIndex']]['m_Properties'])
g=next(hr[c['rid']] for c in a['data']['m_Children'] if hr[c['rid']]['data']['m_FullTypeName']=='SI.Bindable.SIGradient')
if g['data']['m_RuleIndex']>=0:
 assert not any(p['m_Id']==131081 for p in hs['m_Rules'][g['data']['m_RuleIndex']]['m_Properties'])
print(json.dumps({'installed_game_skin_identical':True,'primary_action_style_restored':True,'native_gradient_visible':True,'grid_height':10,'attribute_height':8,'bottom_height':2,'bottom_modules':len(d['m_gridComponents'])-1},indent=2))
