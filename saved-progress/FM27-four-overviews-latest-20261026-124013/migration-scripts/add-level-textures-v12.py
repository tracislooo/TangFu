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
SOURCE = ROOT / '六张图片尺寸透明度更新-v11-DXT5' / BUNDLE_NAME
PACKAGES = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
IMAGE_ROOT = Path('K:/桌面/27skin/等级10_')
OUT = ROOT / '背景包新增十张等级图-v12-DXT5'
TEMPLATE_ID = -910000000000001

source_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
env = UnityPy.load(str(SOURCE))
objects = {obj.path_id: obj for obj in env.objects}
original_hashes = {pid: hashlib.sha256(obj.get_raw_data()).digest() for pid, obj in objects.items()}
template = objects[TEMPLATE_ID]
template_data = template.read_typetree()
asset_file = template.assets_file
assert template.type.name == 'Texture2D'
assert template_data['m_TextureFormat'] == 12
assert template_data['m_MipCount'] == 1
bundle_obj = next(obj for obj in env.objects if obj.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
old_metadata = copy.deepcopy(metadata)
old_externals = [(external.path, external.guid, external.type) for external in asset_file.externals]

# The installed source is an older copy. Verify that v11 retains all its other assets.
package_path = PACKAGES / BUNDLE_NAME
package_hash = hashlib.sha256(package_path.read_bytes()).digest()
installed = UnityPy.load(str(package_path))
installed_objects = {obj.path_id: obj for obj in installed.objects}
assert set(installed_objects) == set(objects)
previously_updated_ids = {-910000000000000 - i for i in range(2, 8)}
for pid, obj in installed_objects.items():
    if pid not in previously_updated_ids:
        assert hashlib.sha256(obj.get_raw_data()).digest() == original_hashes[pid], pid

records, desired, source_images, input_hashes = [], {}, {}, {}
for level in range(1, 11):
    path = IMAGE_ROOT / f'level{level:03d}.png'
    pid = -910000000000000 - (level + 7)
    assert pid not in asset_file.objects, f'Path ID collision: {pid}'
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
    reader.path_id = pid
    reader.data = None
    reader._read_until = None
    reader.save_typetree(data)
    asset_file.objects[pid] = reader
    key = path.stem.lower()
    assert all(existing_key != key for existing_key, _ in metadata['m_Container'])
    preload_index = len(metadata['m_PreloadTable'])
    pointer = {'m_FileID': 0, 'm_PathID': pid}
    metadata['m_PreloadTable'].append(copy.deepcopy(pointer))
    metadata['m_Container'].append((key, {
        'preloadIndex': preload_index, 'preloadSize': 1, 'asset': pointer
    }))
    records.append({'name': path.stem, 'path_id': pid, 'container_name': key,
                    'size': list(image.size), 'texture_format': 'DXT5',
                    'texture_format_id': 12, 'source_alpha_range': list(image.getchannel('A').getextrema()),
                    'source_png_sha256': input_hashes[path]})
    desired[pid], source_images[pid] = data, image

metadata['m_Container'].sort(key=lambda item: item[0])
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
destination = OUT / BUNDLE_NAME
destination.write_bytes(env.file.save(packer='lz4'))

check = UnityPy.load(str(destination))
check_objects = {obj.path_id: obj for obj in check.objects}
assert set(check_objects) == set(objects) | set(desired)
for pid, digest in original_hashes.items():
    if pid != bundle_obj.path_id:
        assert hashlib.sha256(check_objects[pid].get_raw_data()).digest() == digest, pid
check_metadata = check_objects[bundle_obj.path_id].read_typetree()
assert check_metadata == metadata
old_containers = dict(old_metadata['m_Container'])
new_containers = dict(check_metadata['m_Container'])
assert all(new_containers[key] == value for key, value in old_containers.items())
assert check_metadata['m_PreloadTable'][:len(old_metadata['m_PreloadTable'])] == old_metadata['m_PreloadTable']
assert [(external.path, external.guid, external.type)
        for external in check_objects[TEMPLATE_ID].assets_file.externals] == old_externals
assert hashlib.sha256(SOURCE.read_bytes()).digest() == source_hash
assert hashlib.sha256(package_path.read_bytes()).digest() == package_hash
assert all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in input_hashes.items())

previews = {}
for record in records:
    pid = record['path_id']
    data = check_objects[pid].read_typetree()
    assert data == desired[pid]
    assert data['m_TextureFormat'] == template_data['m_TextureFormat']
    assert data['m_TextureSettings'] == template_data['m_TextureSettings']
    assert data['m_ColorSpace'] == template_data['m_ColorSpace']
    decoded = check_objects[pid].read().image.convert('RGBA')
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
    info = new_containers[record['container_name']]
    assert info['asset'] == {'m_FileID': 0, 'm_PathID': pid}
    assert check_metadata['m_PreloadTable'][info['preloadIndex']] == info['asset']
    previews[record['name']] = decoded

# Checkerboard preview from the textures decoded from the finished bundle.
sheet = Image.new('RGB', (1062, 790), '#343434')
draw = ImageDraw.Draw(sheet)
for i, record in enumerate(records):
    x = 15 + (i % 3) * 350
    y = 38 + (i // 3) * 190
    tile = Image.new('RGBA', (326, 168))
    painter = ImageDraw.Draw(tile)
    for tile_y in range(0, 168, 16):
        for tile_x in range(0, 326, 16):
            shade = '#d6d6d6' if (tile_x // 16 + tile_y // 16) % 2 == 0 else '#a7a7a7'
            painter.rectangle((tile_x, tile_y, tile_x + 15, tile_y + 15), fill=shade)
    tile.alpha_composite(previews[record['name']])
    sheet.paste(tile.convert('RGB'), (x, y))
    draw.text((x, y - 19), record['name'] + ' / ' + str(record['path_id']), fill='white')
sheet.save(OUT / '包内等级图解码预览.png')

blue_alpha = check_objects[-910000000000002].read().image.getchannel('A').getextrema()
assert blue_alpha == (0, 101)
assert all(check_objects[-910000000000000 - i].read().image.size == (576, 680) for i in range(3, 8))
manifest = {'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash.hex(),
            'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'serialized_file': asset_file.name, 'textures': records,
            'existing_resources_preserved': len(original_hashes) - 1,
            'blue_light_alpha_range_preserved': list(blue_alpha)}
(OUT / '资源ID对照.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
mapping = '\n'.join(f"{record['name']}：{record['path_id']}" for record in records)
(OUT / '安装与资源说明.txt').write_text(f'''背景包新增十张等级图 v12

{mapping}

新增纹理尺寸均为326×168，DXT5（格式编号12），1级Mip，保留源PNG的透明通道。
其他纹理设置沿用 -910000000000001（PlayerTopBackground）。
已登记新增图片的资源名称与预加载条目。
序列化文件：{asset_file.name}。

此包基于v11，保留全部既有图片，包括五张576×680的CA图及40%左右不透明度的BlueLight。
当前packages目录仍为旧版，所以未用旧版作为基础，以免撤销上一次更新。
备份皮肤packages内的 {BUNDLE_NAME}，用本包同名bundle替换。
本次仅加入图片，没有修改界面引用。界面使用时须再配置对应Path ID。

已重读生成文件，十张纹理均可解码，核对尺寸、方向、Alpha、ID及预加载；其余资源原始字节未变。
源文件和packages文件未覆盖。
''', encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(destination), 'zip': str(archive),
                  'textures': records, 'existing_resources_preserved': len(original_hashes) - 1,
                  'blue_alpha_preserved': blue_alpha}, ensure_ascii=True))
