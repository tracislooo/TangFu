from pathlib import Path
import ast
R=Path(__file__).resolve().parent
s=(R/'inspect-table-choice-native.py').read_text('utf8')
s=s[:s.index('methods=next')]
exec(compile(s,'native','exec'))
methods=next(x['methods'] for x in json.loads((R/'table-choice-metadata.json').read_text('utf8')) if x['name']=='SI.Bindable.StreamedTableViewSettingsCollection')
lines=[]
for name,idx,data in methods:
 if name not in ['OnEnable']:continue
 token=struct.unpack_from('<I',bytes.fromhex(data),18)[0];rid=token&0xffffff
 addr=struct.unpack_from('<Q',b,ptr+8*(rid-1))[0];p=off(addr);lines.append('\n'+name+' '+hex(addr))
 for ins in md.disasm(b[p:p+5000],addr):
  lines.append(hex(ins.address)+' '+ins.mnemonic+' '+ins.op_str)
  if ins.mnemonic=='ret':break
(R/'database-views-research/menu-native.txt').write_text('\n'.join(lines),'utf8')
print('\n'.join(lines))
