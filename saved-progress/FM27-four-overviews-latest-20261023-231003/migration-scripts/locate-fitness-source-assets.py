exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for bundle in [WN,'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=env if bundle==WN else UnityPy.load(str(GAME/bundle))
 for o in e.objects:
  if o.type.name=='MonoBehaviour' and any(s in o.peek_name().lower() for s in ['sharpness','matchload','trainingload','fatigue']):print(bundle,o.path_id,o.peek_name())
