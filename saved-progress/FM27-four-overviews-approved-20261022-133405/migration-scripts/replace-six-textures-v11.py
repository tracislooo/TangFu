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

SOURCE = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
OUT = ROOT / '六张图片尺寸透明度更新-v11-DXT5'
PNG_ROOT = Path('K:/桌面/27skin')
INPUTS = [PNG_ROOT / 'PlayerTopBlueLight.png'] + [
    PNG_ROOT / 'FcCard/新建文件夹' / (name + '.png')
    for name in ('CA000', 'CA120', 'CA140', 'CA160', 'CA180')
]

source_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
input_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in INPUTS}
env = UnityPy.load(str(SOURCE))
objects = {o.path_id: o for o in env.objects}
original_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
template = objects[-910000000000001].read_typetree()
assert template['m_TextureFormat'] == 12
desired, images, records = {}, {}, []

for index, path in enumerate(INPUTS, 2):
    pid = -910000000000000 - index
    obj = objects[pid]
    original = obj.read_typetree()
    assert obj.type.name == 'Texture2D'
    assert original['m_Name'] == path.stem
    assert original['m_TextureFormat'] == 12
    assert original['m_MipCount'] == 1
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
    desired[pid], images[pid] = data, image
    records.append({'name': path.stem, 'path_id': pid,
                    'old_size': [original['m_Width'], original['m_Height']],
                    'new_size': list(image.size), 'format': 'DXT5', 'format_id': 12,
                    'source_alpha_range': list(image.getchannel('A').getextrema()),
                    'source_png_sha256': input_hashes[path]})

OUT.mkdir(exist_ok=True)
destination = OUT / SOURCE.name
destination.write_bytes(env.file.save(packer='lz4'))
check = UnityPy.load(str(destination))
checked_objects = {o.path_id: o for o in check.objects}
assert set(checked_objects) == set(objects)
for pid, digest in original_hashes.items():
    if pid not in desired:
        assert hashlib.sha256(checked_objects[pid].get_raw_data()).digest() == digest, pid
assert hashlib.sha256(SOURCE.read_bytes()).digest() == source_hash
assert all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in input_hashes.items())

previews = {}
for record in records:
    pid = record['path_id']
    assert checked_objects[pid].read_typetree() == desired[pid]
    decoded = checked_objects[pid].read().image.convert('RGBA')
    original = images[pid]
    assert decoded.size == original.size
    rms = ImageStat.Stat(ImageChops.difference(decoded, original)).rms
    assert rms[3] < 20
    assert sum(rms) < sum(ImageStat.Stat(ImageChops.difference(decoded, original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
    alpha_range = decoded.getchannel('A').getextrema()
    assert all(abs(a - b) <= 3 for a, b in zip(alpha_range, original.getchannel('A').getextrema()))
    record['decoded_alpha_range'] = list(alpha_range)
    record['decoded_rgba_rms_error'] = [round(x, 4) for x in rms]
    record['texture_bytes_changed'] = hashlib.sha256(checked_objects[pid].get_raw_data()).digest() != original_hashes[pid]
    previews[record['name']] = decoded

# Visual verification image assembled from textures decoded from the finished bundle.
sheet = Image.new('RGB', (1100, 740), '#343434')
draw = ImageDraw.Draw(sheet)
for i, name in enumerate(('CA000', 'CA120', 'CA140', 'CA160', 'CA180')):
    tile = Image.new('RGBA', (200, 340))
    painter = ImageDraw.Draw(tile)
    for y in range(0, 340, 16):
        for x in range(0, 200, 16):
            shade = '#d6d6d6' if (x // 16 + y // 16) % 2 == 0 else '#a7a7a7'
            painter.rectangle((x, y, x + 15, y + 15), fill=shade)
    pic = previews[name].copy()
    pic.thumbnail((190, 325))
    tile.alpha_composite(pic, ((200 - pic.width) // 2, (340 - pic.height) // 2))
    sheet.paste(tile.convert('RGB'), (10 + i * 220, 35))
    draw.text((10 + i * 220, 10), name + ' / ' + str(previews[name].size), fill='white')
blue = previews['PlayerTopBlueLight'].copy()
blue.thumbnail((1050, 315))
blue_tile = Image.new('RGBA', (1050, 320), '#202020')
blue_tile.alpha_composite(blue, ((1050 - blue.width) // 2, (320 - blue.height) // 2))
sheet.paste(blue_tile.convert('RGB'), (25, 410))
draw.text((25, 390), 'PlayerTopBlueLight / DXT5 / -910000000000002', fill='white')
sheet.save(OUT / '包内六张纹理解码预览.png')

report = {'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash.hex(),
          'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
          'textures': records, 'other_resources_unchanged': len(original_hashes) - len(desired)}
(OUT / '替换记录.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
mapping = '\n'.join(f"{r['name']}：{r['path_id']}；尺寸 {r['new_size'][0]} × {r['new_size'][1]}；源图Alpha范围 {r['source_alpha_range']}" for r in records)
(OUT / '安装说明.txt').write_text(f'''六张图片尺寸与透明度更新 v11

{mapping}

按本次最新PNG文件替换原有六张纹理，保持原ID、资源名、DXT5格式、其他纹理设置和资源引用。
透明度采用新PNG中的Alpha通道，DXT5编码存在正常压缩误差。
原有PlayerTopBackground（-910000000000001）和其余资源未修改。

备份皮肤 packages 内的 ui-backgrounds_assets_common.bundle，用本目录同名文件替换。
这份bundle包含全部六张更新后的图片，不需要先安装v10。
预览来自成品bundle解码，已核对ID、尺寸、方向、透明度与所有其他资源原始字节未变。
源packages文件未覆盖，尚未在游戏中验证显示效果。
''', encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps(report, ensure_ascii=True))
