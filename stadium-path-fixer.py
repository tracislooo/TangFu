import ctypes
from ctypes import wintypes
from datetime import datetime
from hashlib import md5
from pathlib import Path, PurePosixPath
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import uuid

from catalog_binary import Catalog

TAIL = Path('Sports Interactive/Football Manager 27/graphics/Stadiums/stadium_backgrounds')
GAME_AA = Path('fm_Data/StreamingAssets/aa')
MARKER = re.compile(r'kit2d_\d+_fmetstadium')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def documents():
    folder = (ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID('FDD39AD0-238F-46AF-ADB4-6C85480369C7').bytes_le)
    output = wintypes.LPWSTR()
    result = ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(folder), 0, None, ctypes.byref(output))
    if result != 0:
        return Path.home() / 'Documents'
    try:
        return Path(output.value)
    finally:
        ctypes.windll.ole32.CoTaskMemFree(output)


def steam_game():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam') as key:
        steam = Path(winreg.QueryValueEx(key, 'SteamPath')[0])
    vdf = steam / 'steamapps/libraryfolders.vdf'
    libraries = [steam]
    if vdf.is_file():
        libraries.extend(Path(path.replace('\\\\', '\\')) for path in re.findall(r'"path"\s*"([^"]+)"', vdf.read_text('utf-8-sig')))
    return next((path for library in libraries if ((path := library / 'steamapps/common/Football Manager 27') / 'fm.exe').is_file()), None)


def require_closed():
    result = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq fm.exe', '/FO', 'CSV', '/NH'],
                            capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    require(b'"fm.exe"' not in result.stdout.lower(), '请先正常退出 FM27，再运行修复。')


def relink(data, photos):
    catalog = Catalog(data)
    photos = photos.resolve()
    require((photos / 'config.xml').is_file() and (photos / 'images').is_dir(),
            '球场包目录选错了：请选择包含 config.xml 和 images 的那一层。')
    positions, club_keys = {}, set()
    for key, offsets in catalog.keys():
        if not isinstance(key, str) or not MARKER.fullmatch(key):
            continue
        entries = catalog.array(offsets, 'I')
        require(bool(entries), f'球场登记没有资源位置：{key}')
        club_keys.add(key)
        for offset, in entries:
            if offset in positions:
                continue
            info = catalog.location(offset)
            require(info['provider'] == 'SI.Core.LocalAssetProvider' and info['type'][1] == 'UnityEngine.Texture2D',
                    f'遇到不兼容的球场登记：{key}')
            stored = PurePosixPath(info['internal'].replace('\\', '/'))
            require(stored.parent.name.casefold() == 'images' and stored.suffix.lower() in {'.jpg', '.jpeg', '.png'},
                    f'不支持的球场图片路径：{stored}')
            positions[offset] = (info['internal'], photos / 'images' / stored.name)
    require(bool(positions), '此目录没有 TF 球场照片登记。请先安装包含球场功能的皮肤。')
    paths = {target for _, target in positions.values()}
    missing = sorted(path.name for path in paths if not path.is_file())
    require(not missing, f'这个球场包缺少 {len(missing)} 张已登记的照片，例如：{", ".join(missing[:4])}。\n请选择完整、匹配的球场包。')
    offsets, changed = {}, 0
    for place, (old, path) in positions.items():
        new = path.as_posix()
        if old == new:
            continue
        if new not in offsets:
            if new.isascii():
                encoded, flag = new.encode('ascii'), 0
            else:
                encoded, flag = new.encode('utf-16le'), 0x80000000
            address = catalog.append(encoded, True)
            require(address < 0x40000000, '目录过大，无法安全写入。')
            offsets[new] = address | flag
        struct.pack_into('<I', catalog.data, place + 4, offsets[new])
        changed += 1
    updated = bytes(catalog.data)
    if changed:
        check = Catalog(updated)
        for place, (_, path) in positions.items():
            require(check.location(place)['internal'] == path.as_posix(), '写入后的路径回读失败。')
    return updated, len(club_keys), len(paths), changed


def install(game, photos):
    aa = game / GAME_AA
    catalog, digest = aa / 'catalog.bin', aa / 'catalog.hash'
    require((game / 'fm.exe').is_file() and catalog.is_file() and digest.is_file(),
            '请选择有 fm.exe 的 Football Manager 27 游戏安装目录，不是文档里的 FM 文件夹。')
    require_closed()
    raw, old_hash = catalog.read_bytes(), digest.read_bytes()
    updated, clubs, photo_count, changed = relink(raw, photos)
    if not changed:
        return f'路径已经正确，无需修改。\n已核对 {clubs} 支球队、{photo_count} 张照片。'
    require_closed()
    require(catalog.read_bytes() == raw and digest.read_bytes() == old_hash, '文件在检查期间发生变化，请重试。')
    backups = aa / ('TF-stadium-backup-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backups.mkdir()
    (backups / catalog.name).write_bytes(raw)
    (backups / digest.name).write_bytes(old_hash)
    items = [(catalog, updated), (digest, md5(updated).hexdigest().encode('ascii'))]
    temps = []
    replaced = []
    try:
        for target, payload in items:
            with tempfile.NamedTemporaryFile(dir=aa, delete=False) as handle:
                temporary = Path(handle.name)
                temps.append(temporary)
                handle.write(payload)
        for (target, _), temporary in zip(items, temps):
            os.replace(temporary, target)
            replaced.append(target)
        for target, payload in items:
            require(target.read_bytes() == payload, f'安装校验失败：{target.name}')
    except Exception:
        for target in reversed(replaced):
            shutil.copyfile(backups / target.name, target)
        raise
    finally:
        for temporary in temps:
            temporary.unlink(missing_ok=True)
    return f'已更新 {clubs} 支球队的照片登记（{photo_count} 张图）。\n\n备份：\n{backups}'


def main():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    window = tk.Tk()
    window.title('TF 球场图片路径修复')
    frame = ttk.Frame(window, padding=16)
    frame.grid(sticky='nsew')
    window.columnconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    try:
        game = steam_game()
    except (OSError, UnicodeError):
        game = None
    game_path = tk.StringVar(value=str(game) if game else '')
    photo_path = tk.StringVar(value=str(documents() / TAIL))
    ttk.Label(frame, text='先安装 TF 皮肤和球场图片包，并退出 FM27。').grid(row=0, column=0, sticky='w', pady=(0, 8))

    def choose(variable):
        selected = filedialog.askdirectory(parent=window, initialdir=variable.get() or str(documents()))
        if selected:
            variable.set(selected)

    for row, title, variable in [(1, '游戏安装目录（含 fm.exe）', game_path),
                                 (3, '球场图片包（默认自动填入文档路径）', photo_path)]:
        ttk.Label(frame, text=title).grid(row=row, column=0, sticky='w')
        ttk.Entry(frame, textvariable=variable, width=78).grid(row=row+1, column=0, sticky='ew', pady=(2, 10))
        ttk.Button(frame, text='浏览…', command=lambda value=variable: choose(value)).grid(row=row+1, column=1, padx=(8, 0), pady=(2, 10))

    def apply():
        try:
            require(game_path.get().strip() and photo_path.get().strip(), '请填写游戏和球场图片包目录。')
            button.state(['disabled'])
            window.config(cursor='watch')
            window.update_idletasks()
            result = install(Path(game_path.get().strip()), Path(photo_path.get().strip()))
            messagebox.showinfo('校验完成', result, parent=window)
        except (OSError, ValueError, AssertionError, struct.error, subprocess.SubprocessError) as error:
            messagebox.showerror('未能完成修复', str(error) or '资源目录格式不兼容。', parent=window)
        finally:
            window.config(cursor='')
            button.state(['!disabled'])

    button = ttk.Button(frame, text='修复球场照片路径', command=apply)
    button.grid(row=5, column=0, sticky='w', pady=(4, 0))
    window.mainloop()


if __name__ == '__main__':
    main()
