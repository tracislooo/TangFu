from pathlib import Path
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','inspect-role-bool-style-');exec(s)
import ast
src=ast.parse(Path('combine-tactics-condition-sharpness.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['decode','encode']],type_ignores=[]),'codec','exec'))
d=Doc(W,name='TacticalPlannerCollapsablePitchesSingle');print(d.data(1005));print(decode(d.data(1005)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']))
