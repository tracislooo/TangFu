from pathlib import Path
s=Path('fix-tactics-card-frame-and-star-visibility.py').read_text('utf8').split('for folder, tag in ')[0];exec(s)
doc=Doc(W,name='TacticsPositionCombined')
for nm in ['PitchFitnessPercent7','DirectTacticsRatingEquals7']:
 node=doc.named(nm); z=doc.data(node);print(nm,z.get('Binding'))
fun=UnityPy.load(str(GAME/'ui-visualfunctions_assets_all.bundle'))
for o in fun.objects:
 if o.path_id==-2619757750584433222:
  d=o.read_typetree();print(json.dumps(d,ensure_ascii=False)[:16000])
