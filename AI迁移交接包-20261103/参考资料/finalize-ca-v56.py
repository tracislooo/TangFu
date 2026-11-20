import sys,json,hashlib,zipfile,datetime
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from PIL import Image,ImageDraw
P=R/'五张CA替换并永久停用70张徽章-V56-20261027';M=P/'替换删除及引用校验记录.json';m=json.loads(M.read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
assert all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
assert all(sha(Path(r['source_png']).read_bytes())==r['source_png_sha256'] for r in m['replaced_textures'])
m.update(installed=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),installed_hash_verified=True,protected_files_unchanged=True)
M.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
current={'version':56,'date':'2026-10-27','authoritative_source_bundle':str(P/'ui-backgrounds_assets_common.bundle'),'source_bundle_sha256':sha((P/'ui-backgrounds_assets_common.bundle').read_bytes()),'manifest':str(M),'reserved_registry':str(R/'reserved-texture-ids.json'),'active_custom_texture_count':173,'textures':m['active_textures'],'restore_policy':'从本来源迁移173张有效纹理；永久排除reserved-texture-ids.json中的70张，不从旧包无筛选恢复243张。'}
(R/'current-custom-textures.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),'utf8');(P/'当前有效图片恢复来源.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),'utf8')
# Prevent legacy recovery entry points from restoring the retired IDs.
for n in ['restore-custom-backgrounds-v54.py','restore-custom-backgrounds-v55.py']:
 p=R/n;s=p.read_text('utf8')
 if 'Retired custom texture IDs cannot be restored' in s:continue
 lines=s.splitlines();index=next(i for i,line in enumerate(lines) if line.startswith('custom='))
 guard=["reserved_file=R/'reserved-texture-ids.json'","if reserved_file.exists():","    retired_ids={int(v['path_id']) for v in json.loads(reserved_file.read_text('utf8'))['reserved_textures']}","    assert not (custom & retired_ids), 'Retired custom texture IDs cannot be restored. Use current-custom-textures.json (173 active images).' "]
 lines[index+1:index+1]=guard;p.write_text('\n'.join(lines)+'\n','utf8')
# Render decoded output on a checkerboard to inspect alpha and orientation.
e=UnityPy.load(str(P/'ui-backgrounds_assets_common.bundle'));objects={o.path_id:o for o in e.objects}
preview=Image.new('RGB',(1200,345),'#242b33');draw=ImageDraw.Draw(preview)
for i,r in enumerate(m['replaced_textures']):
 tile=Image.new('RGBA',(220,290));d=ImageDraw.Draw(tile)
 for y in range(0,290,10):
  for x in range(0,220,10):d.rectangle((x,y,x+9,y+9),fill='#dddddd' if (x//10+y//10)%2 else '#aaaaaa')
 im=objects[int(r['path_id'])].read().image.convert('RGBA');im.thumbnail((220,290));tile.alpha_composite(im,((220-im.width)//2,(290-im.height)//2));preview.paste(tile.convert('RGB'),(10+i*240,38));draw.text((10+i*240,12),r['name'],fill='white')
preview.save(P/'五张新卡面包内解码预览.png')
with zipfile.ZipFile(P.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in P.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(P))
with zipfile.ZipFile(P.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'installed':True,'active_textures':173,'retired':70,'cleared_references':700,'ca_verified_references':55,'zip_bytes':P.with_suffix('.zip').stat().st_size,'preview':str(P/'五张新卡面包内解码预览.png')},ensure_ascii=False))
