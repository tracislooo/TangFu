import ast,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
src=ast.parse((R/'add-start-screen-kunshan-overlay.py').read_text('utf8'))
for n in src.body:
 if isinstance(n,ast.FunctionDef) and n.name=='install':n.body=n.body[:-1]
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['running','install']],type_ignores=[]),'<installer>','exec'))
install(Path(sys.argv[1]),'--restore' in sys.argv)
print(json.dumps({'installed':'--restore' not in sys.argv,'restored':'--restore' in sys.argv}))
