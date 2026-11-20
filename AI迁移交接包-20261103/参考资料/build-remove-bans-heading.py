from pathlib import Path
src=Path('third-pitch-top-bans-replace-pros.py').read_text('utf8')
head=src.split('doc=objs[W][PAGE]')[0].replace('third-pitch-top-bans-replace-pros-','third-remove-bans-heading-icon-')
body='''PAGE,STYLE=-940000000011010,-940000000011011
doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
gone=remove_subtree(1002);rr=refs(doc)
assert rr[1001]['data']['m_Children']==[{'rid':1003}]
for i,r in rr.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert r==old[i]
assert 1005 not in rr and 1006 not in rr
save(W,PAGE,doc,STYLE,sheet)

'''
tail=src[src.index('outputs={n:e.file.save'):]
a=tail.index("report={'installed':False");b=tail.index("(OUT/'manifest.json')",a)
tail=tail[:a]+'''report={'installed':False,'runtime_verified':False,'third_only':True,
    'bans_heading_frame_and_flag_removed':True,'bans_table_and_bindings_preserved':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
'''+tail[b:]
tail=tail.replace("'right_height':390,'bans_relocated':True,'pitch_title_removed':True","'bans_heading_removed':True")
Path('third-remove-bans-heading-icon.py').write_text(head+body+tail,'utf8')
