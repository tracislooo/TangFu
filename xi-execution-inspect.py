import pathlib,sys,struct
R=pathlib.Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import pefile,capstone
root=pathlib.Path('F:/Steam/steamapps/common/Football Manager 27')
bin=(root/'GameAssembly.dll').read_bytes(); pe=pefile.PE(data=bin,fast_load=True);base=pe.OPTIONAL_HEADER.ImageBase
def off(va):return pe.get_offset_from_rva(va-base)
def va(o):return base+pe.get_rva_from_offset(o)
q=lambda o:struct.unpack_from('<Q',bin,o)[0]
b=(root/'fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
s=[struct.unpack_from('<III',b,8+i*12) for i in range(31)];u=lambda x,p:struct.unpack_from('<I',x,p)[0];h=lambda x,p:struct.unpack_from('<H',x,p)[0]
t=lambda j:b[s[2][0]+j:b.index(b'\0',s[2][0]+j)].decode(errors='replace')
asm=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
needle=b'SI.Core.dll\0'; st=bin.index(needle); idx=bin.index(struct.pack('<Q',va(st))); print('module',hex(idx),bin[idx:idx+40].hex()); table=off(q(idx+16))
def module(assembly,types):
 st=bin.index(assembly.encode()+b'\0');idx=bin.index(struct.pack('<Q',va(st)));table=off(q(idx+16));count=u(bin,idx+8)
 result={}
 for i in range(s[19][0],sum(s[19][:2]),76):
  x=b[i:i+76]; n=t(u(x,0))
  if n not in types:continue
  for j in range(u(x,24),u(x,24)+h(x,52)):
   row=b[s[5][0]+30*j:s[5][0]+30*j+30]; index=int.from_bytes(row[15:18],'little')
   # Method tokens are version dependent; match the known metadata token offset.
   tok=row.find(b'\x06',13,27)
   if tok<3:continue
   index=int.from_bytes(row[tok-3:tok],'little')
   if 0<index<=count:
    addr=q(table+8*(index-1)); result[addr]=n+'.'+t(u(row,0))
 return result

lookup=module('SI.VisualScripting.dll',{'BindNode','VisualRunner','VisualArgsBase'})
for addr,name in lookup.items():
 print(name,hex(addr))
 if 'BindNode.' in name and any(x in name for x in ['Execute','Bind','Initialize']):
  for ins in asm.disasm(bin[off(addr):off(addr)+2500],addr):
   print(ins.mnemonic,ins.op_str)
   if ins.mnemonic=='int3':break
