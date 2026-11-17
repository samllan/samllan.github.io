"""Generate two labelled illustrations using synthetic inputs."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image


EXAMPLES = Path(__file__).resolve().parents[1] / "site" / "research" / "examples"
sys.path.insert(0, str(EXAMPLES))
from map_patch_scores import score_grid
from render_score_overlay import render_overlay


def image_scales():
    rng = np.random.default_rng(14)
    y, x = np.mgrid[:140, :196]
    scan = np.full((*x.shape, 3), (244, 236, 220), dtype=np.uint8)
    for cx, cy in ((43, 42), (99, 42), (155, 42), (43, 96), (99, 96), (155, 96)):
        core = (x - cx) ** 2 + (y - cy) ** 2 <= 22**2
        scatter = rng.integers(-20, 21, size=(int(core.sum()), 1))
        scan[core] = np.array([195, 132, 158]) + scatter
        for dx, dy in rng.integers(-14, 15, size=(27, 2)):
            cell = (x - cx - dx) ** 2 + (y - cy - dy) ** 2 <= 1.5**2
            scan[cell & core] = (110, 65, 103)
    core = scan[74:119, 77:122]
    patch = core[12:29, 12:29]
    local_y, local_x = np.argwhere(np.all(core[7:37, 7:37] == [110, 65, 103], axis=2))[0] + 7
    cell = core[local_y - 3:local_y + 4, local_x - 3:local_x + 4]

    figure = plt.figure(figsize=(9, 3.65), facecolor="#f8f6ef")
    layout = ((0.05, 0.13, 0.24, 0.71), (0.39, 0.13, 0.22, 0.71),
              (0.72, 0.54, 0.21, 0.37), (0.72, 0.05, 0.21, 0.37))
    axes = [figure.add_axes(position) for position in layout]
    for axis, pixels, name in zip(axes, (scan, core, patch, cell),
                                  ("Tissue scan", "Core C01", "Patch from C01", "Cell from C01")):
        axis.imshow(pixels, interpolation="nearest")
        axis.set_title(name, loc="left", color="#244035", fontsize=13, pad=7)
        axis.set_axis_off()
    axes[0].add_patch(Rectangle((76.5, 73.5), 45, 45, fill=False, edgecolor="#205841", linewidth=2))
    axes[0].text(77, 126, "C01", fontsize=9, color="#205841", fontweight="bold")
    axes[1].add_patch(Rectangle((11.5, 11.5), 17, 17, fill=False, edgecolor="#205841", linewidth=2))
    axes[1].add_patch(Rectangle((local_x - 3.5, local_y - 3.5), 7, 7, fill=False, edgecolor="#f8eaae", linewidth=2))
    figure.text(.315, .49, "→", fontsize=21, color="#426454")
    figure.text(.635, .63, "↗", fontsize=21, color="#426454")
    figure.text(.635, .31, "↘", fontsize=21, color="#426454")
    figure.savefig(EXAMPLES / "image_scales.png", dpi=145)
    plt.close(figure)


def score_overlay():
    sample = Image.new("RGB", (64, 48), "#634b68")
    patches = [(8, 8, 36, 28, 0.3), (20, 18, 56, 40, 0.8)]
    scores = score_grid(sample.size, patches)
    overlay = render_overlay(sample, scores)
    figure, axes = plt.subplots(1, 2, figsize=(8.6, 3.7), facecolor="#f8f6ef")
    figure.subplots_adjust(left=.045, right=.955, top=.86, bottom=.25, wspace=.12)
    for axis, image, name in zip(axes, (sample, overlay), ("Input and patch boundaries", "Score overlay")):
        axis.imshow(image, interpolation="nearest")
        axis.set_title(name, loc="left", color="#244035", fontsize=13, pad=7)
        axis.set_axis_off()
    for left, top, right, bottom, _ in patches:
        axes[0].add_patch(Rectangle((left - .5, top - .5), right - left, bottom - top,
                                   fill=False, edgecolor="#f8eaae", linewidth=1.5))
    axes[1].contourf(np.ma.masked_where(np.isfinite(scores), np.ones_like(scores)),
                     levels=(0.5, 1.5), colors="none", hatches=("///",))
    colors = render_overlay(Image.new("RGB", (4, 1), "#634b68"),
                            np.array([[.3, .55, .8, np.nan]]))
    for i, label in enumerate(("0.30 · lower", "0.55 · overlap", "0.80 · higher", "No score")):
        x = .052 + .235 * i
        color = np.asarray(colors)[0, i, :3] / 255
        figure.patches.append(Rectangle((x, .12), .025, .04, transform=figure.transFigure,
                                        facecolor=color, hatch="///" if i == 3 else None))
        figure.text(x + .034, .126, label, fontsize=10, color="#244035")
    figure.savefig(EXAMPLES / "score_overlay_example.png", dpi=145)
    for axis, side in zip(axes, ("input", "output")):
        axis.title.set_visible(False)
        clip = axis.get_window_extent().transformed(figure.dpi_scale_trans.inverted())
        figure.savefig(EXAMPLES / f"score_overlay_{side}.png", dpi=145, bbox_inches=clip)
    plt.close(figure)


if __name__ == "__main__":
    image_scales()
    score_overlay()
