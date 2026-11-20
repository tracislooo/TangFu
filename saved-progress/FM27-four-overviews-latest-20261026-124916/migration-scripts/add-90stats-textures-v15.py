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

SOURCE = ROOT / '背景包新增70张属性图-v14-DXT5/ui-backgrounds_assets_common.bundle'
IMAGE_ROOT = Path('K:/桌面/27skin/属性/空白徽章-四种配色')
OUT = ROOT / '背景包新增四张90stats徽章-v15-DXT5'
source_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
env = UnityPy.load(str(SOURCE))
objects = {obj.path_id: obj for obj in env.objects}
original_hashes = {pid: hashlib.sha256(obj.get_raw_data()).digest() for pid, obj in objects.items()}
template = objects[-910000000000001]
template_data = template.read_typetree()
asset_file = template.assets_file
assert template_data['m_TextureFormat'] == 12 and template_data['m_MipCount'] == 1
bundle_obj = next(obj for obj in env.objects if obj.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
old_metadata = copy.deepcopy(metadata)
old_externals = [(item.path, item.guid, item.type) for item in asset_file.externals]
records, desired, originals, input_hashes = [], {}, {}, {}

for index in range(1, 5):
    path = IMAGE_ROOT / f'90stats{index:02d}.png'
    pid = -910000000000000 - (index + 87)
    assert pid not in asset_file.objects, f'Path ID collision: {pid}'
    assert all(key != path.stem.lower() for key, _ in metadata['m_Container'])
    assert all(obj.peek_name() != path.stem for obj in objects.values() if obj.type.name == 'Texture2D')
    input_hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as png:
        png.load()
        image = png.convert('RGBA')
    pixels, fmt = image_to_texture2d(image, 12, template.platform, template_data['m_PlatformBlob'])
    assert int(fmt) == 12
    assert len(pixels) == ((image.width + 3) // 4) * ((image.height + 3) // 4) * 16
    data = copy.deepcopy(template_data)
    data.update(m_Name=path.stem, m_Width=image.width, m_Height=image.height,
                m_CompleteImageSize=len(pixels), m_IsAlphaChannelOptional=False)
    data['image data'] = pixels
    data['m_StreamData'] = {'offset': 0, 'size': 0, 'path': ''}
    reader = copy.copy(template)
    reader.path_id, reader.data, reader._read_until = pid, None, None
    reader.save_typetree(data)
    asset_file.objects[pid] = reader
    pointer = {'m_FileID': 0, 'm_PathID': pid}
    metadata['m_Container'].append((path.stem.lower(), {
        'preloadIndex': len(metadata['m_PreloadTable']), 'preloadSize': 1,
        'asset': copy.deepcopy(pointer),
    }))
    metadata['m_PreloadTable'].append(pointer)
    desired[pid], originals[pid] = data, image
    records.append({'name': path.stem, 'path_id': pid, 'container_name': path.stem.lower(),
                    'size': list(image.size), 'format': 'DXT5', 'format_id': 12,
                    'source_alpha_range': list(image.getchannel('A').getextrema()),
                    'source_png_sha256': input_hashes[path]})

metadata['m_Container'].sort(key=lambda item: item[0])
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
destination = OUT / SOURCE.name
destination.write_bytes(env.file.save(packer='lz4'))

check = UnityPy.load(str(destination))
checked = {obj.path_id: obj for obj in check.objects}
assert set(checked) == set(objects) | set(desired)
for pid, digest in original_hashes.items():
    if pid != bundle_obj.path_id:
        assert hashlib.sha256(checked[pid].get_raw_data()).digest() == digest, pid
checked_metadata = checked[bundle_obj.path_id].read_typetree()
assert checked_metadata == metadata
new_containers = dict(checked_metadata['m_Container'])
assert all(new_containers[key] == info for key, info in old_metadata['m_Container'])
assert checked_metadata['m_PreloadTable'][:len(old_metadata['m_PreloadTable'])] == old_metadata['m_PreloadTable']
assert [(item.path, item.guid, item.type) for item in checked[-910000000000001].assets_file.externals] == old_externals
assert hashlib.sha256(SOURCE.read_bytes()).digest() == source_hash
assert all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in input_hashes.items())

previews = {}
for record in records:
    pid = record['path_id']
    assert checked[pid].read_typetree() == desired[pid]
    decoded = checked[pid].read().image.convert('RGBA')
    original = originals[pid]
    assert decoded.size == original.size
    alpha_range = decoded.getchannel('A').getextrema()
    assert all(abs(a - b) <= 3 for a, b in zip(alpha_range, original.getchannel('A').getextrema()))
    rms = ImageStat.Stat(ImageChops.difference(decoded, original)).rms
    assert rms[3] < 20
    inverted_rms = ImageStat.Stat(ImageChops.difference(decoded, original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms
    assert sum(rms) < sum(inverted_rms)
    info = new_containers[record['container_name']]
    assert info['asset'] == {'m_FileID': 0, 'm_PathID': pid}
    assert checked_metadata['m_PreloadTable'][info['preloadIndex']] == info['asset']
    record['decoded_alpha_range'] = list(alpha_range)
    record['decoded_rgba_rms_error'] = [round(value, 4) for value in rms]
    previews[record['name']] = decoded

sheet = Image.new('RGB', (1120, 325), '#343434')
draw = ImageDraw.Draw(sheet)
for index, record in enumerate(records):
    x, y = 12 + index * 280, 42
    tile = Image.new('RGBA', (265, 265))
    painter = ImageDraw.Draw(tile)
    for tile_y in range(0, 265, 16):
        for tile_x in range(0, 265, 16):
            shade = '#d6d6d6' if (tile_x // 16 + tile_y // 16) % 2 == 0 else '#a7a7a7'
            painter.rectangle((tile_x, tile_y, tile_x + 15, tile_y + 15), fill=shade)
    image = previews[record['name']].copy()
    image.thumbnail((265, 265))
    tile.alpha_composite(image, ((265 - image.width) // 2, (265 - image.height) // 2))
    sheet.paste(tile.convert('RGB'), (x, y))
    draw.text((x, 10), record['name'] + ' / ' + str(record['path_id']), fill='white')
sheet.save(OUT / '包内90stats徽章解码预览.png')

manifest = {'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash.hex(),
            'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'serialized_file': asset_file.name, 'textures': records,
            'existing_resources_preserved': len(original_hashes) - 1}
(OUT / '资源ID对照.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
mapping = '\n'.join(f"{record['name']}：{record['path_id']}；{record['size'][0]}×{record['size'][1]}" for record in records)
(OUT / '安装与资源说明.txt').write_text(f'''背景包新增四张90stats徽章 v15

{mapping}

以v14为基础加入四张新图，采用DXT5（格式12）、1级Mip，保留各图原始尺寸和Alpha。
其他纹理设置沿用 -910000000000001（PlayerTopBackground）。
四张图片均已登记资源名称与预加载。
序列化文件：{asset_file.name}。

备份皮肤packages内的 {SOURCE.name}，用本目录同名文件替换。
此前70张属性图、十张等级图、五张CA、BlueLight、PlayerTopBackground及所有其他资源均保留。
本次仅加入图片，界面使用时另行配置对应Path ID。

已重新读取成品bundle，四张图片均可解码；ID、尺寸、方向、Alpha和预加载已核对。
其余资源原始字节均未改变，源文件未覆盖。
DXT5存在正常压缩误差；预览拼图是纹理合成在棋盘底色上的显示图，本身不带Alpha。
''', encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps(manifest, ensure_ascii=True))
