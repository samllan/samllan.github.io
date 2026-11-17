"""Render a small error comparison from a saved predictions table."""
import argparse
from html import escape
from math import ceil, floor, isfinite, log10
from pathlib import Path

from build_grading_table import build_table


def render_figure(rows, title="Mean absolute grading error"):
    if not rows or any(not isfinite(error) or error < 0 for _, _, error in rows):
        raise ValueError("Require finite nonnegative errors for one or more rows")
    width, height = 680, 150 + len(rows) * 37
    maximum = max(error for _, _, error in rows) or 1.0
    step = 10 ** floor(log10(maximum))
    ceiling = ceil(maximum / step) * step
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{escape(title)} (synthetic rerun)</title>",
        '<rect width="100%" height="100%" rx="8" fill="#f8f6ed"/>',
        '<g font-family="system-ui, sans-serif" fill="#243e31">',
        f'<text x="24" y="33" font-size="21">{escape(title)}</text>',
        '<text x="24" y="55" font-size="13">Synthetic rerun · lower is better</text>',
    ]
    for index, (label, count, error) in enumerate(rows):
        y = 72 + index * 37
        length = error / ceiling * 330
        parts.extend((
            f'<text x="24" y="{y + 18}" font-size="15">{escape(label.title())}</text>',
            f'<rect x="142" y="{y}" width="330" height="24" rx="3" fill="#e2e8dc"/>',
            f'<rect x="142" y="{y}" width="{length:.1f}" height="24" rx="3" fill="#527c67"/>',
            f'<text x="490" y="{y + 18}" font-size="14">{error:.3f} (n={count})</text>',
        ))
    axis_y = 72 + len(rows) * 37
    parts.append(f'<path d="M142 {axis_y}h330" stroke="#718477"/>')
    for fraction in (0, 0.5, 1):
        x = 142 + 330 * fraction
        parts.append(f'<path d="M{x:g} {axis_y}v5" stroke="#718477"/>')
        parts.append(f'<text x="{x:g}" y="{axis_y + 23}" text-anchor="middle" font-size="13">{fraction * ceiling:g}</text>')
    parts.append(f'<text x="307" y="{axis_y + 48}" text-anchor="middle" font-size="13">Grade points</text>')
    return "\n".join([*parts, "</g></svg>", ""])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, nargs="?")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.predictions:
        with args.predictions.open(encoding="utf-8", newline="") as stream:
            rows = build_table(stream)
    else:
        rows = [("core", 6, 0.35), ("patch", 6, 0.24), ("cell", 6, 0.32)]
    figure = render_figure(rows)
    if args.output:
        args.output.write_text(figure, encoding="utf-8")
    else:
        print(figure, end="")
