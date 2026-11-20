import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.enums import TextureFormat
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image, ImageChops, ImageDraw, ImageStat

SOURCE = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
OUT = ROOT / '背景包新增六张图片-v9-DXT5'
TEMPLATE_ID = -910000000000001
IMAGE_ROOT = Path('K:/桌面/27skin')
INPUTS = [IMAGE_ROOT / 'PlayerTopBlueLight.png'] + [
    IMAGE_ROOT / 'FcCard/新建文件夹' / (name + '.png')
    for name in ['CA000', 'CA120', 'CA140', 'CA160', 'CA180']
]

source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
env = UnityPy.load(str(SOURCE))
original_objects = {o.path_id: o for o in env.objects}
original_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in original_objects.items()}
template = original_objects[TEMPLATE_ID]
template_data = template.read_typetree()
asset_file = template.assets_file
assert template.type.name == 'Texture2D'
assert template_data['m_TextureFormat'] == int(TextureFormat.DXT5) == 12
assert template_data['m_MipCount'] == 1
bundle_obj = next(o for o in env.objects if o.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
old_metadata = copy.deepcopy(metadata)
records = []
desired = {}
source_images = {}

for offset, path in enumerate(INPUTS, 2):
    pid = -910000000000000 - offset
    assert pid not in asset_file.objects, f'Path ID already exists: {pid}'
    with Image.open(path) as image:
        image.load()
        image = image.convert('RGBA')
    pixels, tex_format = image_to_texture2d(
        image, template_data['m_TextureFormat'], template.platform, template_data['m_PlatformBlob']
    )
    assert int(tex_format) == template_data['m_TextureFormat']
    expected_bytes = ((image.width + 3) // 4) * ((image.height + 3) // 4) * 16
    assert len(pixels) == expected_bytes
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
    # Register as a named asset and preload it independently.
    key = path.stem.lower()
    assert all(k != key for k, _ in metadata['m_Container'])
    preload_index = len(metadata['m_PreloadTable'])
    pointer = {'m_FileID': 0, 'm_PathID': pid}
    metadata['m_PreloadTable'].append(copy.deepcopy(pointer))
    metadata['m_Container'].append((key, {
        'preloadIndex': preload_index, 'preloadSize': 1, 'asset': pointer
    }))
    desired[pid] = data
    source_images[pid] = image
    records.append({'name': path.stem, 'path_id': pid, 'container_name': key,
                    'size': [image.width, image.height], 'texture_format': 'DXT5',
                    'texture_format_id': 12, 'image_data_bytes': len(pixels),
                    'source_png_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

metadata['m_Container'].sort(key=lambda item: item[0])
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
destination = OUT / SOURCE.name
destination.write_bytes(env.file.save(packer='lz4'))

# Validate the actual output, including every previous asset's raw bytes.
check = UnityPy.load(str(destination))
objects = {o.path_id: o for o in check.objects}
assert set(objects) == set(original_objects) | set(desired)
for pid, digest in original_hashes.items():
    if pid != bundle_obj.path_id:
        assert hashlib.sha256(objects[pid].get_raw_data()).digest() == digest, pid
check_meta = objects[bundle_obj.path_id].read_typetree()
assert check_meta == metadata
old_containers = dict(old_metadata['m_Container'])
new_containers = dict(check_meta['m_Container'])
assert all(new_containers[key] == info for key, info in old_containers.items())
assert check_meta['m_PreloadTable'][:len(old_metadata['m_PreloadTable'])] == old_metadata['m_PreloadTable']
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash

previews = {}
for record in records:
    pid = record['path_id']
    data = objects[pid].read_typetree()
    assert data == desired[pid]
    assert data['m_TextureFormat'] == template_data['m_TextureFormat']
    assert data['m_MipCount'] == template_data['m_MipCount']
    assert data['m_TextureSettings'] == template_data['m_TextureSettings']
    assert data['m_ColorSpace'] == template_data['m_ColorSpace']
    image = objects[pid].read().image.convert('RGBA')
    original = source_images[pid]
    assert image.size == original.size
    decoded_alpha = image.getchannel('A').getextrema()
    source_alpha = original.getchannel('A').getextrema()
    assert decoded_alpha[0] == source_alpha[0] == 0
    assert abs(decoded_alpha[1] - source_alpha[1]) <= 3
    difference = ImageChops.difference(image, original)
    channel_rms = ImageStat.Stat(difference).rms
    assert channel_rms[3] < 20, (record['name'], channel_rms)
    # A vertically inverted image must have a larger error than the decoded image.
    inverted_error = ImageStat.Stat(ImageChops.difference(image, original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms
    assert sum(channel_rms) < sum(inverted_error)
    record['decoded_rgba_rms_error'] = [round(x, 4) for x in channel_rms]
    previews[record['name']] = image

# A visual proof sheet from decoded bundle images, rather than source PNGs.
sheet = Image.new('RGB', (1100, 780), '#343434')
draw = ImageDraw.Draw(sheet)
for i, name in enumerate(['CA000', 'CA120', 'CA140', 'CA160', 'CA180']):
    tile = Image.new('RGBA', (200, 390))
    td = ImageDraw.Draw(tile)
    for y in range(0, 390, 16):
        for x in range(0, 200, 16):
            shade = '#d6d6d6' if (x // 16 + y // 16) % 2 == 0 else '#a7a7a7'
            td.rectangle((x, y, x + 15, y + 15), fill=shade)
    pic = previews[name].copy()
    pic.thumbnail((190, 360))
    tile.alpha_composite(pic, ((200 - pic.width) // 2, (390 - pic.height) // 2))
    sheet.paste(tile.convert('RGB'), (10 + i * 220, 30))
    draw.text((10 + i * 220, 10), name + ' / DXT5', fill='white')
blue = previews['PlayerTopBlueLight'].copy()
blue.thumbnail((1050, 315))
blue_tile = Image.new('RGBA', (1050, 320), '#202020')
blue_tile.alpha_composite(blue, ((1050 - blue.width) // 2, (320 - blue.height) // 2))
sheet.paste(blue_tile.convert('RGB'), (25, 450))
draw.text((25, 430), 'PlayerTopBlueLight / DXT5 / -910000000000002', fill='white')
sheet.save(OUT / 'bundle纹理解码预览.png')

manifest = {
    'source_bundle': str(SOURCE), 'source_bundle_sha256': source_hash,
    'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
    'serialized_file': asset_file.name,
    'template_path_id': TEMPLATE_ID,
    'original_resources_preserved': len(original_hashes) - 1,
    'textures': records,
}
(OUT / '资源ID对照.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
mapping_lines = '\n'.join(f"{r['name']}：{r['path_id']}；{r['size'][0]} × {r['size'][1]}" for r in records)
readme = f'''ui-backgrounds_assets_common.bundle 新增六张纹理 v9

{mapping_lines}

六张图片均按照原资源 -910000000000001 的 Texture2D 设置写入：
DXT5（格式编号12），1级Mip，保持各自原始尺寸；透明通道保留。
过滤、Wrap、颜色空间和内嵌存储方式沿用原纹理设置。
DXT5是有损压缩，边缘和颜色会有少量压缩误差。

备份皮肤 packages 内的 ui-backgrounds_assets_common.bundle，再用本包同名文件替换。
本次只将图片加入资源包，未修改界面引用。
文件内新增了对应的资源名称和预加载条目。
界面跨文件引用时，序列化文件为 {asset_file.name}，Path ID 使用上表；File ID 取决于界面bundle的Externals列表。

检查结果：已重读成品bundle，六张图片均可解码，尺寸、方向、透明通道、DXT5格式和ID已核对。
原有纹理及其他资源的原始字节均保持不变，仅新增六个资源并更新包内资源目录。
源packages文件未覆盖。
'''
(OUT / '安装与资源说明.txt').write_text(readme, encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(destination), 'zip': str(archive),
                  'format': 'DXT5', 'textures': records,
                  'original_resources_preserved': len(original_hashes) - 1}, ensure_ascii=True))
