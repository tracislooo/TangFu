from pathlib import Path
import json,hashlib,datetime,zipfile
from PIL import Image
R=Path.cwd();P=R/'CA180新版替换并核对引用-V57-20261027';F=P/'替换及引用校验记录.json';m=json.loads(F.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
installed=all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
m.update(installed=installed,installed_hash_verified=installed,protected_files_unchanged=True)
if installed:m['installed_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
cur=json.loads((R/'current-custom-textures.json').read_text('utf8'))
cur.update(version=57,date='2026-10-27',authoritative_source_bundle=str(P/'ui-backgrounds_assets_common.bundle'),source_bundle_sha256=sha((P/'ui-backgrounds_assets_common.bundle').read_bytes()),manifest=str(F))
t=next(t for t in cur['textures'] if t['name']=='CA180');t.update(texture_sha256=m['texture_sha256'],size=m['size'],decoded_alpha_range=m['decoded_alpha_range'])
assert len(cur['textures'])==173
(R/'current-custom-textures.json').write_text(json.dumps(cur,ensure_ascii=False,indent=2),'utf8');(P/'当前有效图片恢复来源.json').write_text(json.dumps(cur,ensure_ascii=False,indent=2),'utf8')
(P/'永久保留禁止复用ID.json').write_bytes((R/'reserved-texture-ids.json').read_bytes())
im=Image.open(P/'CA180成品解码预览.png').convert('RGBA');im.thumbnail((377,482));bg=Image.new('RGBA',im.size,'#909090');bg.alpha_composite(im);bg.convert('RGB').save(P/'透明显示检查.jpg')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in P.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(P))
with zipfile.ZipFile(P.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'installed':installed,'references':len(m['verified_references']),'other_resources_preserved':m['other_background_objects_unchanged'],'zip_bytes':P.with_suffix('.zip').stat().st_size}))
