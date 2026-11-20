from pathlib import Path
import struct,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import capstone
b=Path('F:/Steam/steamapps/common/Football Manager 27/GameAssembly.dll').read_bytes();pe=struct.unpack_from('<I',b,0x3c)[0];n=struct.unpack_from('<H',b,pe+6)[0];opt=pe+24;sz=struct.unpack_from('<H',b,pe+20)[0];base=struct.unpack_from('<Q',b,opt+24)[0]
secs=[]
for i in range(n):
 p=opt+sz+40*i;vs,va,rs,ro=struct.unpack_from('<4I',b,p+8);secs.append((va,max(vs,rs),ro,rs))
def va(off):
 for v,s,o,r in secs:
  if o<=off<o+r:return base+v+off-o
def off(addr):
 for v,s,o,r in secs:
  if base+v<=addr<base+v+s:return o+addr-base-v
def refs(addr):
 pat=struct.pack('<Q',addr);start=0;out=[]
 while True:
  p=b.find(pat,start)
  if p<0:break
  out.append(p);start=p+8
 return out
nameoff=b.find(b'SI.Bindable.dll\0');assert nameoff>=0
found=refs(va(nameoff));print('module_refs',[(hex(p),b[p:p+32].hex()) for p in found])
mod=next(p for p in found if 1000<struct.unpack_from('<I',b,p+8)[0]<100000 and off(struct.unpack_from('<Q',b,p+16)[0]) is not None)
cnt=struct.unpack_from('<I',b,mod+8)[0];ptr=off(struct.unpack_from('<Q',b,mod+16)[0]);md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
methods=next(x['methods'] for x in json.loads((R/'table-choice-metadata.json').read_text('utf8')) if x['name']=='SI.Bindable.StreamedTableViewSettingsCollection')
methods=next(x['methods'] for x in json.loads((R/'table-choice-metadata.json').read_text('utf8')) if x['name']=='SI.Bindable.StreamedTableView')
lines=[]
for name,idx,data in methods:
 if name not in ['Equals']:continue
 raw=bytes.fromhex(data);token=struct.unpack_from('<I',raw,18)[0];rid=token&0xffffff
 assert 0<rid<=cnt,(name,hex(token),cnt)
 addr=struct.unpack_from('<Q',b,ptr+8*(rid-1))[0];p=off(addr);lines.append('\n'+name+' '+hex(addr))
 if p is None:continue
 for ins in md.disasm(b[p:p+2400],addr):
  lines.append(hex(ins.address)+' '+ins.mnemonic+' '+ins.op_str)
  if ins.mnemonic=='ret':break
(R/'table-choice-native.txt').write_text('\n'.join(lines),'utf8');print(str(R/'table-choice-native.txt'))
lines=[]
for addr in [0x1817682d0,0x181767fe0]:
 lines.append('\nFUNC '+hex(addr));p=off(addr)
 for ins in md.disasm(b[p:p+1600],addr):
  lines.append(hex(ins.address)+' '+ins.mnemonic+' '+ins.op_str)
  if ins.mnemonic=='ret':break
(R/'table-choice-builtin.txt').write_text('\n'.join(lines),'utf8')
