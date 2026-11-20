"""Fit all current player overview radars within their existing layout slots."""
import ast
import copy
import datetime
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

import importlib.util

R = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('overview_radars', R/'inspect-current-overview-radars.py')
inspection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspection)
UnityPy, W, L = inspection.UnityPy, inspection.W, inspection.L
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = inspection.POOLS
for file, names in [('build-fc-player-hover-layout.py', {'write', 'Styles'}),
                    ('add-card-six-ratings.py', {'validate_ui'})]:
    module = ast.parse((R/file).read_text('utf8'))
    selected = [n for n in module.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(ast.Module(body=selected, type_ignores=[]), file, 'exec'))
TypeTreeHelper.write_value = write

AUTO = {'m_ValueType':1,'valueIndex':2}
sha = lambda b: hashlib.sha256(b).hexdigest()


def fit(doc, sheet, fallback):
    refs = {r['rid']:r.get('data', {}) for r in doc['references']['RefIds']}
    sty = Styles(sheet)
    charts = inspection.geometry(doc, sheet)
    touched, serialized, details = set(), set(), []

    def edit(i, properties):
        sty.edit(refs[i], [sty.p(k,v) for k,v in properties.items()])
        touched.add(i)

    def name(i):
        return refs.get(refs[i].get('m_SerializedData', {}).get('rid'), {}).get('name', '')

    for entry in charts:
        i = entry['chart']['rid']
        sid = refs[i]['m_SerializedData']['rid']
        parent = entry['ancestors'][0]
        season = name(i) == 'SeasonSelectedSixAxisRadar'
        radius, distance = (25, 4) if fallback else (24, 4)
        if not fallback and not season:
            height = parent['style']['height'][0]['value']
            assert height in [200, 249]
            radius = 26 if height == 249 else 22
            if height == 249:
                # Keep the original left anchor, but cap the slot at the actual
                # right edge and allow vertical room above and below the plot.
                width = parent['style']['width'][0]
                box = {131103:sty.px(2), 131105:AUTO, 131104:sty.px(4),
                       131087:sty.px(240), 131096:sty.px(240), 131094:sty.px(240)}
                if width['unit'] == 1:
                    box[131095] = sty.px(width['value'])
                edit(parent['rid'], box)
                edit(i, {131087:sty.px(240), 131096:sty.px(240),
                         131094:sty.px(240), 131082:sty.px(240)})
        if season:
            switch = next(a for a in entry['ancestors'] if a['name']=='WorkingSeasonRadarGoalkeeperSwitch')
            half_height = switch['style']['height'][0]['unit'] == 2
            radius, distance = (18 if half_height else 23), 4
            branch = next(a['rid'] for a in entry['ancestors'] if a['name']=='SeasonRadarNumericValues')
            overlay, = [c['rid'] for c in refs[branch]['m_Children'] if name(c['rid'])=='SeasonRadarDirectAxisLabels']
            edit(overlay, {131089:sty.px(0), 131104:sty.px(0), 131103:sty.px(0), 131080:sty.px(0),
                           131105:AUTO, 131087:AUTO, 131096:sty.px(0), 131094:{'m_ValueType':1,'valueIndex':3}})
            side_inset = 16 if half_height else 23
            boxes = [(34,32,False,None), (68,30,False,side_inset), (68,30,True,side_inset),
                     (34,32,True,None), (2,30,True,side_inset), (2,30,False,side_inset)]
            labels = refs[overlay]['m_Children']
            assert len(labels) == len(boxes) == 6
            for child,(left,width,bottom,inset) in zip(labels,boxes):
                assert name(child['rid']).startswith('AxisLabel_')
                anchor = sty.px(2) if inset is None else sty.pct(inset)
                edit(child['rid'], {131089:sty.pct(left), 131105:sty.pct(width),
                                   131104:AUTO if bottom else anchor, 131080:anchor if bottom else AUTO})
                # Existing labels are two 14px rows. Check minimum supported chart
                # height, and keep all boxes strictly inside the overlay.
            for h in ([84, 100, 125] if half_height else [200, 249]):
                rectangles = []
                for left,width,bottom,inset in boxes:
                    gap = 2 if inset is None else h * inset / 100
                    y = h-gap-28 if bottom else gap
                    assert 0 <= y and y+28 <= h and 0 < left < left+width < 100
                    rectangles.append((left,left+width,y,y+28))
                for j,(x0,x1,y0,y1) in enumerate(rectangles):
                    assert all(x1<=a or x0>=b or y1<=c or y0>=d for a,b,c,d in rectangles[:j])
        refs[sid].update(SpiderChartRadiusPercentage=float(radius), LabelDistanceFromChart=float(distance),
                         SpiderChartRadiusPercentage_UxmlAttributeFlags=1, LabelDistanceFromChart_UxmlAttributeFlags=1)
        serialized.add(sid)
        details.append(dict(rid=i, season=season, radius_percent=radius, label_distance=distance))
    return details, touched, serialized


def main():
    loc = json.loads((R/'current-game-location.json').read_text('utf8'))
    roots = [('game',Path(loc['bundle_root'])), ('skin',Path(loc['skin_packages']))]
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
    out = R/('player-overview-radar-fit-'+stamp)
    out.mkdir()
    protected, tx, audit = {}, [], []
    for tag, root in roots:
        catdir = root.parent if tag=='game' else root
        for p in [root/L, catdir/'catalog.bin', catdir/'catalog.hash']:
            protected[str(p)] = sha(p.read_bytes())
        target = root/W
        before = target.read_bytes()
        _, pages, docs = inspection.discover(root)
        active = {p['ident'] for p in pages if p['ident'].startswith('PlayerOverview')}
        assert len(active) >= 9 and all(bn==W for bn, _ in docs)
        assert {p['pid'] for p in pages if p['ident'] in active} <= {pid for _,pid in docs}
        env = UnityPy.load(before)
        objects = {o.path_id:o for o in env.objects}
        hashes = {pid:sha(o.get_raw_data()) for pid,o in objects.items()}
        changes, page_checks = {}, []
        fallback = {p['pid'] for p in pages if p['ident']=='PlayerAttributesBlock'}
        for _, pid in sorted(docs):
            doc = objects[pid].read_typetree()
            assert doc == docs[W,pid]
            old = copy.deepcopy(doc)
            sid = doc['inlineSheet']['m_PathID']
            sheet = objects[sid].read_typetree()
            prior_sheet = copy.deepcopy(sheet)
            details, touched, chart_data = fit(doc,sheet,pid in fallback)
            allowed_fields = {'SpiderChartRadiusPercentage','LabelDistanceFromChart',
                              'SpiderChartRadiusPercentage_UxmlAttributeFlags','LabelDistanceFromChart_UxmlAttributeFlags'}
            for a,b in zip(doc['references']['RefIds'],old['references']['RefIds'],strict=True):
                assert a['rid']==b['rid']
                if a != b:
                    fields = allowed_fields if a['rid'] in chart_data else {'m_RuleIndex'} if a['rid'] in touched else set()
                    assert (set(a['data']) ^ set(b['data'])) <= fields
                    assert all(a['data'].get(k)==v for k,v in b['data'].items() if k not in fields)
            for k,v in prior_sheet.items():
                assert sheet[k][:len(v)] == v if k in {'floats','dimensions','strings','m_Rules'} else sheet[k]==v
            validate_ui(doc,sheet)
            doc['m_ContentHash'] = zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode()) & 0x7fffffff
            changes[pid] = doc
            if sheet != prior_sheet:
                assert sid not in changes
                changes[sid] = sheet
            page_checks.append(dict(page=doc['m_Name'], pid=pid, charts=details, edited_layout_nodes=sorted(touched)))
        for pid, data in changes.items():
            objects[pid].save_typetree(data)
        payload = env.file.save(packer='lz4')
        readback = {o.path_id:o for o in UnityPy.load(payload).objects}
        assert readback.keys() == objects.keys()
        for pid, digest in hashes.items():
            if pid in changes:
                assert readback[pid].read_typetree() == changes[pid], (tag,pid)
            else:
                assert sha(readback[pid].get_raw_data()) == digest, (tag,pid)
        src, backup = out/tag/W, out/('backup-'+tag)/W
        src.parent.mkdir(); backup.parent.mkdir()
        src.write_bytes(payload); backup.write_bytes(before)
        tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(payload)))
        audit.append(dict(target=tag, choices=sorted(active), pages=page_checks,
                          charts=sum(len(x['charts']) for x in page_checks), other_objects_byte_identical=True))
        print(tag, len(active), len(page_checks), audit[-1]['charts'], flush=True)
    for file,value in [('transaction.json',tx),('manifest.json',dict(installed=False,runtime_verified=False,
                                                                  protected_sha256=protected,audits=audit))]:
        (out/file).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
    (out/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
    for mode,file in [('', 'install.ps1'),(' --restore','restore.ps1')]:
        (out/file).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+
                              "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+
                              "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
    print(out,flush=True)


if __name__=='__main__':
    main()
