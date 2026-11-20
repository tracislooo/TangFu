exec(open('inspect-radar-relocation.py',encoding='utf8').read().split('dump(doc,objects')[0])
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects}
role=next(o for o in go.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='role_selector-large')
d=role.read_typetree();dump(d,go,'live-role-selector-tree.txt')
(R/'live-role-selector.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print('pid',role.path_id,'sheet',d['inlineSheet'])
for i in [1031,1049,1050,1051,1072,1087,1096,1097,1297,1184]:
 a=rr[i]['data'];sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 print(i,a.get('m_FullTypeName'),a.get('m_Classes'),json.dumps(sd,ensure_ascii=False))
