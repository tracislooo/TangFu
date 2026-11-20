from pathlib import Path
import re
b=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
ss=re.findall(rb'[ -~]{5,}',b)
for s in ss:
 if b'ContextMenu' in s and len(s)<200:print(s.decode())
