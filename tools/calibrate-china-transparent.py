from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.codex-deps'))
import cv2
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'exports/China-top-two-leagues-2026/map_China_ninedash.png'
target = Path('K:/桌面/27skin/PICTURE/country-new/map_China_transparent.png')
output = root / 'analysis/china-transparent-registration.json'

old = np.array(Image.open(source).convert('RGB'))
new = np.array(Image.open(target).convert('RGB'))

def features(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = ((hsv[:, :, 1] > 80) & (hsv[:, :, 0] > 5) & (hsv[:, :, 0] < 40)).astype('uint8') * 255
    mask[850:, :] = 0
    mask[:, 1120:] = 0
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return cv2.SIFT_create(nfeatures=12000).detectAndCompute(gray, mask)

old_points, old_descriptors = features(old)
new_points, new_descriptors = features(new)
matches = cv2.BFMatcher().knnMatch(old_descriptors, new_descriptors, k=2)
good = [a for a, b in matches if a.distance < .7 * b.distance]
start = np.float32([old_points[m.queryIdx].pt for m in good])
end = np.float32([new_points[m.trainIdx].pt for m in good])
matrix, inliers = cv2.estimateAffine2D(start, end, method=cv2.RANSAC, ransacReprojThreshold=3)
assert matrix is not None
selected = inliers.ravel().astype(bool)
errors = np.linalg.norm(start @ matrix[:, :2].T + matrix[:, 2] - end, axis=1)
assert selected.sum() >= 50
assert np.median(errors[selected]) < 2
report = {
    'source': str(source), 'target': str(target), 'image_size': [1920, 1080],
    'model': 'affine image registration of shared terrain features',
    'matrix_old_to_new': matrix.tolist(), 'feature_matches': len(good),
    'inliers': int(selected.sum()),
    'inlier_median_error_px': float(np.median(errors[selected])),
    'inlier_p95_error_px': float(np.percentile(errors[selected], 95)),
    'matched_extent_old': [start[selected].min(axis=0).tolist(), start[selected].max(axis=0).tolist()],
}
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=True, indent=2))
