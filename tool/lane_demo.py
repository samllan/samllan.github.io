"""Reproducible educational line-fit example, added for the 2026 portfolio.

Input: the Udacity course image in site/assets/lane-input.jpg.
Requires NumPy and Pillow; these are not needed to build or view the website.
This is a new illustrative implementation, not a claim that the old notebook ran.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

assets = Path(__file__).resolve().parents[1] / 'site' / 'assets'
image = Image.open(assets / 'lane-input.jpg').convert('RGB')
pixels = np.asarray(image)
height, width = pixels.shape[:2]
y, x = np.indices((height, width))
white = np.all(pixels > 180, axis=2)
yellow = (pixels[:, :, 0] > 150) & (pixels[:, :, 1] > 130) & (pixels[:, :, 2] < 140)
top, bottom = int(height * .61), int(height * .94)
spread = (y - top) / max(1, bottom - top)
road = (y >= top) & (y <= bottom) & (x > width * (.45 - .37 * spread)) & (x < width * (.55 + .37 * spread))
mask = (white | yellow) & road
overlay = image.copy()
draw = ImageDraw.Draw(overlay)
for side in (x < width * .5, x >= width * .5):
    rows, columns = [], []
    for row in range(top, bottom, 6):
        yy, xx = np.where(mask[row:row + 6] & side[row:row + 6])
        if len(xx) >= 3:
            rows.append(row + float(np.median(yy)))
            columns.append(float(np.median(xx)))
    if len(rows) < 4:
        raise RuntimeError('Not enough lane-marking evidence for this example')
    slope, intercept = np.polyfit(rows, columns, 1)
    endpoints = [(int(slope * row + intercept), row) for row in (top, bottom)]
    draw.line(endpoints, fill=(70, 245, 185), width=max(5, width // 130))
    for point in endpoints:
        draw.ellipse((point[0]-5, point[1]-5, point[0]+5, point[1]+5), fill='white')
    print('Fitted endpoints:', endpoints)
overlay.save(assets / 'lane-overlay.jpg', quality=92)
