exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for o in objects.values():
 if o.type.name=='MonoBehaviour' and any(x in o.peek_name().lower() for x in ['playerdynamics','playerhappiness','reporthappiness','personaldynamics','playerpersonalinformation']):print(o.path_id,o.peek_name())
