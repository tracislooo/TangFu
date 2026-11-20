import json
from pathlib import Path
for n in ['StyleStepperFromStepReached','StyleStepperFromDataCollection','StyleAndOverrideStepperFromDataCollection','StyleDefaultStepperFromStaticData']:
 d=json.loads(Path('FMskin/ui-visualfunctions_assets_all/'+n+'.json').read_text('utf8'));print(n,d['container'],[(x['m_name'],x['m_type']['m_typeString']) for x in d['type_tree']['m_inputs']])
