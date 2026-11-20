import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image, ImageChops, ImageDraw, ImageStat

BUNDLE_NAME = 'ui-backgrounds_assets_common.bundle'
SOURCE = ROOT / '背景包新增十张等级图-v12-DXT5' / BUNDLE_NAME
OUT = ROOT / '五张CA图片更新-v13-DXT5'
IMAGE_ROOT = Path('K:/桌面/27skin/FcCard/新建文件夹')
NAMES = ['CA000', 'CA120', 'CA140', 'CA160', 'CA180']

source_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
env = UnityPy.load(str(SOURCE))
objects = {obj.path_id: obj for obj in env.objects}
original_hashes = {pid: hashlib.sha256(obj.get_raw_data()).digest() for pid, obj in objects.items()}
desired, source_images, input_hashes, records = {}, {}, {}, []
for index, name in enumerate(NAMES, 3):
    path = IMAGE_ROOT / (name + '.png')
    pid = -910000000000000 - index
    obj = objects[pid]
    original = obj.read_typetree()
    assert obj.type.name == 'Texture2D' and original['m_Name'] == name
    assert original['m_TextureFormat'] == 12 and original['m_MipCount'] == 1
    input_hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as png:
        png.load()
        image = png.convert('RGBA')
    pixels, format_id = image_to_texture2d(image, 12, obj.platform, original['m_PlatformBlob'])
    assert int(format_id) == 12
    assert len(pixels) == ((image.width + 3) // 4) * ((image.height + 3) // 4) * 16
    data = copy.deepcopy(original)
    data.update(m_Width=image.width, m_Height=image.height, m_CompleteImageSize=len(pixels))
    data['image data'] = pixels
    data['m_StreamData'] = {'offset': 0, 'size': 0, 'path': ''}
    obj.save_typetree(data)
    desired[pid], source_images[pid] = data, image
    records.append({'name': name, 'path_id': pid,
                    'old_size': [original['m_Width'], original['m_Height']],
                    'new_size': list(image.size), 'format': 'DXT5', 'format_id': 12,
                    'source_png_sha256': input_hashes[path],
                    'source_alpha_range': list(image.getchannel('A').getextrema())})

OUT.mkdir(exist_ok=True)
destination = OUT / BUNDLE_NAME
destination.write_bytes(env.file.save(packer='lz4'))
check = UnityPy.load(str(destination))
checked = {obj.path_id: obj for obj in check.objects}
assert set(checked) == set(objects)
for pid, digest in original_hashes.items():
    if pid not in desired:
        assert hashlib.sha256(checked[pid].get_raw_data()).digest() == digest, pid
assert hashlib.sha256(SOURCE.read_bytes()).digest() == source_hash
assert all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in input_hashes.items())

previews = {}
for record in records:
    pid = record['path_id']
    assert checked[pid].read_typetree() == desired[pid]
    decoded = checked[pid].read().image.convert('RGBA')
    original = source_images[pid]
    assert decoded.size == original.size
    alpha_range = decoded.getchannel('A').getextrema()
    assert all(abs(a - b) <= 3 for a, b in zip(alpha_range, original.getchannel('A').getextrema()))
    rms = ImageStat.Stat(ImageChops.difference(decoded, original)).rms
    assert rms[3] < 20
    inverted_rms = ImageStat.Stat(ImageChops.difference(decoded, original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms
    assert sum(rms) < sum(inverted_rms)
    record['decoded_alpha_range'] = list(alpha_range)
    record['decoded_rgba_rms_error'] = [round(value, 4) for value in rms]
    previews[record['name']] = decoded

assert checked[-910000000000002].read().image.getchannel('A').getextrema() == (0, 101)
for level in range(1, 11):
    pid = -910000000000000 - (level + 7)
    assert checked[pid].peek_name() == f'level{level:03d}'
    assert hashlib.sha256(checked[pid].get_raw_data()).digest() == original_hashes[pid]

sheet = Image.new('RGB', (1100, 280), '#343434')
draw = ImageDraw.Draw(sheet)
for index, name in enumerate(NAMES):
    x = 10 + index * 220
    tile = Image.new('RGBA', (200, 230))
    painter = ImageDraw.Draw(tile)
    for y in range(0, 230, 16):
        for tile_x in range(0, 200, 16):
            shade = '#d6d6d6' if (tile_x // 16 + y // 16) % 2 == 0 else '#a7a7a7'
            painter.rectangle((tile_x, y, tile_x + 15, y + 15), fill=shade)
    image = previews[name].copy()
    image.thumbnail((192, 222))
    tile.alpha_composite(image, ((200 - image.width) // 2, (230 - image.height) // 2))
    sheet.paste(tile.convert('RGB'), (x, 40))
    draw.text((x, 10), name + ' / ' + str(previews[name].size), fill='white')
sheet.save(OUT / '包内CA图片解码预览.png')

report = {'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash.hex(),
          'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
          'textures': records, 'other_resources_unchanged': len(original_hashes) - len(desired),
          'level001_to_level010_preserved': True, 'blue_light_preserved': True}
(OUT / '替换记录.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
mapping = '\n'.join(f"{record['name']}：{record['path_id']}；{record['new_size'][0]} × {record['new_size'][1]}" for record in records)
(OUT / '安装说明.txt').write_text(f'''五张CA图片更新 v13

{mapping}

以v12为基础，使用本次最新PNG替换原有五张CA纹理。
保留原ID、名称、DXT5格式、其他纹理设置和界面引用；尺寸与透明度采用新PNG。
BlueLight、PlayerTopBackground及十张level等级图均保留，没有修改其他资源。

备份皮肤packages内的 {BUNDLE_NAME}，用本目录同名bundle替换。
本包包含此前所有图片，无需先安装v11或v12。
预览来自成品bundle解码，已核对尺寸、方向、Alpha，并确认其余资源原始字节未变。
源文件未覆盖。
''', encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps(report, ensure_ascii=True))
