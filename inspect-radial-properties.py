from pathlib import Path
import re
b=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
for w in sorted(set(re.findall(rb'[ -~]{5,}',b))):
 if (b'Gauge' in w and any(x in w.lower() for x in [b'width',b'segment',b'radial',b'track'])) or (b'--' in w and any(x in w.lower() for x in [b'width',b'inner',b'radius'])):print(w.decode())
