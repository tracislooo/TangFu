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
IMAGE_ROOT = Path('K:/桌面/27skin/属性')
OUT = ROOT / '背景包新增70张属性图-v14-DXT5'
GROUPS = ['SPT', 'TCN', 'ATT', 'DEF', 'FED', 'KIK', 'SPD']
INPUTS = [IMAGE_ROOT / f'{group}{level:02d}.png' for group in GROUPS for level in range(1, 11)]
TEMPLATE_ID = -910000000000001

assert len(INPUTS) == 70 and all(path.is_file() for path in INPUTS)
source_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
env = UnityPy.load(str(SOURCE))
objects = {obj.path_id: obj for obj in env.objects}
original_hashes = {pid: hashlib.sha256(obj.get_raw_data()).digest() for pid, obj in objects.items()}
template = objects[TEMPLATE_ID]
template_data = template.read_typetree()
asset_file = template.assets_file
assert template.type.name == 'Texture2D'
assert template_data['m_TextureFormat'] == 12 and template_data['m_MipCount'] == 1
assert all(-910000000000000 - i in objects for i in range(1, 18))
bundle_obj = next(obj for obj in env.objects if obj.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
old_metadata = copy.deepcopy(metadata)
old_externals = [(item.path, item.guid, item.type) for item in asset_file.externals]
input_hashes, desired, source_images, records = {}, {}, {}, []

for number, path in enumerate(INPUTS, 18):
    pid = -910000000000000 - number
    assert pid not in asset_file.objects, f'Path ID collision: {pid}'
    key = path.stem.lower()
    assert all(existing_key != key for existing_key, _ in metadata['m_Container']), key
    assert all(obj.peek_name() != path.stem for obj in objects.values() if obj.type.name == 'Texture2D'), path.stem
    input_hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as png:
        png.load()
        image = png.convert('RGBA')
    pixels, format_id = image_to_texture2d(
        image, template_data['m_TextureFormat'], template.platform, template_data['m_PlatformBlob']
    )
    assert int(format_id) == 12
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
    metadata['m_Container'].append((key, {
        'preloadIndex': len(metadata['m_PreloadTable']), 'preloadSize': 1,
        'asset': copy.deepcopy(pointer),
    }))
    metadata['m_PreloadTable'].append(pointer)
    desired[pid], source_images[pid] = data, image
    records.append({'name': path.stem, 'path_id': pid, 'container_name': key,
                    'size': list(image.size), 'format': 'DXT5', 'format_id': 12,
                    'source_alpha_range': list(image.getchannel('A').getextrema()),
                    'source_png_sha256': input_hashes[path]})

metadata['m_Container'].sort(key=lambda item: item[0])
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
destination = OUT / SOURCE.name
destination.write_bytes(env.file.save(packer='lz4'))

# Validate the saved file: all previous resources, preload ranges and references remain intact.
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
assert [(item.path, item.guid, item.type) for item in checked[TEMPLATE_ID].assets_file.externals] == old_externals
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
    info = new_containers[record['container_name']]
    assert info['asset'] == {'m_FileID': 0, 'm_PathID': pid}
    assert checked_metadata['m_PreloadTable'][info['preloadIndex']] == info['asset']
    record['decoded_alpha_range'] = list(alpha_range)
    record['decoded_rgba_rms_error'] = [round(value, 4) for value in rms]
    previews[record['name']] = decoded

# Overview of every newly embedded texture, decoded from the finished bundle.
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
    image = previews[record['name']].copy()
    image.thumbnail((126, 126))
    tile.alpha_composite(image, ((126 - image.width) // 2, (126 - image.height) // 2))
    sheet.paste(tile.convert('RGB'), (x, y))
    draw.text((x, y - 18), record['name'], fill='white')
sheet.save(OUT / '包内70张属性图解码预览.png')

manifest = {'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash.hex(),
            'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'serialized_file': asset_file.name, 'new_texture_count': len(records),
            'existing_resources_preserved': len(original_hashes) - 1, 'textures': records}
(OUT / '资源ID对照.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
mapping = '\n'.join(f"{record['name']}\t{record['path_id']}\t{record['size'][0]}×{record['size'][1]}\tDXT5" for record in records)
(OUT / '资源ID对照.txt').write_text('名称\tPath ID\t尺寸\t格式\n' + mapping + '\n', encoding='utf-8-sig')
(OUT / '安装说明.txt').write_text(f'''背景包新增70张属性图 v14

按SPT、TCN、ATT、DEF、FED、KIK、SPD的顺序，每组01至10分配Path ID。
新增ID从 -910000000000018 至 -910000000000087；详见资源ID对照文件。
各图尺寸均为200×200，DXT5（格式12），1级Mip，保留源PNG透明通道。
其他纹理设置沿用 -910000000000001（PlayerTopBackground）。
序列化文件：{asset_file.name}。
全部新增图片已登记资源名称和预加载。

备份皮肤packages里的 {SOURCE.name}，用本目录同名文件替换。
此前的CA、BlueLight、十张等级图和所有其他资源均保留。
本次仅加入图片，未修改界面引用。界面使用时另行配置对应Path ID。

验证：已重新打开成品bundle，70张图片均可解码；核对ID、尺寸、方向、Alpha和预加载。
所有其他资源原始字节未变，源packages文件未覆盖。
预览拼图来自成品bundle解码，仅用于查看；它合成在棋盘底色上，本身不带Alpha。
纹理资源中仍保留原PNG的Alpha，DXT5有正常压缩误差。
''', encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(destination), 'zip': str(archive), 'count': len(records),
                  'dimensions': sorted(set(tuple(record['size']) for record in records)),
                  'first_id': records[0]['path_id'], 'last_id': records[-1]['path_id'],
                  'existing_resources_preserved': len(original_hashes) - 1,
                  'group_id_ranges': {group: [records[index * 10]['path_id'], records[index * 10 + 9]['path_id']]
                                      for index, group in enumerate(GROUPS)}}, ensure_ascii=True))
