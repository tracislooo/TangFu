"""Offline TF skin V1 texture replacement utility; never launches the game."""
import copy, datetime, hashlib, io, json, os, subprocess, sys, threading, uuid
from pathlib import Path
def error_log(kind, value, tb):
    import traceback
    dest=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
    (dest/'error.log').write_text(''.join(traceback.format_exception(kind,value,tb)), 'utf8')
sys.excepthook=error_log
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.codex-deps'))
import UnityPy
from PIL import Image, ImageOps, ImageTk

BASE = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
PID = -910000000000149
NAME = 'TF skin V1'
BUNDLE = 'ui-backgrounds_assets_common.bundle'
sha = lambda data: hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def closed():
    r = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq fm.exe', '/FO', 'CSV', '/NH'], capture_output=True, creationflags=0x08000000)
    if b'"fm.exe"' in r.stdout.lower():
        raise RuntimeError('请先正常退出 Football Manager，再执行替换或回退。')

def atomic(path, data):
    path = Path(path)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_bytes(data)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def prepare(raw, image, targets, reserved):
    env = UnityPy.load(raw)
    af = next(a for a in env.assets if PID in a.objects) if PID in targets else env.assets[0]
    objects = af.objects
    if set(objects) & set(reserved):
        raise RuntimeError('资源包含永久禁用 ID，已停止。')
    hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
    for pid, name in targets.items():
        if pid not in objects or objects[pid].type.name != 'Texture2D' or objects[pid].peek_name() != name:
            raise RuntimeError(f'资源版本不匹配：未找到 {name} / {pid}，未写入文件。')
    for pid in targets:
        texture = objects[pid].read()
        texture.set_image(image, target_format=4, mipmap_count=1)
        texture.save()
    payload = env.file.save(packer='lz4')
    check = UnityPy.load(payload)
    saved = next(a for a in check.assets if a.name == af.name).objects
    assert set(saved) == set(objects), '对象集合改变'
    for pid, h in hashes.items():
        if pid not in targets:
            assert sha(saved[pid].get_raw_data()) == h, f'无关资源改变：{pid}'
        else:
            t = saved[pid].read()
            assert t.m_Name == targets[pid]
            assert t.image.convert('RGBA').tobytes() == image.tobytes(), '像素校验失败'
    return payload, {str(pid): sha(saved[pid].get_raw_data()) for pid in targets}

def replace(image_path, bundle_path, sync_native=False, skin=False):
    closed()
    cfg = read_json(BASE / 'config.json')
    path = Path(bundle_path).resolve()
    if path.name != BUNDLE:
        raise RuntimeError('请选择 ui-backgrounds_assets_common.bundle。')
    if 'Project Taco' in str(path):
        raise RuntimeError('旧游戏目录已停用。')
    with Image.open(image_path) as img:
        image = ImageOps.exif_transpose(img).convert('RGBA')
    if image.width * image.height > 40000000:
        raise RuntimeError('图片超过四千万像素，请先缩小。')
    folders = [path.parent]
    if skin:
        folders.append(Path(cfg['skin_packages']).resolve())
    folders = list(dict.fromkeys(folders))
    targets = {BUNDLE: {PID: NAME}}
    if sync_native:
        for row in cfg['native_copies']:
            targets.setdefault(row['bundle'], {})[int(row['path_id'])] = row['actual_name']
    pending, texture_hashes = {}, {}
    for folder in folders:
        for bn, wanted in targets.items():
            p = folder / bn
            old = p.read_bytes()
            new, hashes = prepare(old, image, wanted, cfg['reserved'])
            pending[p] = (old, new)
            texture_hashes[str(p)] = hashes
    # Keep the workspace's authoritative source current for later skin maintenance.
    regpath = Path(cfg['registry'])
    if path == Path(cfg['default_bundle']).resolve() and regpath.exists():
        old = regpath.read_bytes()
        reg = json.loads(old)
        reg['version'] += 1
        reg['authoritative_source_bundle'] = str(path)
        reg['source_bundle_sha256'] = sha(pending[path][1])
        for row in reg['textures']:
            if int(row['path_id']) == PID:
                row.update(texture_sha256=texture_hashes[str(path)][str(PID)], size=list(image.size), texture_format_id=4,
                           source_png=str(Path(image_path).resolve()))
        reg['tf_background_tool_last_replacement'] = {'date_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source_image': str(Path(image_path).resolve()), 'native_copies_synced': sync_native, 'skin_synced': skin}
        pending[regpath] = (old, json.dumps(reg, ensure_ascii=False, indent=2).encode('utf8'))
    backup = BASE / 'backups' / (datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6])
    backup.mkdir(parents=True)
    rows = []
    for i, (p, (old, new)) in enumerate(pending.items()):
        b = backup / (str(i) + '-' + p.name)
        b.write_bytes(old)
        rows.append({'target': str(p), 'backup': str(b), 'before': sha(old), 'after': sha(new)})
    manifest = {'files': rows, 'image': str(image_path), 'size': list(image.size), 'texture_hashes': texture_hashes, 'installed': False}
    (backup / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
    closed()
    for p, (old, new) in pending.items():
        assert p.read_bytes() == old, f'生成期间文件发生改变：{p}'
    try:
        for p, (old, new) in pending.items():
            atomic(p, new)
            assert p.read_bytes() == new
    except BaseException:
        for p, (old, new) in pending.items():
            atomic(p, old)
        raise
    manifest['installed'] = True
    (backup / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
    return str(backup)

def restore(manifest_path):
    closed()
    manifest_path = Path(manifest_path)
    manifest = read_json(manifest_path)
    if not manifest.get('installed'):
        raise RuntimeError('此备份没有处于已安装状态。')
    work = []
    for row in manifest['files']:
        p, b = Path(row['target']), Path(row['backup'])
        current, original = p.read_bytes(), b.read_bytes()
        if sha(current) != row['after'] or sha(original) != row['before']:
            raise RuntimeError(f'文件已更新或备份损坏，已停止以保护后续修改：{p}')
        work.append((p, current, original))
    closed()
    try:
        for p, current, original in work:
            assert p.read_bytes() == current
            atomic(p, original)
            assert p.read_bytes() == original
    except BaseException:
        for p, current, original in work:
            atomic(p, current)
        raise
    manifest['installed'] = False
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')

def main():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    cfg = read_json(BASE / 'config.json')
    root = tk.Tk(); root.title('TF skin V1 背景替换器'); root.geometry('700x580')
    frame = ttk.Frame(root, padding=16); frame.pack(fill='both', expand=True)
    image_path, bundle = tk.StringVar(), tk.StringVar(value=cfg['default_bundle'])
    sync, skin = tk.BooleanVar(), tk.BooleanVar()
    status = tk.StringVar(value='选择图片后点击替换。游戏需先退出；重新启动后查看效果。')
    def choose_image():
        p = filedialog.askopenfilename(filetypes=[('图片','*.png *.jpg *.jpeg *.webp *.bmp'),('所有文件','*.*')])
        if p:
            try:
                with Image.open(p) as img:
                    thumb=ImageOps.exif_transpose(img).convert('RGBA'); thumb.thumbnail((640,280))
                    photo=ImageTk.PhotoImage(thumb); preview.configure(image=photo); preview.image=photo
                image_path.set(p)
            except Exception as e: messagebox.showerror('图片无法读取',str(e))
    ttk.Label(frame,text='目标资源包').pack(anchor='w')
    ttk.Entry(frame,textvariable=bundle).pack(fill='x')
    ttk.Button(frame,text='选择 bundle',command=lambda: bundle.set(filedialog.askopenfilename(filetypes=[('资源包','*.bundle')]) or bundle.get())).pack(anchor='e')
    ttk.Button(frame,text='选择替换图片',command=choose_image).pack(anchor='w')
    ttk.Label(frame,textvariable=image_path,wraplength=650).pack(anchor='w')
    preview=ttk.Label(frame,anchor='center'); preview.pack(fill='both',expand=True)
    ttk.Checkbutton(frame,text='同步清单内的原生背景副本（含 fm-skin-v2 和赛事背景）',variable=sync).pack(anchor='w')
    ttk.Checkbutton(frame,text='同时替换独立主皮肤中的对应资源',variable=skin).pack(anchor='w')
    ttk.Label(frame,textvariable=status,wraplength=650).pack(anchor='w',pady=10)
    def task(fn):
        apply_button.config(state='disabled'); undo.config(state='disabled');status.set('处理中，请等待完成…')
        def run():
            try:
                result=fn()
                root.after(0,lambda: status.set('完成。'+str(result or '已回退。')))
            except Exception as e:
                msg=str(e);root.after(0,lambda: messagebox.showerror('操作未完成',msg));root.after(0,lambda:status.set('操作未完成，请查看错误信息。'))
            finally:root.after(0,lambda:(apply_button.config(state='normal'),undo.config(state='normal')))
        threading.Thread(target=run,daemon=False).start()
    def apply():
        if not image_path.get():messagebox.showinfo('选择图片','请先选择一张图片。');return
        values=(image_path.get(),bundle.get(),sync.get(),skin.get())
        task(lambda:replace(*values))
    def undo_action():
        p=filedialog.askopenfilename(initialdir=str(BASE/'backups'),title='选择需要回退的备份 manifest.json',filetypes=[('备份清单','manifest.json')])
        if p:task(lambda:restore(p))
    apply_button=ttk.Button(frame,text='替换图片并自动备份',command=apply);apply_button.pack(side='left')
    undo=ttk.Button(frame,text='从备份回退',command=undo_action);undo.pack(side='right')
    root.mainloop()

if __name__ == '__main__':
    if '--self-check' in sys.argv:
        cfg=read_json(BASE/'config.json')
        raw=Path(cfg['default_bundle']).read_bytes()
        data, hashes=prepare(raw,Image.new('RGBA',(37,23),(31,77,123,255)),{PID:NAME},cfg['reserved'])
        assert Path(cfg['default_bundle']).read_bytes()==raw
        (BASE/'self-check.json').write_text(json.dumps({'passed':True,'game_files_untouched':True,'replacement_pixels_verified':True,'unrelated_objects_verified':True}),'utf8')
    else:main()
