from pathlib import Path
import sys,struct
sys.path.insert(0,str(Path.cwd()/'.codex-deps'))
import capstone,pefile
root=Path('F:/Steam/steamapps/common/Project Taco')
b=(root/'fm_Data/il2cpp_data/il2cpp.usym').read_bytes();n=struct.unpack_from('<Q',b,8)[0];base=24+n*24
def sym(a):
 lo,hi=0,n
 while lo<hi:
  m=(lo+hi)//2
  if struct.unpack_from('<Q',b,24+m*24)[0]<=a:lo=m+1
  else:hi=m
 r=struct.unpack_from('<Q4I',b,24+(lo-1)*24);q=base+r[2]
 return b[q:b.find(b'\0',q)].decode().split('/')[-1]+':'+str(r[3])
p=pefile.PE(str(root/'GameAssembly.dll'),fast_load=True);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
for a,size in [(0x19164f0,0x1e0),(0x1916850,0x240)]:
 for i in cs.disasm(p.get_data(a,size),a):
  note=''
  if i.mnemonic=='call' and i.op_str.startswith('0x'):note=sym(int(i.op_str,16))
  print(hex(i.address),i.mnemonic,i.op_str,note)
