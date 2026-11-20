exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
src=UnityPy.load(str(R/'Action点击区域修正-20261016-003713'/WN));so={o.path_id:o for o in src.objects}
t=next(o for o in src.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerAttributesLargeBlock').read_typetree();tr={r['rid']:r for r in t['references']['RefIds']}
for r in tr.values():
 if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings':
  a=r;print('OLD MENU',json.dumps(r));print('OLD SD',json.dumps(tr[r['data']['m_SerializedData']['rid']]));print('OLD PARENT',json.dumps(tr[r['data']['m_Parent']['rid']]))
for r in rr.values():
 if 'QuickFlick' in r.get('data',{}).get('name',''):
  n=next(x for x in rr.values() if x.get('data',{}).get('m_SerializedData',{}).get('rid')==r['rid']);print('NAV',json.dumps(n));print('NAV SD',json.dumps(r))
