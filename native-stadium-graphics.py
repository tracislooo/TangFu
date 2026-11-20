import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime

from PIL import Image, ImageOps

DATA = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
GENERATED = 'TF Stadium Photos'
OWNER = '.tf-stadium-generated'
TARGET = 'graphics/pictures/team/{}/kits/fmetstadium'
STADIUM = re.compile(r'graphics/pictures/stadium/(\d+)/background', re.I)
FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def closed():
    result = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq fm.exe', '/FO', 'CSV', '/NH'],
                            capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    require(b'"fm.exe"' not in result.stdout.lower(), '请先正常退出 FM27。')


def read_pack(pack):
    pack = pack.resolve()
    result = {}
    for row in ET.parse(pack / 'config.xml').findall('.//record[@to][@from]'):
        match = STADIUM.fullmatch(row.attrib['to'].replace('\\', '/'))
        if not match:
            continue
        name = row.attrib['from'].replace('\\', '/')
        base = (pack / name).resolve()
        require(base.is_relative_to(pack), '球场包 config.xml 含目录外路径。')
        candidates = [base] if base.suffix.lower() in FORMATS else [base.parent / (base.name + ext) for ext in FORMATS]
        found = next((path for path in candidates if path.is_file()), None)
        if found:
            require(found.resolve().is_relative_to(pack), '球场包路径指向目录外的图片。')
            result[int(match[1])] = found
    require(result, '在所选 config.xml 中没有找到可用的球场背景图片。')
    return result


def conflicts(graphics, output):
    for config in graphics.rglob('config.xml'):
        if config.is_relative_to(output):
            continue
        with config.open('rb') as stream:
            if re.search(rb'kits[\\/]fmetstadium\b', stream.read().lower().replace(b'\x00', b'')):
                raise ValueError(f'已有另一份球场槽位配置，避免重复覆盖。请先移出：\n{config}')


def prepare(graphics, pack, mapping, progress=print):
    graphics = graphics.resolve()
    pack = pack.resolve()
    output = graphics / GENERATED
    require(graphics.is_dir() and pack.is_relative_to(graphics) and not pack.is_relative_to(output),
            '请选择 FM 的 graphics 文件夹，以及在其内部的球场包目录。')
    require(output.resolve() == output, 'TF 输出目录不能是指向其他位置的链接。')
    require(not output.exists() or (output / OWNER).is_file(), '输出目录已存在且不属于 TF，未覆盖。')
    conflicts(graphics, output)
    photos = read_pack(pack)
    used = sorted(set(mapping.values()) & photos.keys())
    require(used, '球场包没有与此版球队映射匹配的图片。')
    with tempfile.TemporaryDirectory(prefix='tf-stadium-stage-', dir=graphics.parent) as staging:
        temporary = Path(staging) / GENERATED
        images = temporary / 'images'
        images.mkdir(parents=True)
        Image.new('RGB', (640, 360), '#263445').save(images / 'unavailable.jpg', quality=90)
        names = {}
        converted = 0
        unreadable = []
        for stadium in used:
            source = photos[stadium]
            try:
                with Image.open(source) as image:
                    image.load()
                    if image.format == 'JPEG' and image.mode == 'RGB' and image.getexif().get(274, 1) == 1:
                        filename = f'{stadium}.jpg'
                        shutil.copyfile(source, images / filename)
                    elif image.format == 'PNG' and image.mode in {'RGB', 'RGBA'}:
                        filename = f'{stadium}.png'
                        shutil.copyfile(source, images / filename)
                    else:
                        filename = f'{stadium}.jpg'
                        ImageOps.exif_transpose(image).convert('RGB').save(images / filename, quality=95)
                        converted += 1
            except (Image.UnidentifiedImageError, SyntaxError):
                unreadable.append(stadium)
                continue
            except OSError as error:
                if error.errno is not None:
                    raise
                unreadable.append(stadium)
                continue
            names[stadium] = filename
        require(names, '所有匹配图片均无法解码，未安装。')
        root = ET.Element('record')
        ET.SubElement(root, 'boolean', id='preload', value='false')
        ET.SubElement(root, 'boolean', id='amap', value='false')
        entries = ET.SubElement(root, 'list', id='maps')
        for club, stadium in sorted(mapping.items()):
            filename = names.get(stadium, 'unavailable.jpg')
            ET.SubElement(entries, 'record', {'from': f'images/{Path(filename).stem}', 'to': TARGET.format(club)})
        ET.indent(root, space='  ')
        config = temporary / 'config.xml'
        ET.ElementTree(root).write(config, encoding='utf-8', xml_declaration=True)
        records = ET.parse(config).findall('.//record[@to][@from]')
        assert len({row.attrib['to'] for row in records}) == len(records) == len(mapping)
        stems = {f'images/{path.stem}' for path in images.iterdir()}
        assert all(row.attrib['from'] in stems for row in records)
        (temporary / OWNER).write_text('TF native fmetstadium graphics', 'utf-8')
        closed()
        backup = None
        if output.exists():
            require((output / OWNER).is_file(), '输出目录已变化，未覆盖。')
            backup = graphics.parent / ('TF-Stadium-Backup-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
            output.rename(backup)
        try:
            temporary.rename(output)
        except OSError:
            if backup:
                backup.rename(output)
            raise
        result = dict(clubs=len(mapping), pictured_clubs=sum(stadium in names for stadium in mapping.values()),
                      photos=len(names), converted=converted, unreadable=unreadable, output=str(output),
                      backup=str(backup) if backup else None)
        progress(result)
        return result


def default_graphics():
    import ctypes
    from ctypes import wintypes
    import uuid
    folder = (ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID('FDD39AD0-238F-46AF-ADB4-6C85480369C7').bytes_le)
    output = wintypes.LPWSTR()
    if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(folder), 0, None, ctypes.byref(output)) != 0:
        path = Path.home() / 'Documents'
    else:
        try:
            path = Path(output.value)
        finally:
            ctypes.windll.ole32.CoTaskMemFree(output)
    return path / 'Sports Interactive/Football Manager 27/graphics'


def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('--graphics', type=Path, required=True)
        parser.add_argument('--pack', type=Path, required=True)
        parser.add_argument('--mapping', type=Path, default=DATA / 'tf-native-stadium-clubs.json')
        options = parser.parse_args()
        closed()
        mapping = {int(club): stadium for club, stadium in json.loads(options.mapping.read_text('utf-8')).items()}
        prepare(options.graphics, options.pack, mapping)
        return
    mapping = {int(club): stadium for club, stadium in json.loads((DATA / 'tf-native-stadium-clubs.json').read_text('utf-8')).items()}
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    window = tk.Tk()
    window.title('TF 原生球场照片设置')
    frame = ttk.Frame(window, padding=16)
    frame.pack(fill='both', expand=True)
    frame.columnconfigure(0, weight=1)
    graphics = default_graphics()
    candidates = list(graphics.glob('**/stadium_backgrounds/config.xml'))
    graphics_var = tk.StringVar(value=str(graphics))
    pack_var = tk.StringVar(value=str(candidates[0].parent) if len(candidates) == 1 else '')
    ttk.Label(frame, text='先安装新版 TF 皮肤及球场包，再正常退出 FM27。').grid(row=0, column=0, sticky='w')
    for row, title, variable in [(1, 'FM graphics 文件夹', graphics_var), (3, '球场包文件夹（含 config.xml）', pack_var)]:
        ttk.Label(frame, text=title).grid(row=row, column=0, sticky='w', pady=(8, 0))
        ttk.Entry(frame, textvariable=variable, width=75).grid(row=row+1, column=0, sticky='ew')
        def choose(value=variable):
            selected = filedialog.askdirectory(parent=window, initialdir=value.get() or graphics_var.get())
            if selected:
                value.set(selected)
        ttk.Button(frame, text='浏览…', command=choose).grid(row=row+1, column=1, padx=(6, 0))
    def setup():
        try:
            require(graphics_var.get().strip() and pack_var.get().strip(), '请选择 graphics 和球场包文件夹。')
            closed()
            window.config(cursor='watch')
            button.state(['disabled'])
            window.update_idletasks()
            result = prepare(Path(graphics_var.get()), Path(pack_var.get()), mapping, lambda _: None)
            messagebox.showinfo('球场照片已设置',
                                f"照片匹配 {result['pictured_clubs']} 支球队（{result['photos']} 张图），转换 {result['converted']} 张。\n没有匹配照片的球队使用占位图。\n\n请自行启动 FM27。", parent=window)
        except (OSError, ValueError, ET.ParseError, subprocess.SubprocessError) as error:
            messagebox.showerror('未完成设置', str(error), parent=window)
        finally:
            button.state(['!disabled'])
            window.config(cursor='')
    button = ttk.Button(frame, text='设置球场照片', command=setup)
    button.grid(row=5, column=0, sticky='w', pady=(10, 0))
    window.mainloop()


if __name__ == '__main__':
    main()
