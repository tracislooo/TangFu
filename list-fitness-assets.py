exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for o in objects.values():
 if o.type.name=='MonoBehaviour' and any(s in o.peek_name().lower() for s in ['fitness','injury','medical','load','condition','fresh','sharp','fatigue','physic']):print(o.path_id,o.peek_name())
