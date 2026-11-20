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
from PIL import Image, ImageChops, ImageStat

SOURCE = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
PNG = Path('K:/桌面/27skin/PlayerTopBlueLight.png')
OUT = ROOT / '替换BlueLight-v10-DXT5'
TARGET_ID = -910000000000002

original_file_hash = hashlib.sha256(SOURCE.read_bytes()).digest()
env = UnityPy.load(str(SOURCE))
objects = {o.path_id: o for o in env.objects}
original_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
obj = objects[TARGET_ID]
original = obj.read_typetree()
assert obj.type.name == 'Texture2D'
assert original['m_Name'] == 'PlayerTopBlueLight'
assert original['m_TextureFormat'] == 12
assert original['m_MipCount'] == 1
assert all(-910000000000000 - i in objects for i in range(1, 8))
with Image.open(PNG) as png:
    png.load()
    image = png.convert('RGBA')
pixels, format_id = image_to_texture2d(image, 12, obj.platform, original['m_PlatformBlob'])
assert int(format_id) == 12
data = copy.deepcopy(original)
data.update(m_Width=image.width, m_Height=image.height, m_CompleteImageSize=len(pixels))
data['image data'] = pixels
data['m_StreamData'] = {'offset': 0, 'size': 0, 'path': ''}
obj.save_typetree(data)

OUT.mkdir(exist_ok=True)
destination = OUT / SOURCE.name
destination.write_bytes(env.file.save(packer='lz4'))
check = UnityPy.load(str(destination))
check_objects = {o.path_id: o for o in check.objects}
assert set(check_objects) == set(objects)
for pid, digest in original_hashes.items():
    if pid != TARGET_ID:
        assert hashlib.sha256(check_objects[pid].get_raw_data()).digest() == digest, pid
assert check_objects[TARGET_ID].read_typetree() == data
assert hashlib.sha256(SOURCE.read_bytes()).digest() == original_file_hash
decoded = check_objects[TARGET_ID].read().image.convert('RGBA')
assert decoded.size == image.size
rms = ImageStat.Stat(ImageChops.difference(decoded, image)).rms
assert rms[3] < 20
assert sum(rms) < sum(ImageStat.Stat(ImageChops.difference(decoded, image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
assert abs(decoded.getchannel('A').getextrema()[0] - image.getchannel('A').getextrema()[0]) <= 3
decoded.save(OUT / 'PlayerTopBlueLight-包内解码预览.png')
report = {
    'source_bundle': str(SOURCE), 'source_bundle_sha256': original_file_hash.hex(),
    'source_image': str(PNG), 'source_image_sha256': hashlib.sha256(PNG.read_bytes()).hexdigest(),
    'target_name': data['m_Name'], 'path_id': TARGET_ID,
    'texture_format': 'DXT5', 'texture_format_id': 12,
    'size': list(decoded.size), 'source_alpha_range': image.getchannel('A').getextrema(),
    'decoded_alpha_range': decoded.getchannel('A').getextrema(),
    'rgba_rms_error': rms, 'other_resources_unchanged': len(original_hashes) - 1,
    'output_bundle_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
}
(OUT / '替换记录.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / '安装说明.txt').write_text('''PlayerTopBlueLight 图片替换 v10

替换资源：PlayerTopBlueLight，Path ID -910000000000002。
使用本次提供的 K:/桌面/27skin/PlayerTopBlueLight.png。
保持DXT5格式、原纹理设置、资源名、ID和所有界面引用。
其余图片与资源没有修改。

备份皮肤 packages 内的 ui-backgrounds_assets_common.bundle，用本目录同名文件替换。
附带预览是从生成的bundle实际解码的图片。
已验证成品可解码、尺寸和透明通道，并逐个核对其余资源原始字节未变。
源packages文件未覆盖。
''', encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in OUT.iterdir():
        if file.is_file():
            z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps(report, ensure_ascii=True))
