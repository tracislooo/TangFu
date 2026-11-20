import copy
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image, ImageChops, ImageDraw, ImageStat

SOURCE = ROOT / '背景包新增四张90stats徽章-v15-DXT5/ui-backgrounds_assets_common.bundle'
INPUT_ZIP = Path('K:/桌面/27skin/属性/上框加粗成品-70张.zip')
OUT = ROOT / '70张属性图上框加粗更新-v16-DXT5'
GROUPS = ['SPT', 'TCN', 'ATT', 'DEF', 'FED', 'KIK', 'SPD']
NAMES = [f'{group}{level:02d}' for group in GROUPS for level in range(1, 11)]

source_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
zip_hash = hashlib.sha256(INPUT_ZIP.read_bytes()).digest()
env = UnityPy.load(str(SOURCE))
objects = {obj.path_id: obj for obj in env.objects}
original_hashes = {pid: hashlib.sha256(obj.get_raw_data()).digest() for pid, obj in objects.items()}
targets = {}
for obj in objects.values():
    if obj.type.name == 'Texture2D':
        name = obj.peek_name()
        if name in NAMES:
            assert name not in targets, f'Duplicate texture name: {name}'
            targets[name] = obj
assert set(targets) == set(NAMES)
records = []
desired = {}

with zipfile.ZipFile(INPUT_ZIP) as archive:
    entries = {Path(name.replace('\\', '/')).name: name
               for name in archive.namelist() if name.lower().endswith('.png')}
    assert set(entries) == {name + '.png' for name in NAMES}
    for index, name in enumerate(NAMES):
        entry = entries[name + '.png']
        png_bytes = archive.read(entry)
        obj = targets[name]
        pid = obj.path_id
        # Locate by existing resource name, then confirm its previously assigned ID.
        assert pid == -910000000000000 - (18 + index)
        original = obj.read_typetree()
        assert original['m_TextureFormat'] == 12 and original['m_MipCount'] == 1
        with Image.open(io.BytesIO(png_bytes)) as png:
            png.load()
            image = png.convert('RGBA')
        pixels, fmt = image_to_texture2d(image, 12, obj.platform, original['m_PlatformBlob'])
        assert int(fmt) == 12
        assert len(pixels) == ((image.width + 3) // 4) * ((image.height + 3) // 4) * 16
        data = copy.deepcopy(original)
        data.update(m_Width=image.width, m_Height=image.height, m_CompleteImageSize=len(pixels))
        data['image data'] = pixels
        data['m_StreamData'] = {'offset': 0, 'size': 0, 'path': ''}
        obj.save_typetree(data)
        desired[pid] = data
        records.append({'name': name, 'path_id': pid, 'source_zip_entry': entry,
                        'source_png_sha256': hashlib.sha256(png_bytes).hexdigest(),
                        'old_size': [original['m_Width'], original['m_Height']],
                        'new_size': list(image.size), 'format': 'DXT5', 'format_id': 12,
                        'source_alpha_range': list(image.getchannel('A').getextrema())})
        if (index + 1) % 10 == 0:
            print(f'Encoded {index + 1}/70', flush=True)

OUT.mkdir(exist_ok=True)
destination = OUT / SOURCE.name
destination.write_bytes(env.file.save(packer='lz4'))
print('Bundle saved; validating the actual output', flush=True)
check = UnityPy.load(str(destination))
checked = {obj.path_id: obj for obj in check.objects}
assert set(checked) == set(objects)
for pid, digest in original_hashes.items():
    if pid not in desired:
        assert hashlib.sha256(checked[pid].get_raw_data()).digest() == digest, pid
assert hashlib.sha256(SOURCE.read_bytes()).digest() == source_hash
assert hashlib.sha256(INPUT_ZIP.read_bytes()).digest() == zip_hash

# Validate against the original archive while retaining only small preview images.
previews = {}
with zipfile.ZipFile(INPUT_ZIP) as archive:
    for index, record in enumerate(records):
        pid = record['path_id']
        data = checked[pid].read_typetree()
        assert data == desired[pid]
        assert data['m_Name'] == record['name']
        with Image.open(io.BytesIO(archive.read(record['source_zip_entry']))) as png:
            png.load()
            original = png.convert('RGBA')
        decoded = checked[pid].read().image.convert('RGBA')
        assert decoded.size == original.size
        alpha_range = decoded.getchannel('A').getextrema()
        assert all(abs(a - b) <= 3 for a, b in zip(alpha_range, original.getchannel('A').getextrema()))
        rms = ImageStat.Stat(ImageChops.difference(decoded, original)).rms
        assert rms[3] < 20
        inverted_rms = ImageStat.Stat(ImageChops.difference(decoded, original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms
        assert sum(rms) < sum(inverted_rms)
        record['decoded_alpha_range'] = list(alpha_range)
        record['decoded_rgba_rms_error'] = [round(value, 4) for value in rms]
        decoded.thumbnail((126, 126))
        previews[record['name']] = decoded
        if (index + 1) % 10 == 0:
            print(f'Validated {index + 1}/70', flush=True)

# Full overview decoded from the finished bundle, in the original ID/group order.
sheet = Image.new('RGB', (1400, 1040), '#343434')
draw = ImageDraw.Draw(sheet)
for index, record in enumerate(records):
    x = 10 + (index % 10) * 139
    y = 30 + (index // 10) * 147
    tile = Image.new('RGBA', (126, 126))
    painter = ImageDraw.Draw(tile)
    for tile_y in range(0, 126, 12):
        for tile_x in range(0, 126, 12):
            shade = '#d6d6d6' if (tile_x // 12 + tile_y // 12) % 2 == 0 else '#a7a7a7'
            painter.rectangle((tile_x, tile_y, tile_x + 11, tile_y + 11), fill=shade)
    image = previews[record['name']]
    tile.alpha_composite(image, ((126 - image.width) // 2, (126 - image.height) // 2))
    sheet.paste(tile.convert('RGB'), (x, y))
    draw.text((x, y - 18), record['name'], fill='white')
sheet.save(OUT / '包内70张加粗属性图解码预览.png')

manifest = {'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash.hex(),
            'input_archive': str(INPUT_ZIP), 'input_archive_sha256': zip_hash.hex(),
            'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'replaced_texture_count': len(records), 'textures': records,
            'other_resources_unchanged': len(original_hashes) - len(records)}
(OUT / '替换与ID记录.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
mapping = '\n'.join(f"{record['name']}\t{record['path_id']}\t{record['new_size'][0]}×{record['new_size'][1]}\tDXT5" for record in records)
(OUT / '资源ID对照.txt').write_text('名称\t原Path ID（保留）\t新尺寸\t格式\n' + mapping + '\n', encoding='utf-8-sig')
(OUT / '安装说明.txt').write_text(f'''70张属性图上框加粗替换 v16

以v15为基础，按已有资源名替换SPT、TCN、ATT、DEF、FED、KIK、SPD各01至10，共70张。
原Path ID -910000000000018 至 -910000000000087不变；未新增资源或更改界面引用。
每张采用本次新版PNG的1254×1254尺寸和Alpha，DXT5格式及其他纹理设置保持。

用户列出的“上框加粗成品”文件夹目前不存在，已从同目录“上框加粗成品-70张.zip”读取对应70张同名图片。
输入压缩包：{INPUT_ZIP}

四张90stats徽章、BlueLight、CA、十张level等级图、PlayerTopBackground及所有其他资源均保留。
备份皮肤packages里的 {SOURCE.name}，用本目录同名bundle替换。
本包包含此前全部图片，不需另行安装旧版。

已重读成品，70张纹理均可解码；核对名称、ID、尺寸、方向和Alpha。
其余资源（包括AssetBundle目录和预加载数据）的原始字节全部不变。
源bundle、源PNG压缩包未覆盖。
预览拼图为解码纹理合成在棋盘底色上的显示图，本身不带Alpha；纹理内仍有Alpha。
DXT5存在正常压缩误差，尚未进入游戏验证。
''', encoding='utf-8-sig')
archive_path = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive_path) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(destination), 'zip': str(archive_path),
                  'count': len(records), 'dimensions': sorted(set(tuple(record['new_size']) for record in records)),
                  'first_id': records[0]['path_id'], 'last_id': records[-1]['path_id'],
                  'other_resources_unchanged': len(original_hashes) - len(records),
                  'sha256': manifest['output_bundle_sha256']}, ensure_ascii=True))
