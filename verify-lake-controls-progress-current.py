from pathlib import Path
import sys,json,hashlib,importlib.util,zlib
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R/'lake-controls-progress-repair-20261117-221018';m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
def exact(c,h):return all(abs(c[k]-v/255)<1e-6 for k,v in zip(['r','g','b'],bytes.fromhex(h))) and abs(c['a']-1)<1e-6
for tag in ['game','skin']:
 d=out/tag;expected={'--buttons-toggle-active-primary-surface':'078BC4','--buttons-toggle-active-primary-hover':'119DD5','--data-progress-indicator-foreground':'35C6E8'}
 oo={o.path_id:o for o in UnityPy.load(str(d/'ui-styles_assets_default.bundle')).objects};s=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
 for k,h in expected.items():
  ps=[p for r in s['m_Rules'] for p in r['m_Properties'] if p.get('m_CustomName')==k];assert ps
  for p in ps:assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4 and exact(s['colors'][p['m_Values'][0]['valueIndex']],h)
 oo={o.path_id:o for o in UnityPy.load(str(d/'ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle')).objects};t=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='DefaultMatchUI');rr={r['rid']:r for r in t['references']['RefIds']};n=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='playpause');s=oo[t['inlineSheet']['m_PathID']].read_typetree();p=next(p for p in s['m_Rules'][n['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458752);assert exact(s['colors'][p['m_Values'][0]['valueIndex']],'078BC4')
 c=cm.Catalog((d/'catalog.bin').read_bytes());assert (d/'catalog.hash').read_text()==hashlib.md5((d/'catalog.bin').read_bytes()).hexdigest()
 for rec in next(a for a in m['audits'] if a['variant']==tag)['catalog_crc_and_size']:
  data=(d/rec['bundle']).read_bytes();rd=EndianBinaryReader(data);b=object.__new__(BundleFile);b.signature=rd.read_string_to_null();b.version=rd.read_u_int();b.version_player=rd.read_string_to_null();b.version_engine=rd.read_string_to_null();_,block=b.read_fs(rd);assert zlib.crc32(block.bytes)==rec['crc'] and len(data)==rec['size']
 print(tag,'palette / playpause / catalog metadata checks passed')
(out/'verification.json').write_text(json.dumps({'palette_verified':True,'playpause_verified':True,'bundle_crc_and_size_verified':True,'runtime_verified':False},indent=2),'utf8')
