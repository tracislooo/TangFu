from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import cv2
import numpy as np
import openpyxl
from PIL import Image

DATA = Path('K:/桌面/27skin/PICTURE/country-new')
MAPS = ROOT / 'country-new-images-20261117/sources'
HANDOVER = Path('G:/Doc/deepseek-harness/default-workspace/tt')


def features(path, transparent, china):
    rgba = np.array(Image.open(path).convert('RGBA'))
    rgb = rgba[:, :, :3]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = (hsv[:, :, 1] > 65) & (hsv[:, :, 0] > 3) & (hsv[:, :, 0] < 45)
    if transparent:
        mask &= rgba[:, :, 3] > 180
    if china:
        mask[850:, :] = False
        mask[:, 1120:] = False
    return cv2.SIFT_create(nfeatures=10000).detectAndCompute(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), mask.astype('uint8') * 255)


def calibrate_country(source, target, china):
    old_points, old_desc = features(source, False, china)
    new_points, new_desc = features(target, True, china)
    matches = [a for a, b in cv2.BFMatcher().knnMatch(old_desc, new_desc, k=2) if a.distance < .74 * b.distance]
    if len(matches) < 3:
        return {'inliers': 0}
    start = np.float32([old_points[m.queryIdx].pt for m in matches])
    end = np.float32([new_points[m.trainIdx].pt for m in matches])
    matrix, inliers = cv2.estimateAffine2D(start, end, method=cv2.RANSAC, ransacReprojThreshold=2.5, maxIters=5000)
    if matrix is None:
        return {'inliers': 0}
    chosen = inliers.ravel().astype(bool)
    error = np.linalg.norm(start @ matrix[:, :2].T + matrix[:, 2] - end, axis=1)
    return dict(matrix=matrix.tolist(), matches=len(matches), inliers=int(chosen.sum()),
                median_error=float(np.median(error[chosen])), p95_error=float(np.percentile(error[chosen], 95)),
                source_extent=np.ptp(start[chosen], axis=0).tolist(), source=str(source), target=str(target))


def mercator(latitude):
    return np.degrees(np.arcsinh(np.tan(np.radians(latitude))))


def calibrate_world():
    rgba = np.array(Image.open(MAPS / 'world.png').convert('RGBA'))
    land = (rgba[:, :, 3] > 127).astype('uint8')
    coast = land - cv2.erode(land, np.ones((3, 3), 'uint8'))
    distance = cv2.distanceTransform(1 - coast, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    data = json.loads((HANDOVER / 'geo_tools/_ne50_coastline.geojson').read_text('utf8'))
    lines = [line for item in data['features'] for line in
             ([item['geometry']['coordinates']] if item['geometry']['type'] == 'LineString' else item['geometry']['coordinates'])]
    points = np.vstack(lines)
    lon, lat = points[(abs(points[:, 0]) < 178) & (points[:, 1] > -57) & (points[:, 1] < 83)][::3].T
    best = None
    for kind, ordinate in [('mercator', mercator(lat)), ('equirectangular', lat)]:
        def error(params):
            origin_x, origin_y, scale_x, scale_y = params
            x = (origin_x + scale_x * lon).round().astype(int)
            y = (origin_y - scale_y * ordinate).round().astype(int)
            return np.clip(distance[y.clip(0, 1079), x.clip(0, 1919)], 0, 35).mean() + 100 * np.mean((y < 0) | (y >= 1080) | (x < 0) | (x >= 1920))

        seeds = [np.array([ox, oy, sx, sy], dtype=float) for ox in (625, 660) for oy in (665, 690)
                 for sx in (3.4, 3.55) for sy in (3.2, 3.5, 4.5, 5.2)]
        candidates = sorted(((error(seed), index, seed) for index, seed in enumerate(seeds)), key=lambda v: v[0])[:4]
        for score, _, params in candidates:
            for scale in (1, .5, .25, .125, .0625, .03125):
                step = np.array([14, 14, .14, .14]) * scale
                for _ in range(25):
                    chosen = min([params + shift for shift in np.vstack([np.diag(step), -np.diag(step)])], key=error)
                    improved = error(chosen)
                    if improved >= score:
                        break
                    score, params = improved, chosen
            if best is None or score < best['mean_clipped_coast_error']:
                best = dict(projection=kind, transform=params.tolist(), mean_clipped_coast_error=float(score))
    return best


if __name__ == '__main__':
    book = openpyxl.load_workbook(DATA / 'country-new-ID对应表.xlsx', data_only=True, read_only=True)
    result = {}
    for _, old, target, *_ in list(book.worksheets[0].values)[1:]:
        if target == 'world.png':
            continue
        original_name = old.replace('_transparent', '') if target != '110.png' else 'map_China_ninedash.png'
        result[Path(target).stem] = calibrate_country(DATA.parent / 'country' / original_name, MAPS / target, target == '110.png')
        print(target, {k: v for k, v in result[Path(target).stem].items() if k not in {'source', 'target'}}, flush=True)
    result['world'] = calibrate_world()
    print(result['world'], flush=True)
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2, ensure_ascii=False), 'utf8')
