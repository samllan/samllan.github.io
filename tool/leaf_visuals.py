"""Colourful SVG visuals and compact tables for each experiment leaf."""
import csv
from html import escape
from urllib.parse import quote


def table_cell(heading, body, *, class_name=""):
    css_class = f' class="{escape(class_name, quote=True)}"' if class_name else ""
    return f'<td role="cell" data-label="{escape(heading, quote=True)}"{css_class}>{body}</td>'


def mini_table(title, headings, rows, *, note="", highlight_row=None):
    cols = "".join(f'<th scope="col" role="columnheader">{escape(str(h))}</th>' for h in headings)
    body = []
    for idx, row in enumerate(rows):
        row_class = ' class="lab-row-highlight"' if idx == highlight_row else ""
        cells = "".join(table_cell(str(heading), escape(str(cell))) for heading, cell in zip(headings, row))
        body.append(f'<tr role="row"{row_class}>{cells}</tr>')
    caption = f"<caption>{escape(title)}</caption>" if title else ""
    note_html = f'<p class="lab-card-note">{escape(note)}</p>' if note else ""
    body_html = "".join(body)
    return (
        f'<div class="lab-evidence-table"><table class="lab-result-table lab-stack-table" role="table">'
        f'{caption}<thead role="rowgroup"><tr role="row">{cols}</tr></thead>'
        f'<tbody role="rowgroup">{body_html}</tbody></table>{note_html}</div>'
    )


def metric_bars(title, items, *, max_value, unit="", note=""):
    bars = "".join(
        f'<li><span>{escape(label)}</span>'
        f'<meter min="0" max="{max_value}" value="{value:g}" aria-label="{escape(label, quote=True)}"></meter>'
        f'<strong>{escape(display if display is not None else f"{value:g}{unit}")}</strong></li>'
        for label, value, display in items
    )
    heading = f'<p class="lab-card-note">{escape(title)}</p>' if title else ""
    foot = f'<p class="lab-card-note">{escape(note)}</p>' if note else ""
    return f'{heading}<ul class="lab-bars">{bars}</ul>{foot}'


def stat_cards(pairs, *, note=""):
    items = "".join(
        f"<div><dt>{escape(str(label))}</dt><dd>{escape(str(value))}</dd></div>"
        for label, value in pairs
    )
    foot = f'<p class="lab-card-note">{escape(note)}</p>' if note else ""
    return f'<dl class="lab-values">{items}</dl>{foot}'


def figure_tag(filename, alt, caption, *size):
    dimensions = f' width="{int(size[0])}" height="{int(size[1])}"' if size else ""
    return (
        f'<figure class="lab-figure"><img src="examples/{quote(filename)}" alt="{escape(alt, quote=True)}" '
        f'loading="lazy"{dimensions}><figcaption>{escape(caption)}</figcaption></figure>'
    )


def chart_caption(title, note, inside):
    caption = f'<figcaption>{escape(title)}</figcaption>' if title else ""
    foot = f'<p class="lab-card-note">{escape(note)}</p>' if note else ""
    return f'<figure class="lab-chart">{caption}{inside}{foot}</figure>'


def swatch_chart(title, swatches, *, note=""):
    items = "".join(
        f'<div style="--swatch:{fill};--swatch-line:{stroke}">'
        f'<dt>{escape(label)}</dt><dd>{escape(sublabel)}</dd></div>'
        for label, sublabel, fill, stroke in swatches
    )
    return chart_caption(title, note, f'<dl class="lab-swatches">{items}</dl>')


def chart_bar(label, value, colour, *, start, width, signed=False):
    axis = " lab-chart-axis" if signed else ""
    return (
        f'<li><span>{escape(label)}</span><strong>{escape(value)}</strong>'
        f'<span class="lab-chart-track{axis}" aria-hidden="true">'
        f'<i style="--bar-start:{start:.3f}%;--bar-width:{width:.3f}%;--bar-colour:{colour}"></i>'
        f'</span></li>'
    )


def bar_chart(title, bars, *, max_val=1.0, note=""):
    items = "".join(
        chart_bar(label, display, colour, start=0, width=100 * max(0, min(1, value / max_val)))
        for label, value, display, colour in bars
    )
    return chart_caption(title, note, f'<ul class="lab-chart-bars">{items}</ul>')


def diverging_chart(title, rows, *, scale=1.0, note=""):
    items = []
    for label, value, display in rows:
        width = 50 * min(1, abs(value) / scale)
        start = 50 - width if value < 0 else 50
        colour = "#b3472a" if value < 0 else "#2f6f55"
        items.append(chart_bar(label, display, colour, start=start, width=width, signed=True))
    return chart_caption(title, note, '<ul class="lab-chart-bars">' + "".join(items) + '</ul>')


def leaf_visuals(filename, examples, demo, captured):
    # --- Overview ---
    if filename == "research_questions.md":
        inp = figure_tag(
            "image_scales.png",
            "Generated examples of a scan, a core, a patch and a cell crop",
            "Synthetic schematic: one whole-slide scan branches into a 5,000 × 5,000 px core (C01), patches and individual cells.",
        )
        out = (
            swatch_chart(
                "Three biological scales tested across two clinical tasks",
                (
                    ("Core view", "5,000 × 5,000 px", "#e6c5d4", "#8a4b68"),
                    ("Patch view", "224 × 224 px tiles", "#d5e5dc", "#205841"),
                    ("Cell view", "9.1M single cells", "#f7e7ba", "#8a5a19"),
                ),
            )
            + '<div class="lab-route-cards">'
            '<div class="lab-route-card"><p class="lab-card-note"><strong>1. Prepare tissue scales</strong> — Can multi-gigabyte scans become traceable, compact regions on disk?</p>'
            '<p class="lab-next"><a href="#crop/crop_benchmark.csv">1-click cropping (6 s → 3 s) →</a><a href="#storage/compare_image_encodings.py">WebP compression (−86.5%) →</a></p></div>'
            '<div class="lab-route-card"><p class="lab-card-note"><strong>2. Task 1: Staining grades</strong> — Which scale best matches expert IHC scores (0–3)?</p>'
            '<p class="lab-next"><a href="#figures/run_grading_example.py">Trace Case S02 to chart →</a><a href="#agreement/compare_assessor_errors.py">0.238 model MAE vs 0.382 rater gap →</a></p></div>'
            '<div class="lab-route-card"><p class="lab-card-note"><strong>3. Task 2: Subtype labels</strong> — Which pooled representations best separate ABC vs GCB subtypes?</p>'
            '<p class="lab-next"><a href="#validation/summarise_validation.py">0.992 AUC subtype validation →</a><a href="#explain/test_mask_score_changes.py">Dimming & perturbation controls →</a></p></div>'
            "</div>"
        )
        return inp, out

    if filename == "README.md":
        if (examples / "trial_waits.csv").is_file():
            return (
                swatch_chart(
                    "Four JSON/Markdown files define any logbook project",
                    (
                        ("project.json", "Title & links", "#e2e8dc", "#205841"),
                        ("goals.json", "Tree & stories", "#d5e5dc", "#205841"),
                        ("leaf_details", "Inputs & links", "#f7e7ba", "#8a5a19"),
                    ),
                ),
                mini_table(
                    "Files that define a logbook project folder",
                    ("Project file", "Role"),
                    (
                        ("project.json", "Sets project title, description, back link and source repository URL."),
                        ("goals.json", "Defines the goal hierarchy, narrative stories, tables, revisions and file lists."),
                        ("leaf_details.json", "Holds per-entry titles, inputs, questions, methods and upstream links."),
                        ("row_examples.json", "Stores captured script outputs and headline metric badges."),
                    ),
                ),
            )
        inp = (
            '<p class="lab-card-note"><strong>Dependencies</strong> · Python 3.9+ with NumPy and Pillow:</p>'
            '<pre class="lab-command">python -m pip install numpy pillow\npython run_grading_example.py --output grading-demo</pre>'
            + swatch_chart(
                "One command replays the full grading pipeline",
                (
                    ("1. Splits", "splits.csv", "#e2e8dc", "#527c67"),
                    ("2. Predict", "36 held-out rows", "#d5e5dc", "#205841"),
                    ("3. Chart", "grading_figure.svg", "#f7e7ba", "#8a5a19"),
                ),
            )
        )
        out = mini_table(
            "First files to inspect after running the grading example",
            ("Generated file", "What it lets you check"),
            (
                ("grading-demo/case_trace.csv", "Follow case S02 from two assessor ratings (2 and 3) to its 2.500 reference and patch error."),
                ("grading-demo/predictions.csv", "Verify that all 36 predictions (12 cases × 3 scales) were scored on held-out folds."),
                ("grading-demo/grading_figure.svg", "Compare the resulting mean absolute error bars across core, patch and cell scales."),
            ),
            note="Follow up with python build_grading_table.py grading-demo/predictions.csv to recompute the scale summary.",
        )
        return inp, out

    # --- Pilot example ---
    if filename == "trial_waits.csv":
        return (
            bar_chart(
                "Observed visitor wait times (minutes, lower is faster)",
                (("Paper list (AM)", 8.0, "8 min median", "#8a5a19"), ("Arrival list (PM)", 4.0, "4 min median", "#205841")),
                max_val=10.0,
            ),
            mini_table(
                "Recorded wait times (fictional pilot)",
                ("Method", "Session", "Observed waits (min)", "Median"),
                (("Paper list", "Morning", "7, 8, 9, 12", "8 min"), ("Prepared arrival list", "Afternoon", "3, 4, 4, 6", "4 min")),
            ),
        )
    if filename == "summarise_waits.py":
        return (
            swatch_chart(
                "Two groups of 4 observations",
                (("Paper list", "7, 8, 9, 12 min", "#f7e7ba", "#8a5a19"), ("Prepared list", "3, 4, 4, 6 min", "#d5e5dc", "#205841")),
            ),
            bar_chart(
                "Recomputed median wait from CSV",
                (("Paper list", 8.0, "8 min (n=4)", "#8a5a19"), ("Prepared list", 4.0, "4 min (n=4)", "#205841")),
                max_val=10.0,
                note="The session notes show the two methods ran at different times of day.",
            ),
        )
    if filename == "decision.md":
        return (
            swatch_chart(
                "Confounded pilot vs balanced follow-up design",
                (
                    ("Pilot 1", "AM vs PM (confounded)", "#f5d0c5", "#b3472a"),
                    ("Pilot 2", "Matched time slots", "#d5e5dc", "#205841"),
                ),
            ),
            mini_table(
                "What changed between the first pilot summary and the review",
                ("Stage", "Observation", "Conclusion"),
                (
                    ("Initial pilot", "Median wait dropped from 8 min to 4 min", "Draft decision: adopt prepared arrival list"),
                    ("Session audit", "Paper list ran in morning; arrival list in afternoon", "Revised decision: alternate methods in matched time slots"),
                ),
                highlight_row=1,
            ),
        )

    # --- Goal: crop (Locate tissue cores) ---
    if filename == "select_core_rectangles.py":
        inp = (
            '<svg viewBox="0 0 340 116" class="lab-diagram" role="img" aria-label="Two hand-drawn boxes of slightly different sizes around tissue cores">'
            '<rect width="340" height="116" rx="6" fill="#f7f4ea"/>'
            '<circle cx="78" cy="60" r="32" fill="#c98ca7" opacity="0.85"/>'
            '<rect x="38" y="24" width="76" height="80" fill="none" stroke="#205841" stroke-width="2" stroke-dasharray="4 2"/>'
            '<text x="38" y="19" font-size="10.5" fill="#205841" font-weight="bold">1A · 122 × 128 preview px</text>'
            '<circle cx="222" cy="58" r="32" fill="#c98ca7" opacity="0.85"/>'
            '<rect x="178" y="22" width="84" height="74" fill="none" stroke="#8a5a19" stroke-width="2" stroke-dasharray="4 2"/>'
            '<text x="174" y="17" font-size="10.5" fill="#8a5a19" font-weight="bold">1B · 129 × 123 preview px</text>'
            "</svg>"
            '<p class="lab-card-note">Preview zoom: <code>1.25×</code> · Scan multiplier: <code>50×</code> (scale factor <code>40×</code>).</p>'
        )
        out = (
            swatch_chart(
                "Resulting full-scan crops have uneven pixel dimensions",
                (
                    ("Core 1A", "4,880 × 5,120 px (tall)", "#e6c5d4", "#205841"),
                    ("Core 1B", "5,160 × 4,920 px (wide)", "#f7e7ba", "#8a5a19"),
                    ("6 s / core", "1.00 prec & recall", "#e2e8dc", "#527c67"),
                ),
            )
            + mini_table(
                "Scaled full-scan bounds from hand-drawn boxes",
                ("Core", "Preview (x, y, w, h)", "Full-scan bounds (px)", "Crop size"),
                (
                    ("1A", "(18, 22, 122, 128)", "(720, 880, 5600, 6000)", "4,880 × 5,120 px"),
                    ("1B", "(164, 20, 129, 123)", "(6560, 800, 11720, 5720)", "5,160 × 4,920 px"),
                ),
            )
        )
        return inp, out

    if filename == "interpolate_core_grid.py":
        inp = (
            '<svg viewBox="0 0 360 126" class="lab-diagram" role="img" aria-label="Tilted microarray grid projected from two reference corners, showing one drifted core">'
            '<rect width="360" height="126" rx="6" fill="#f7f4ea"/>'
            '<line x1="55" y1="22" x2="67" y2="104" stroke="#6b8577" stroke-width="1.5" stroke-dasharray="3 3"/>'
            '<circle cx="55" cy="22" r="12" fill="#c98ca7"/><circle cx="55" cy="22" r="3" fill="#1b3126"/>'
            '<text x="72" y="26" font-size="10.5" fill="#1b3126">1A corner click (20, 20)</text>'
            '<circle cx="61" cy="63" r="12" fill="#c98ca7"/>'
            '<rect x="46" y="48" width="30" height="30" fill="none" stroke="#205841" stroke-width="1.5"/>'
            '<circle cx="67" cy="104" r="12" fill="#c98ca7"/><circle cx="67" cy="104" r="3" fill="#1b3126"/>'
            '<text x="84" y="108" font-size="10.5" fill="#1b3126">3A corner click (26, 80)</text>'
            '<circle cx="222" cy="54" r="12" fill="#c98ca7"/>'
            '<rect x="195" y="45" width="30" height="30" fill="none" stroke="#b3472a" stroke-width="2"/>'
            '<text x="164" y="38" font-size="10.5" fill="#b3472a" font-weight="bold">2B drifted core (5.8 px off grid)</text>'
            "</svg>"
        )
        out = (
            bar_chart(
                "Centre drift from projected grid slot (px)",
                (
                    ("Core 1A (on-grid)", 0.0, "0.0 px", "#205841"),
                    ("Core 2A (on-grid)", 0.0, "0.0 px", "#205841"),
                    ("Core 3A (on-grid)", 0.0, "0.0 px", "#205841"),
                    ("Core 2B (drifted)", 5.8, "5.8 px (clipped)", "#b3472a"),
                ),
                max_val=6.0,
            )
            + mini_table(
                "Projected grid slots vs observed core centres",
                ("Core", "Projected", "Observed", "Drift", "Box (l, t, r, b)"),
                (
                    ("1A–3A", "On axis", "On axis", "0.0 px", "Centred 30 × 30 px"),
                    ("2B", "(53, 47)", "(58, 44)", "5.8 px", "(38, 32, 68, 62) · clipped"),
                ),
                highlight_row=1,
            )
        )
        return inp, out

    if filename == "prepare_image_regions.py" and demo:
        inp, out = demo.split("<!-- output panel -->", 1)
        out += (
            '<p class="lab-card-note"><strong>Two distinct jobs in this module:</strong> '
            "<code>crop_from_clicks</code> locates fixed-size cores on a whole slide (clamping edge clicks inward), "
            "while <code>grid_patches</code> tiles an already extracted core into regular squares.</p>"
        )
        return inp, out

    if filename == "crop_benchmark.csv":
        with (examples / filename).open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        inp = (
            swatch_chart(
                "Four core-extraction strategies evaluated in Thesis Table 2.5",
                (
                    ("Hough", "0.06 s · auto circles", "#f5d0c5", "#b3472a"),
                    ("Tilted grid", "0.5 s · 2 corner clicks", "#f7e7ba", "#8a5a19"),
                    ("Manual rectangles", "6 s · draw each box", "#e2e8dc", "#527c67"),
                    ("1-click crop", "3 s · 1.00 prec/recall", "#d5e5dc", "#205841"),
                ),
                note="Precision = share of extracted regions that were valid cores (no wrong selections). Recall = share of target cores found (no missed cores).",
            )
        )
        chart = bar_chart(
            "Thesis Table 2.5 · Time per tissue core",
            (
                ("Hough (0.89 rec)", 0.06, "0.06 s", "#b3472a"),
                ("Grid (0.98 prec)", 0.5, "0.5 s", "#8a5a19"),
                ("Rectangles (1.00)", 6.0, "6.0 s", "#527c67"),
                ("1-click (1.00 ★)", 3.0, "3.0 s", "#205841"),
            ),
            max_val=6.0,
        )
        table = mini_table(
            "Point-and-click halved manual time (6 s → 3 s) at 1.00 precision and recall",
            ("Approach", "Time / core", "Precision", "Recall", "Manual effort"),
            [(r["approach"], f'{r["seconds_per_sample"]} s', r["precision"], r["recall"], r["manual_intervention"]) for r in rows],
            highlight_row=3,
        )
        return inp, chart + table

    if filename == "record_crop_marks.py":
        inp = (
            '<svg viewBox="0 0 288 118" class="lab-diagram" role="img" aria-label="96 by 72 scan showing Point A at (20, 16) and Rectangle B from (64, 44) to (88, 68)">'
            '<rect x="12" y="10" width="192" height="98" rx="4" fill="#f5f0e2" stroke="#9ab0a2"/>'
            '<circle cx="52" cy="36" r="14" fill="#c98ca7" opacity="0.85"/>'
            '<line x1="46" y1="36" x2="58" y2="36" stroke="#1b3126" stroke-width="2"/>'
            '<line x1="52" y1="30" x2="52" y2="42" stroke="#1b3126" stroke-width="2"/>'
            '<text x="69" y="40" font-size="10.5" fill="#1b3126" font-weight="bold">A · point (20, 16)</text>'
            '<circle cx="164" cy="82" r="14" fill="#c98ca7" opacity="0.85"/>'
            '<rect x="140" y="66" width="48" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<text x="90" y="62" font-size="10.5" fill="#205841" font-weight="bold">B · rect (64, 44)–(88, 68)</text>'
            "</svg>"
        )
        out = (
            swatch_chart(
                "Two annotation schemas stored in one CSV",
                (
                    ("Row A · point", "(x=20, y=16, blank, blank)", "#f7e7ba", "#8a5a19"),
                    ("Row B · rect", "(64, 44, right=88, bottom=68)", "#d5e5dc", "#205841"),
                ),
            )
            + mini_table(
                "Saved annotation CSV rows (demo-scan, 96 × 72 px)",
                ("image", "label", "kind", "x", "y", "right", "bottom"),
                (
                    ("demo-scan", "A", "point", "20", "16", "— (blank)", "— (blank)"),
                    ("demo-scan", "B", "rectangle", "64", "44", "88", "68"),
                ),
                highlight_row=0,
                note="Point rows leave right/bottom blank until fixed-size bounds are computed during extraction.",
            )
        )
        return inp, out

    # --- Goal: prepare (Extract traceable crops) ---
    if filename == "extract_labelled_crops.py":
        inp = (
            '<svg viewBox="0 0 280 112" class="lab-diagram" role="img" aria-label="32 by 24 source scan with two labelled crop boxes">'
            '<rect x="16" y="12" width="160" height="88" rx="4" fill="#b57594"/>'
            '<rect x="26" y="24" width="50" height="40" fill="none" stroke="#fffae7" stroke-width="2"/>'
            '<text x="26" y="20" font-size="10" fill="#fffae7" font-weight="bold">rectangle (2,3)–(12,13)</text>'
            '<rect x="121" y="42" width="40" height="32" fill="none" stroke="#f9ecb2" stroke-width="2"/>'
            '<text x="96" y="38" font-size="10" fill="#f9ecb2" font-weight="bold">crop-01 (21,8)–(29,16)</text>'
            "</svg>"
        )
        out = (
            swatch_chart(
                "Extracted image files paired with crops.csv manifest",
                (
                    ("crop-001.png", "10 × 10 px from (2, 3)", "#e6c5d4", "#205841"),
                    ("crop-002.png", "8 × 8 px from (21, 8)", "#e6c5d4", "#8a5a19"),
                ),
            )
            + mini_table(
                "Generated crops.csv manifest",
                ("image", "label", "file", "Bounds (l, t, r, b)"),
                (
                    ("demo-scan", "rectangle", "crop-001.png", "(2, 3, 12, 13)"),
                    ("demo-scan", "crop-01", "crop-002.png", "(21, 8, 29, 16)"),
                ),
                highlight_row=1,
            )
        )
        return inp, out

    if filename == "map_crop_to_scan.py":
        inp = (
            '<svg viewBox="0 0 330 106" class="lab-diagram" role="img" aria-label="Downsampled crop box mapped by 4x scale and offset">'
            '<rect x="14" y="18" width="84" height="72" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<rect x="34" y="34" width="36" height="36" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<text x="14" y="13" font-size="10.5" fill="#244035" font-weight="bold">4× downsampled crop · box 20 × 20 px</text>'
            '<text x="112" y="50" font-size="12" fill="#205841" font-weight="bold">×4 scale</text>'
            '<text x="108" y="66" font-size="10" fill="#536052">+ (1200, 800)</text>'
            '<rect x="190" y="14" width="116" height="80" rx="4" fill="#f5f0e2" stroke="#527c67"/>'
            '<rect x="216" y="30" width="54" height="48" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<text x="190" y="11" font-size="10.5" fill="#244035" font-weight="bold">Full scan · 80 × 80 px</text>'
            "</svg>"
        )
        out = (
            bar_chart(
                "Pixel width before and after ×4 scan mapping",
                (("Local crop box", 20, "20 × 20 px", "#8a5a19"), ("Full-scan box", 80, "80 × 80 px", "#205841")),
                max_val=80,
            )
            + mini_table(
                "Coordinate transformation: Scan = Origin + 4 × Local",
                ("Corner", "Local (px)", "× 4 scale", "+ Origin (1200, 800)", "Full-scan (px)"),
                (("Left / Top", "(10, 8)", "(40, 32)", "+ (1200, 800)", "(1240, 832)"), ("Right / Bottom", "(30, 28)", "(120, 112)", "+ (1200, 800)", "(1320, 912)")),
            )
        )
        return inp, out

    # --- Goal: patches (Tile into patches) ---
    if filename == "filter_tissue_patches.py":
        inp = (
            '<svg viewBox="0 0 300 100" class="lab-diagram" role="img" aria-label="8 grid squares over a binary tissue mask">'
            '<rect x="16" y="14" width="144" height="72" fill="#eef1eb" stroke="#9ab0a2"/>'
            '<rect x="16" y="14" width="81" height="72" fill="#c98ca7" opacity="0.85"/>'
            '<g fill="none" stroke="#244035" stroke-width="1.2">'
            '<rect x="16" y="14" width="36" height="36"/><rect x="52" y="14" width="36" height="36"/>'
            '<rect x="88" y="14" width="36" height="36"/><rect x="124" y="14" width="36" height="36"/>'
            '<rect x="16" y="50" width="36" height="36"/><rect x="52" y="50" width="36" height="36"/>'
            '<rect x="88" y="50" width="36" height="36"/><rect x="124" y="50" width="36" height="36"/>'
            "</g>"
            '<text x="23" y="36" font-size="10" fill="#1b3126" font-weight="bold">100%</text>'
            '<text x="59" y="36" font-size="10" fill="#1b3126" font-weight="bold">100%</text>'
            '<text x="97" y="36" font-size="10" fill="#b3472a" font-weight="bold">25%</text>'
            '<text x="135" y="36" font-size="10" fill="#536052">0%</text>'
            '<text x="172" y="36" font-size="11" fill="#205841" font-weight="bold">Rule: tissue ≥ 50%</text>'
            '<text x="172" y="54" font-size="10" fill="#205841">✓ 4 squares kept</text>'
            '<text x="172" y="70" font-size="10" fill="#b3472a">✕ 4 squares skipped</text>'
            "</svg>"
        )
        out = bar_chart(
            "Measured tissue coverage across the 4 grid columns (threshold = 50%)",
            (
                ("x=0 (2 patches)", 100, "100% · Keep", "#205841"),
                ("x=4 (2 patches)", 100, "100% · Keep", "#205841"),
                ("x=8 (2 patches)", 25, "25% · Skip", "#b3472a"),
                ("x=12 (2 patches)", 0, "0% · Skip", "#8a998e"),
            ),
            max_val=100,
            note="Columns x=8 (25% tissue) and x=12 (0% background) fall below the 50% threshold and are rejected.",
        )
        return inp, out

    if filename == "summarise_patch_counts.py":
        inp = swatch_chart(
            "Expected cohort cores vs saved patch manifest",
            (
                ("Core A", "2 patches saved", "#d5e5dc", "#205841"),
                ("Core B", "0 patches (alert!)", "#f5d0c5", "#b3472a"),
                ("Core C", "1 patch saved", "#d5e5dc", "#205841"),
            ),
        )
        out = bar_chart(
            "Retained patch count per expected core (keeping B = 0 visible)",
            (
                ("Core A", 2, "2 patches", "#205841"),
                ("Core B (empty)", 0.05, "0 patches ⚠", "#b3472a"),
                ("Core C", 1, "1 patch", "#205841"),
            ),
            max_val=2,
            note="Keeping Core B at 0 verifies it was expected in the cohort but yielded no patches above the tissue threshold.",
        )
        return inp, out

    if filename == "extract_patch_images.py":
        inp = (
            '<svg viewBox="0 0 280 96" class="lab-diagram" role="img" aria-label="16 by 16 core split into four 8 by 8 patches">'
            '<rect x="14" y="12" width="72" height="72" fill="#eef1eb" stroke="#9ab0a2"/>'
            '<rect x="14" y="12" width="54" height="36" fill="#bd7896"/>'
            '<line x1="50" y1="12" x2="50" y2="84" stroke="#244035" stroke-width="1.2"/>'
            '<line x1="14" y1="48" x2="86" y2="48" stroke="#244035" stroke-width="1.2"/>'
            '<rect x="114" y="18" width="44" height="44" fill="#bd7896" stroke="#205841" stroke-width="2"/>'
            '<text x="108" y="76" font-size="10" fill="#244035">patch-x0-y0 (100%)</text>'
            '<rect x="194" y="18" width="44" height="44" fill="#eef1eb" stroke="#205841" stroke-width="2"/>'
            '<rect x="194" y="18" width="22" height="44" fill="#bd7896"/>'
            '<text x="188" y="76" font-size="10" fill="#244035">patch-x8-y0 (50%)</text>'
            "</svg>"
        )
        out = mini_table(
            "Saved patches.csv manifest linking each PNG back to core-1",
            ("core", "file", "Bounds (l, t, r, b)", "tissue_fraction"),
            (
                ("core-1", "patch-x0-y0.png", "(0, 0, 8, 8)", "1.00 (100%)"),
                ("core-1", "patch-x8-y0.png", "(8, 0, 16, 8)", "0.50 (50%)"),
            ),
            note="The top-right square patch-x8-y0.png keeps its exact (8, 0, 16, 8) bounds and 0.50 coverage.",
        )
        return inp, out

    # --- Goal: cells (Segment single cells) ---
    if filename == "extract_cell_crops.py":
        inp = (
            '<svg viewBox="0 0 330 98" class="lab-diagram" role="img" aria-label="Segmented cell regions with two accepted 8x8 cell crops">'
            '<rect x="14" y="12" width="128" height="72" rx="4" fill="#dcdcdc" stroke="#9ab0a2"/>'
            '<circle cx="50" cy="44" r="10" fill="#7d4e6d"/>'
            '<rect x="34" y="28" width="32" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<circle cx="102" cy="54" r="10" fill="#7d4e6d"/>'
            '<rect x="86" y="38" width="32" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<circle cx="24" cy="74" r="2.5" fill="#b3472a"/>'
            '<text x="156" y="30" font-size="10.5" fill="#244035" font-weight="bold">Width filter: 3–7 px</text>'
            '<text x="156" y="48" font-size="10" fill="#205841">✓ Cell 1 &amp; 2 (5 px) → 8×8 crop</text>'
            '<text x="156" y="66" font-size="10" fill="#b3472a">✕ Artefact speck (&lt;3 px) skipped</text>'
            "</svg>"
        )
        out = (
            swatch_chart(
                "Extracted 8 × 8 px cell crops linked to full-scan centres",
                (
                    ("Cell 1 (8×8)", "Scan (249.0, 530.0)", "#e6c5d4", "#205841"),
                    ("Cell 2 (8×8)", "Scan (262.0, 534.0)", "#e6c5d4", "#205841"),
                ),
            )
            + mini_table(
                "Cell crop records (scan origin = 240, 520)",
                ("Instance", "Local centre", "Full-scan centre", "Crop size"),
                (("Cell 1", "(9.0, 10.0)", "(249.0, 530.0)", "8 × 8 px"), ("Cell 2", "(22.0, 14.0)", "(262.0, 534.0)", "8 × 8 px")),
            )
        )
        return inp, out

    if filename == "index_segmented_cells.py":
        inp = (
            '<svg viewBox="0 0 290 92" class="lab-diagram" role="img" aria-label="Core C1 at scan origin (640, 480) containing Cell 1 and Cell 2">'
            '<rect x="12" y="10" width="266" height="72" rx="4" fill="#f7f4ea" stroke="#9ab0a2"/>'
            '<rect x="110" y="18" width="90" height="56" rx="3" fill="#e6c5d4" stroke="#205841" stroke-width="1.5"/>'
            '<text x="18" y="30" font-size="10" fill="#536052">Scan (0, 0)</text>'
            '<text x="114" y="30" font-size="9.5" fill="#1b3126" font-weight="bold">Core C1 (640, 480)</text>'
            '<circle cx="136" cy="42" r="4" fill="#205841"/><text x="143" y="45" font-size="9.5" fill="#205841">Cell 1 (+29,+18)</text>'
            '<circle cx="158" cy="62" r="4" fill="#8a5a19"/><text x="165" y="65" font-size="9.5" fill="#8a5a19">Cell 2 (+61,+70)</text>'
            "</svg>"
        )
        out = mini_table(
            "Global scan coordinates (Scan = Core Origin + Local Cell Offset)",
            ("Cell key", "Core origin", "Local offset", "Global scan (x, y)"),
            (
                ("C1 · Cell 1", "(640, 480)", "+ (29, 18)", "(669, 498) px"),
                ("C1 · Cell 2", "(640, 480)", "+ (61, 70)", "(701, 550) px"),
            ),
        )
        return inp, out

    if filename == "package_cell_arrays.py":
        inp = swatch_chart(
            "Three aligned per-cell arrays before packaging",
            (
                ("identifiers", "['C1-1', 'C1-2']", "#e2e8dc", "#527c67"),
                ("xy coords", "[[7, 6], [9, 3]]", "#d5e5dc", "#205841"),
                ("features", "[[0.3], [0.8]]", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Compressed NPZ archive arrays and row-0 alignment check",
            ("Array key", "Shape", "Dtype", "Row 0 value"),
            (
                ("identifiers", "(2,)", "str", "'C1-1'"),
                ("xy", "(2, 2)", "int", "[7, 6]"),
                ("features", "(2, 1)", "float32", "[0.3]"),
            ),
            note="Reading index 0 across all three arrays recovers Cell C1-1 at (7, 6) with feature 0.3.",
        )
        return inp, out

    if filename == "summarise_cells_by_core.py":
        inp = swatch_chart(
            "4 indexed cells spread unevenly across 3 expected cores",
            (
                ("Core A", "3 cells (75% share)", "#f7e7ba", "#8a5a19"),
                ("Core B", "1 cell (25% share)", "#d5e5dc", "#205841"),
                ("Core C", "0 cells (empty!)", "#f5d0c5", "#b3472a"),
            ),
        )
        out = bar_chart(
            "Cell count per core (revealing 75% concentration in Core A)",
            (
                ("Core A (dominates)", 3, "3 cells (75%)", "#8a5a19"),
                ("Core B", 1, "1 cell (25%)", "#205841"),
                ("Core C (empty)", 0.08, "0 cells ⚠", "#b3472a"),
            ),
            max_val=3,
            note="Total = 4 cells, median = 1 cell/core. A total count alone hides that Core A supplies 75% of the dataset.",
        )
        return inp, out

    # --- Goal: storage (Compress & audit storage) ---
    if filename == "compare_image_encodings.py":
        inp = '<p class="lab-card-note">The generated example encodes a 48 × 48 RGB patch as lossless PNG and as WebP at quality 75.</p>'
        generated = mini_table(
            "Generated example · one patch",
            ("Format", "File size", "Mean channel difference"),
            (("PNG", "129 B", "0.00 / 255"), ("WebP", "174 B", "1.95 / 255")),
        )
        historical = bar_chart(
            "Thesis result · storage for 229,683 patches",
            (("PNG collection", 26.94, "26.94 GB", "#8a5a19"), ("WebP collection", 3.63, "3.63 GB", "#205841")),
            max_val=26.94,
            note="Storage fell by 86.5%. The thesis describes a compression ratio of 0.85 (pp. 71–72, Fig. 2.12).",
        )
        out = generated + historical
        return inp, out

    if filename == "audit_dataset_structure.py":
        inp = swatch_chart(
            "Pre-flight audit comparing manifest against storage arrays",
            (
                ("Array A · ⚠ Shape", "(10, 32) vs (10, 64)", "#f7e7ba", "#8a5a19"),
                ("Array B · ✕ Missing", "Absent from disk", "#f5d0c5", "#b3472a"),
                ("spillover · ! Extra", "Unlisted (1, 64)", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Three dataset faults caught before launching training",
            ("Fault", "Key", "Observed vs expected", "Action"),
            (
                ("⚠ Wrong shape", "A", "(10, 32) vs (10, 64)", "Re-export A with all 64 feature columns."),
                ("✕ Missing file", "B", "Absent vs (8, 64)", "Run extraction for B before training."),
                ("! Unexpected file", "spillover", "Unlisted (1, 64)", "Remove or quarantine unindexed file."),
            ),
        )
        return inp, out

    if filename == "measure_storage_reads.py":
        inp = (
            '<svg viewBox="0 0 330 84" class="lab-diagram" role="img" aria-label="20 separate 4 KB files compared with one contiguous bundle file">'
            '<rect x="12" y="12" width="24" height="22" rx="2" fill="#e2e8dc" stroke="#527c67"/>'
            '<rect x="42" y="12" width="24" height="22" rx="2" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<rect x="72" y="12" width="24" height="22" rx="2" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<rect x="102" y="12" width="24" height="22" rx="2" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<text x="136" y="27" font-size="10.5" fill="#244035">20 files: open <code>2.bin</code>, <code>5.bin</code>, <code>9.bin</code></text>'
            '<rect x="12" y="48" width="114" height="22" rx="2" fill="#e2e8dc" stroke="#527c67"/>'
            '<rect x="30" y="48" width="18" height="22" fill="#c98ca7"/><rect x="60" y="48" width="18" height="22" fill="#c98ca7"/><rect x="96" y="48" width="18" height="22" fill="#c98ca7"/>'
            '<text x="136" y="63" font-size="10.5" fill="#244035">1 bundle: seek inside <code>bundle.bin</code></text>'
            "</svg>"
        )
        out = bar_chart(
            "Local read time for 3 chunks = 12,288 bytes (single run)",
            (("Separate files", 11.244, "11.24 ms (12,288 B)", "#8a5a19"), ("Single bundle", 10.052, "10.05 ms (12,288 B)", "#205841")),
            max_val=12.0,
            note="Both layouts return the exact same 12,288 bytes; timings vary across machines and OS caches.",
        )
        return inp, out

    # --- Goal: autoencoder (Autoencoder reconstruction) ---
    if filename == "fit_linear_autoencoder.py":
        inp = (
            '<svg viewBox="0 0 300 84" class="lab-diagram" role="img" aria-label="3-value patches compressed through a 2-number bottleneck and decoded">'
            '<rect x="14" y="14" width="76" height="56" rx="4" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.5"/>'
            '<text x="52" y="38" text-anchor="middle" font-size="10.5" fill="#1b3126" font-weight="bold">Input (3×3)</text>'
            '<text x="52" y="54" text-anchor="middle" font-size="9.5" fill="#244035">3 values/patch</text>'
            '<text x="102" y="45" font-size="13" fill="#205841" font-weight="bold">→</text>'
            '<rect x="118" y="22" width="64" height="40" rx="4" fill="#f7e7ba" stroke="#8a5a19" stroke-width="2"/>'
            '<text x="150" y="41" text-anchor="middle" font-size="10.5" fill="#1b3126" font-weight="bold">Code (3×2)</text>'
            '<text x="150" y="54" text-anchor="middle" font-size="9" fill="#4b5c51">2 numbers</text>'
            '<text x="192" y="45" font-size="13" fill="#205841" font-weight="bold">→</text>'
            '<rect x="208" y="14" width="78" height="56" rx="4" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="247" y="38" text-anchor="middle" font-size="10.5" fill="#1b3126" font-weight="bold">Decoded</text>'
            '<text x="247" y="54" text-anchor="middle" font-size="9.5" fill="#205841">3 values rebuilt</text>'
            "</svg>"
        )
        out = mini_table(
            "Original 3-value patches, compact 2-number codes and decoded values",
            ("Patch", "Original (3 values)", "2-number code", "Decoded (3 values)"),
            (
                ("Patch 1", "[0.1, 0.2, 0.3]", "[-0.436, -0.253]", "[0.10, 0.20, 0.30]"),
                ("Patch 2", "[0.6, 0.9, 0.8]", "[+0.550, -0.123]", "[0.60, 0.90, 0.80]"),
                ("Patch 3", "[0.8, 0.2, 0.4]", "[-0.114, +0.376]", "[0.80, 0.20, 0.40]"),
            ),
        )
        return inp, out

    if filename == "score_reconstructions.py":
        inp = swatch_chart(
            "Original vs reconstructed pairs (highlighting Sample b's 0.2 residual)",
            (
                ("Sample a", "[0.0, 1.0] → [0.1, 0.9]", "#d5e5dc", "#205841"),
                ("Sample b (worst)", "[0.2, 0.4] → [0.4, 0.4]", "#f5d0c5", "#b3472a"),
            ),
        )
        out = bar_chart(
            "Samples ranked worst-first by mean squared reconstruction error",
            (
                ("1. Sample b (inspect)", 0.020, "MSE 0.020", "#b3472a"),
                ("2. Sample a", 0.010, "MSE 0.010", "#205841"),
            ),
            max_val=0.022,
            note="Ranking by MSE brings Sample b (with the 0.20 miss on its first value) to the top of the review queue.",
        )
        return inp, out

    if filename == "compare_bottleneck_sizes.py":
        inp = swatch_chart(
            "Same held-out test set passed through 1-number vs 2-number bottlenecks",
            (
                ("Width = 1", "16 bytes (2 test rows)", "#f7e7ba", "#8a5a19"),
                ("Width = 2", "32 bytes (2 test rows)", "#d5e5dc", "#205841"),
            ),
        )
        out = bar_chart(
            "Held-out reconstruction error (MSE, lower retains more detail)",
            (
                ("1 number (16 B)", 0.00141, "0.00141 MSE", "#8a5a19"),
                ("2 numbers (32 B)", 0.00049, "0.00049 MSE (2.9× lower)", "#205841"),
            ),
            max_val=0.0015,
        )
        return inp, out

    if filename == "score_variational_reconstruction.py":
        inp = swatch_chart(
            "Two-part VAE objective: image fidelity + code distribution penalty",
            (
                ("Image error (BCE)", "0.387", "#e6c5d4", "#8a4b68"),
                ("Raw KL penalty", "0.083", "#f7e7ba", "#8a5a19"),
                ("Weight β = 0.5", "0.5 × 0.083 = 0.042", "#d5e5dc", "#205841"),
            ),
        )
        out = bar_chart(
            "Receipt: 0.387 (image) + 0.5 × 0.083 (code KL) = 0.429 total",
            (
                ("Reconstruction", 0.387, "0.387", "#8a4b68"),
                ("Weighted KL (β=0.5)", 0.042, "0.042 (raw 0.083)", "#8a5a19"),
                ("Total VAE loss", 0.429, "0.429", "#205841"),
            ),
            max_val=0.45,
        )
        return inp, out

    # --- Goal: features (Contrastive view learning) ---
    if filename == "learn_image_features.py":
        inp = swatch_chart(
            "Orthogonal vs duplicated feature columns across 4 samples",
            (
                ("Independent cols", "Col 1 ⊥ Col 2 (r = 0)", "#d5e5dc", "#205841"),
                ("Duplicated col", "Col 1 = Col 2 (r = 1)", "#f5d0c5", "#b3472a"),
            ),
        )
        out = bar_chart(
            "Barlow Twins total loss (agreement + 0.005 × off-diagonal redundancy)",
            (
                ("Independent (r=0)", 0.0005, "0.000 total loss", "#205841"),
                ("Duplicated (r=1)", 0.010, "0.010 (redundancy penalty)", "#b3472a"),
            ),
            max_val=0.011,
            note="Both arrangements achieve 0.000 agreement loss across views, but duplicating a column triggers the off-diagonal redundancy penalty (+0.010).",
        )
        return inp, out

    if filename == "prepare_paired_views.py":
        inp = swatch_chart(
            "Source 2 × 2 patch p1 and two stochastic augmentations (seed = 9)",
            (
                ("p1 (original)", "[[0.10, 0.50], [0.70, 1.00]]", "#e6c5d4", "#8a4b68"),
                ("View 1 (×0.94)", "[[0.09, 0.47], [0.66, 0.94]]", "#d5e5dc", "#205841"),
                ("View 2 (flip, ×1.04)", "[[0.52, 0.10], [1.00, 0.72]]", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Paired views keep shared patch ID p1 for contrastive training",
            ("View", "Shared ID", "Row 1", "Row 2", "Applied transform"),
            (
                ("View 1", "p1", "[0.09, 0.47]", "[0.66, 0.94]", "Unflipped · brightness ×0.94"),
                ("View 2", "p1", "[0.52, 0.10]", "[1.00, 0.72]", "Horizontal flip · brightness ×1.04"),
            ),
        )
        return inp, out

    if filename == "audit_feature_variation.py":
        inp = swatch_chart(
            "3-column feature matrix with 1 constant column and 1 correlated pair",
            (
                ("Col 0 · Varies", "[1, 2, 3]", "#d5e5dc", "#205841"),
                ("Col 1 · Constant", "[0, 0, 0] (std = 0)", "#f5d0c5", "#b3472a"),
                ("Col 2 · Duplicate", "[5, 10, 15] (5 × Col 0)", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Feature health checks before downstream training",
            ("Flagged issue", "Column(s)", "Measured value", "Meaning"),
            (
                ("Collapsed feature", "Column 1", "Std dev = 0.0", "Zero variation across patches; carries no signal."),
                ("Redundant pair", "Columns (0, 2)", "|r| = 1.00 (≥ 0.99)", "Column 2 is a linear multiple of Column 0."),
            ),
        )
        return inp, out

    if filename == "fit_shared_view_encoder.py":
        inp = (
            '<svg viewBox="0 0 300 84" class="lab-diagram" role="img" aria-label="Two views entering shared weight matrix W">'
            '<rect x="12" y="12" width="74" height="26" rx="4" fill="#d5e5dc" stroke="#205841"/>'
            '<text x="20" y="29" font-size="10.5" fill="#1b3126">View 1 (4×2)</text>'
            '<rect x="12" y="46" width="74" height="26" rx="4" fill="#f7e7ba" stroke="#8a5a19"/>'
            '<text x="20" y="63" font-size="10.5" fill="#1b3126">View 2 (4×2)</text>'
            '<line x1="86" y1="25" x2="122" y2="38" stroke="#205841" stroke-width="1.5"/>'
            '<line x1="86" y1="59" x2="122" y2="46" stroke="#205841" stroke-width="1.5"/>'
            '<rect x="122" y="24" width="88" height="36" rx="4" fill="#e6c5d4" stroke="#8a4b68" stroke-width="2"/>'
            '<text x="130" y="46" font-size="10.5" fill="#1b3126" font-weight="bold">Shared W (2×2)</text>'
            '<line x1="210" y1="42" x2="232" y2="42" stroke="#205841" stroke-width="1.5"/>'
            '<text x="236" y="46" font-size="10.5" fill="#205841" font-weight="bold">40 steps</text>'
            "</svg>"
        )
        out = (
            '<svg viewBox="0 0 300 90" class="lab-diagram" role="img" aria-label="Barlow Twins objective curve dropping from 0.1938 to 0.0003 over 40 steps">'
            '<rect width="300" height="90" rx="6" fill="#f7f4ea"/>'
            '<text x="14" y="18" font-size="11" fill="#244035" font-weight="bold">Barlow Twins objective over 40 update steps</text>'
            '<line x1="36" y1="26" x2="36" y2="72" stroke="#9ab0a2"/><line x1="36" y1="72" x2="276" y2="72" stroke="#9ab0a2"/>'
            '<path d="M36,30 Q90,66 156,70 T272,71" fill="none" stroke="#205841" stroke-width="2.5"/>'
            '<circle cx="36" cy="30" r="4" fill="#b3472a"/><text x="44" y="34" font-size="10" fill="#b3472a" font-weight="bold">Step 0: 0.1938</text>'
            '<circle cx="272" cy="71" r="4" fill="#205841"/><text x="184" y="64" font-size="10" fill="#205841" font-weight="bold">Step 40: 0.0003</text>'
            "</svg>"
        )
        return inp, out

    # --- Goal: frozen-features (Pretrained encoders) ---
    if filename == "batch_frozen_features.py":
        inp = swatch_chart(
            "Three identified patches processed in batches of 2 (weights frozen)",
            (
                ("Batch 1 · p1", "[[0.1, 0.4]]", "#d5e5dc", "#205841"),
                ("Batch 1 · p2", "[[0.7, 0.9]]", "#d5e5dc", "#205841"),
                ("Batch 2 · p3", "[[0.4, 0.2]]", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Output vectors preserve exact input ID order across batches",
            ("Patch ID", "Feature 1 (mean)", "Feature 2 (std)", "Batch"),
            (("p1", "0.250", "0.150", "Batch 1"), ("p2", "0.800", "0.100", "Batch 1"), ("p3", "0.300", "0.100", "Batch 2")),
        )
        return inp, out

    if filename == "compare_encoder_dimensions.py":
        inp = swatch_chart(
            "30 patches encoded at two vector widths (float32 = 4 B/value)",
            (
                ("small encoder", "30 × 16 float32", "#d5e5dc", "#205841"),
                ("wide encoder", "30 × 64 float32", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = bar_chart(
            "In-memory array size for 30 patches (bytes)",
            (("small (16-D)", 1920, "1,920 B", "#205841"), ("wide (64-D)", 7680, "7,680 B (4×)", "#8a5a19")),
            max_val=8000,
            note="Calculated array footprint (examples × dimensions × 4 bytes), distinct from compressed disk file size.",
        )
        return inp, out

    if filename == "standardise_encoder_inputs.py":
        inp = (
            '<svg viewBox="0 0 310 84" class="lab-diagram" role="img" aria-label="16 by 20 RGB patch resized to 8 by 8 and normalised">'
            '<rect x="16" y="12" width="44" height="56" rx="3" fill="#95bbaf" stroke="#244035"/>'
            '<text x="12" y="79" font-size="9.5" fill="#244035">16 × 20 RGB (#95bbaf)</text>'
            '<text x="76" y="44" font-size="11" fill="#205841" font-weight="bold">→ resize 8×8 &amp; norm →</text>'
            '<rect x="212" y="20" width="38" height="38" rx="3" fill="#95bbaf" stroke="#205841" stroke-width="2"/>'
            '<text x="180" y="74" font-size="9.5" fill="#244035">Tensor (3, 8, 8) float32</text>'
            "</svg>"
        )
        out = bar_chart(
            "Normalised channel values (mean = 0.5, std = 0.25)",
            (
                ("R (149 → 0.584)", 0.337, "+0.337", "#b3472a"),
                ("G (187 → 0.733)", 0.933, "+0.933", "#205841"),
                ("B (175 → 0.686)", 0.745, "+0.745", "#3b6e8c"),
            ),
            max_val=1.0,
        )
        return inp, out

    # --- Goal: feature-benchmarks (Benchmark feature quality) ---
    if filename == "benchmark_frozen_features.py":
        inp = swatch_chart(
            "Shared train centroids [0, 1] and held-out test split [2, 3]",
            (
                ("Train [0, 1]", "Labels ['a', 'b'] at 0.0, 4.0", "#e2e8dc", "#527c67"),
                ("Test · first", "[0.3, 3.7] → ['a', 'b']", "#d5e5dc", "#205841"),
                ("Test · second", "[3.5, 3.7] → ['b', 'b']", "#f5d0c5", "#b3472a"),
            ),
        )
        out = bar_chart(
            "Held-out nearest-centroid accuracy on shared test cases [2, 3]",
            (("first encoder", 1.0, "2/2 (100%)", "#205841"), ("second encoder", 0.5, "1/2 (50%)", "#b3472a")),
            max_val=1.0,
        )
        return inp, out

    if filename == "measure_feature_separation.py":
        inp = (
            '<svg viewBox="0 0 340 74" class="lab-diagram" role="img" aria-label="Four 1D points in two groups showing within-group distance 0.5 vs nearest other-group distance 3.25">'
            '<rect width="340" height="74" rx="6" fill="#f7f4ea"/>'
            '<line x1="24" y1="38" x2="286" y2="38" stroke="#9ab0a2" stroke-width="2"/>'
            '<circle cx="40" cy="38" r="6" fill="#205841"/><text x="24" y="24" font-size="10" fill="#205841" font-weight="bold">s0 (0.0)</text>'
            '<circle cx="80" cy="38" r="6" fill="#205841"/><text x="68" y="24" font-size="10" fill="#205841" font-weight="bold">s1 (0.5)</text>'
            '<circle cx="220" cy="38" r="6" fill="#8a5a19"/><text x="200" y="24" font-size="10" fill="#8a5a19" font-weight="bold">s2 (3.5)</text>'
            '<circle cx="266" cy="38" r="6" fill="#8a5a19"/><text x="252" y="24" font-size="10" fill="#8a5a19" font-weight="bold">s3 (4.0)</text>'
            '<text x="24" y="60" font-size="10" fill="#205841">Group g1 (within = 0.5)</text>'
            '<text x="176" y="60" font-size="10" fill="#8a5a19">Group g2 (across = 3.25–3.75)</text>'
            "</svg>"
        )
        out = bar_chart(
            "Per-sample silhouette score (1 representation split into g1 and g2)",
            (
                ("s0 (g1, x=0.0)", 0.87, "0.87", "#205841"),
                ("s1 (g1, x=0.5)", 0.85, "0.85", "#205841"),
                ("s2 (g2, x=3.5)", 0.85, "0.85", "#8a5a19"),
                ("s3 (g2, x=4.0)", 0.87, "0.87", "#8a5a19"),
            ),
            max_val=1.0,
        )
        return inp, out

    if filename == "project_feature_space.py":
        inp = swatch_chart(
            "Three 3D feature vectors projected onto 2 principal axes",
            (
                ("Sample 1", "[0.10, 0.30, 0.20]", "#d5e5dc", "#205841"),
                ("Sample 2", "[0.20, 0.45, 0.17]", "#d5e5dc", "#205841"),
                ("Sample 3", "[0.75, 0.60, 0.90]", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = (
            '<svg viewBox="0 0 310 112" class="lab-diagram" role="img" aria-label="2D PCA scatter plot of three samples with variance explained on each axis">'
            '<rect x="36" y="10" width="244" height="78" rx="4" fill="#f7f4ea" stroke="#9ab0a2"/>'
            '<line x1="36" y1="49" x2="280" y2="49" stroke="#d0d8cd" stroke-dasharray="3 3"/>'
            '<circle cx="74" cy="34" r="5.5" fill="#205841"/><text x="83" y="37" font-size="10" fill="#205841" font-weight="bold">S1 (-0.359, +0.080)</text>'
            '<circle cx="88" cy="66" r="5.5" fill="#205841"/><text x="97" y="69" font-size="10" fill="#205841" font-weight="bold">S2 (-0.282, -0.086)</text>'
            '<circle cx="242" cy="48" r="5.5" fill="#8a5a19"/><text x="148" y="44" font-size="10" fill="#8a5a19" font-weight="bold">S3 (+0.640, +0.007)</text>'
            '<text x="54" y="104" font-size="10" fill="#244035" font-weight="bold">PC1: 97.8% variance · PC2: 2.2% variance</text>'
            "</svg>"
        )
        return inp, out

    if filename == "check_bag_classifier_on_known_signal.py":
        inp = (
            '<svg viewBox="0 0 320 84" class="lab-diagram" role="img" aria-label="Positive bag with 1 planted +5 signal among 12 patches vs negative bag of background noise">'
            '<rect width="320" height="84" rx="6" fill="#f7f4ea"/>'
            '<text x="12" y="20" font-size="10.5" fill="#244035" font-weight="bold">Positive bag (1 of 12 patches carries +5 signal):</text>'
            + "".join(
                f'<rect x="{12 + i * 22}" y="26" width="18" height="16" rx="2" fill="{"#b3472a" if i == 4 else "#d0d8cd"}"/>'
                for i in range(12)
            )
            + '<text x="12" y="58" font-size="10.5" fill="#244035" font-weight="bold">Negative bag (all 12 patches N(0, 1) noise):</text>'
            + "".join(
                f'<rect x="{12 + i * 22}" y="64" width="18" height="14" rx="2" fill="#d0d8cd"/>'
                for i in range(12)
            )
            + "</svg>"
        )
        out = bar_chart(
            "Bag-level ROC AUC across 64 bags (32 positive, 32 negative)",
            (
                ("Mean pooling", 0.830, "0.830 AUC (diluted)", "#8a5a19"),
                ("Max pooling", 0.999, "0.999 AUC ★", "#205841"),
            ),
            max_val=1.0,
            note="Averaging all 12 patches dilutes a single positive instance with 11 background patches; max pooling isolates the strongest instance.",
        )
        return inp, out

    # --- Goal: feature-export (Keep vector coordinates) ---
    if filename == "export_feature_vectors.py":
        inp = (
            '<svg viewBox="0 0 295 76" class="lab-diagram" role="img" aria-label="Two adjacent 4x4 patches on an 8x4 grid with their IDs and bounds">'
            '<rect x="14" y="12" width="52" height="52" fill="#d5e5dc" stroke="#205841" stroke-width="2"/>'
            '<text x="18" y="34" font-size="9.5" fill="#1b3126" font-weight="bold">patch-x0-y0</text>'
            '<text x="18" y="48" font-size="9" fill="#536052">(0, 0, 4, 4)</text>'
            '<rect x="66" y="12" width="52" height="52" fill="#f7e7ba" stroke="#8a5a19" stroke-width="2"/>'
            '<text x="70" y="34" font-size="9.5" fill="#1b3126" font-weight="bold">patch-x4-y0</text>'
            '<text x="70" y="48" font-size="9" fill="#536052">(4, 0, 8, 4)</text>'
            '<text x="130" y="34" font-size="10.5" fill="#244035" font-weight="bold">+ 2 features per row</text>'
            '<text x="130" y="50" font-size="9.5" fill="#536052">Coordinates travel with vector</text>'
            "</svg>"
        )
        out = mini_table(
            "Exported CSV rows keeping bounds and features together",
            ("region_id", "Bounds (l, t, r, b)", "feature_1", "feature_2"),
            (("patch-x0-y0", "(0, 0, 4, 4)", "0.12", "0.68"), ("patch-x4-y0", "(4, 0, 8, 4)", "0.43", "0.19")),
        )
        return inp, out

    if filename == "align_features_to_regions.py":
        inp = (
            '<svg viewBox="0 0 305 78" class="lab-diagram" role="img" aria-label="Region table ordered A, B joined by ID to feature table ordered B, A">'
            '<rect x="12" y="12" width="102" height="24" rx="3" fill="#d5e5dc" stroke="#205841"/><text x="18" y="28" font-size="10" fill="#1b3126">Regions: A (12, 6)</text>'
            '<rect x="12" y="42" width="102" height="24" rx="3" fill="#f7e7ba" stroke="#8a5a19"/><text x="18" y="58" font-size="10" fill="#1b3126">Regions: B (80, 5)</text>'
            '<rect x="176" y="12" width="116" height="24" rx="3" fill="#f7e7ba" stroke="#8a5a19"/><text x="182" y="28" font-size="10" fill="#1b3126">Vectors: B (0.1, 0.2)</text>'
            '<rect x="176" y="42" width="116" height="24" rx="3" fill="#d5e5dc" stroke="#205841"/><text x="182" y="58" font-size="10" fill="#1b3126">Vectors: A (0.3, 0.4)</text>'
            '<line x1="114" y1="24" x2="176" y2="54" stroke="#205841" stroke-width="2"/>'
            '<line x1="114" y1="54" x2="176" y2="24" stroke="#8a5a19" stroke-width="2"/>'
            "</svg>"
        )
        out = mini_table(
            "Records aligned by ID regardless of input file order",
            ("Region ID", "Coordinates (x, y)", "Feature vector", "Join check"),
            (("A", "(12, 6)", "(0.3, 0.4)", "✓ Matched across reordered rows"), ("B", "(80, 5)", "(0.1, 0.2)", "✓ Matched by ID")),
        )
        return inp, out

    if filename == "check_feature_cache.py":
        inp = swatch_chart(
            "Cached feature array checked against experiment requirements",
            (
                ("ID order · ✕", "['B', 'A'] vs ['A', 'B']", "#f5d0c5", "#b3472a"),
                ("Encoder · ✕", "v1 vs expected v2", "#f5d0c5", "#b3472a"),
                ("Shape · ✓", "(2, 8) matches width 8", "#d5e5dc", "#205841"),
            ),
        )
        out = mini_table(
            "Cache verification report before training",
            ("Check", "Status", "Action required"),
            (
                ("region IDs or ordering", "Flagged", "Re-index cache to ['A', 'B'] order."),
                ("encoder name", "Flagged", "Re-extract features with encoder-v2."),
                ("vector shape (2, 8)", "Passed", "Dimensions match expected 2 × 8 matrix."),
            ),
        )
        return inp, out

    # --- Goal: grading-splits (Reference grades & splits) ---
    if filename == "prepare_reference_grades.py":
        inp = swatch_chart(
            "Assessor stain ratings (0–3 scale) supplied for Samples a and b",
            (
                ("Sample a", "r1 = 1, r2 = 2 (n=2)", "#d5e5dc", "#205841"),
                ("Sample b", "r2 = 3 only (n=1)", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Reference grade paired with assessor count (n) and spread",
            ("Sample", "Mean grade", "Assessors (n)", "Spread", "Why count (n) matters alongside spread"),
            (
                ("a", "1.5", "n = 2", "1.0", "Two assessors differed by 1 grade point (1 vs 2)."),
                ("b", "3.0", "n = 1", "0.0", "Spread = 0 from n = 1 means uncorroborated, not two agreeing raters."),
            ),
            highlight_row=1,
        )
        return inp, out

    if filename == "assign_validation_folds.py":
        inp = (
            '<svg viewBox="0 0 300 84" class="lab-diagram" role="img" aria-label="Samples a and b in group g1 kept together in Fold 0 while c and d go to Fold 1">'
            '<rect x="12" y="12" width="110" height="26" rx="4" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="18" y="29" font-size="10.5" fill="#1b3126" font-weight="bold">Group g1: a, b</text>'
            '<rect x="12" y="46" width="110" height="26" rx="4" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="18" y="63" font-size="10.5" fill="#1b3126" font-weight="bold">Groups g2, g3: c, d</text>'
            '<text x="136" y="29" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<text x="136" y="63" font-size="12" fill="#8a5a19" font-weight="bold">→</text>'
            '<rect x="158" y="12" width="128" height="26" rx="4" fill="#d5e5dc" stroke="#205841" stroke-width="2"/>'
            '<text x="166" y="29" font-size="10.5" fill="#1b3126" font-weight="bold">Fold 0: a, b (paired)</text>'
            '<rect x="158" y="46" width="128" height="26" rx="4" fill="#f7e7ba" stroke="#8a5a19" stroke-width="2"/>'
            '<text x="166" y="63" font-size="10.5" fill="#1b3126" font-weight="bold">Fold 1: c, d</text>'
            "</svg>"
        )
        out = mini_table(
            "Group-aware fold split (preventing group g1 from leaking across train/test)",
            ("Sample", "Group", "Held-out fold", "Kept together with"),
            (("a, b", "g1", "Fold 0", "Both in Fold 0 (never split across train and test)"), ("c, d", "g2, g3", "Fold 1", "Balanced 2 samples per fold")),
        )
        return inp, out

    # --- Goal: grading-models (Compare scale graders) ---
    if filename == "train_scale_graders.py":
        inp = swatch_chart(
            "Shared split (Train: a=1, b=2 · Test: c=3) at Patch vs Cell scale",
            (
                ("Patch features", "a:0.1, b:0.5 → test c:0.9", "#d5e5dc", "#205841"),
                ("Cell features", "a:0.3, b:0.6 → test c:0.7", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = bar_chart(
            "Held-out prediction error on Sample c (reference grade = 3.000)",
            (
                ("Patch grader (pred 2.17)", 0.833, "0.833 error", "#205841"),
                ("Cell grader (pred 1.76)", 1.241, "1.241 error", "#8a5a19"),
            ),
            max_val=1.5,
            note="Two-scale demo of the three-scale thesis comparison (where patch features achieved the lowest error).",
        )
        return inp, out

    if filename == "save_held_out_grades.py":
        inp = swatch_chart(
            "2-fold cross-validation rotates which samples are held out",
            (
                ("Fold 0 eval", "Train {b, c} → Predict {a, d}", "#d5e5dc", "#205841"),
                ("Fold 1 eval", "Train {a, d} → Predict {b, c}", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Out-of-fold predictions CSV (every sample predicted by a model that did not train on it)",
            ("sample", "scale", "fold", "reference", "prediction", "|error|"),
            (
                ("a", "patch", "0", "0.0", "1.039", "1.039"),
                ("d", "patch", "0", "3.0", "1.907", "1.093"),
                ("b", "patch", "1", "1.0", "1.071", "0.071"),
                ("c", "patch", "1", "2.0", "2.071", "0.071"),
            ),
        )
        return inp, out

    if filename == "summarise_errors_by_grade.py":
        inp = swatch_chart(
            "5 held-out predictions grouped by ordinal reference grade",
            (
                ("Grade 0 (n=2)", "Preds: 0.7, 0.2", "#d5e5dc", "#205841"),
                ("Grade 1 (n=1)", "Pred: 1.2", "#e2e8dc", "#527c67"),
                ("Grade 3 (n=2)", "Preds: 2.1, 2.8", "#f5d0c5", "#b3472a"),
            ),
        )
        out = (
            diverging_chart(
                "Signed error by reference grade (prediction − reference)",
                (
                    ("Grade 0 (n=2)", 0.45, "+0.45 (high)"),
                    ("Grade 1 (n=1)", 0.20, "+0.20 (high)"),
                    ("Grade 3 (n=2)", -0.55, "−0.55 (low)"),
                ),
                scale=0.6,
                note="Grade 0 runs +0.45 high on average, while Grade 3 under-predicts by −0.55 across its 2 cases.",
            )
        )
        return inp, out

    # --- Goal: compare (Matched ablation runs) ---
    if filename == "compare_experiments.py":
        inp = mini_table(
            "Baseline and compact variant paired on Folds 0 & 1 (seed = 7)",
            ("Config", "Fold 0 (err, time, RAM)", "Fold 1 (err, time, RAM)"),
            (
                ("baseline", "0.31 · 52 s · 92 MiB", "0.33 · 55 s · 91 MiB"),
                ("compact", "0.32 · 29 s · 60 MiB", "0.34 · 31 s · 59 MiB"),
            ),
        )
        out = diverging_chart(
            "Paired % change (compact vs baseline across 2 folds, seed 7)",
            (
                ("Error (+worse)", 3.1, "+3.1%"),
                ("Time / epoch", -43.9, "−43.9% faster"),
                ("Peak memory", -35.0, "−35.0% smaller"),
            ),
            scale=50.0,
            note="Compact cuts runtime (−43.9%) and memory (−35.0%) while raising error by +3.1%.",
        )
        return inp, out

    if filename == "plan_matched_runs.py":
        inp = swatch_chart(
            "Baseline + 2 single-parameter changes × 2 folds × 2 seeds = 12 runs",
            (
                ("baseline", "pool=mean, bs=16", "#e2e8dc", "#527c67"),
                ("max_pool", "pool=max, bs=16", "#d5e5dc", "#205841"),
                ("large_batch", "pool=mean, bs=32", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "12-run schedule grid (each cell pairs Fold and Seed across variants)",
            ("Configuration", "Fold 0 · Seed 7", "Fold 0 · Seed 11", "Fold 1 · Seed 7", "Fold 1 · Seed 11"),
            (
                ("baseline", "mean, bs=16", "mean, bs=16", "mean, bs=16", "mean, bs=16"),
                ("max_pool (1 change)", "max, bs=16", "max, bs=16", "max, bs=16", "max, bs=16"),
                ("large_batch (1 change)", "mean, bs=32", "mean, bs=32", "mean, bs=32", "mean, bs=32"),
            ),
        )
        return inp, out

    if filename == "verify_run_configuration.py":
        inp = swatch_chart(
            "Planned run settings vs recorded startup log (seed = 7)",
            (
                ("seed = 7 · ✓", "Recorded 7", "#d5e5dc", "#205841"),
                ("depth = 2 · ⚠", "Recorded 1 (wrong!)", "#f7e7ba", "#8a5a19"),
                ("positions · ✕", "Missing from log", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Two configuration faults caught before including the run",
            ("Setting", "Planned", "Effective", "Recorded?", "Impact on comparison"),
            (
                ("depth", "2", "1", "True", "Ran a 1-layer model instead of planned 2-layer model."),
                ("position_encoding", "True", "None", "False", "Unconfirmed whether positional encoding was active."),
            ),
        )
        return inp, out

    if filename == "summarise_matched_training_traces.py":
        inp = swatch_chart(
            "Validation window fixed to final Epochs 2–3 across 2 paired runs",
            (
                ("Epoch 1", "Warmup (excluded)", "#e2e8dc", "#7b8c80"),
                ("Epoch 2", "Included in window", "#d5e5dc", "#205841"),
                ("Epoch 3", "Included in window", "#d5e5dc", "#205841"),
            ),
        )
        out = (
            bar_chart(
                "Final-window mean balanced accuracy & elapsed time (Epochs 2–3)",
                (
                    ("baseline (0.760 acc)", 66.0, "66.0 s · 0.760 acc", "#8a5a19"),
                    ("variant (0.770 acc)", 51.0, "51.0 s · 0.770 acc", "#205841"),
                ),
                max_val=70.0,
            )
        )
        return inp, out

    # --- Goal: sampling (Sample rare & hard cases) ---
    if filename == "weight_grading_examples.py":
        inp = mini_table(
            "Four samples combining class frequency and training loss",
            ("Sample", "Grade class", "Epoch 1 loss", "Epoch 2 loss"),
            (
                ("s1, s3", "Grade 0 (common, n=3)", "0.10 (low)", "0.20"),
                ("s2", "Grade 0 (common, n=3)", "0.90 (high loss!)", "0.60"),
                ("s4", "Grade 1 (rare, n=1)", "0.40", "0.30"),
            ),
        )
        out = bar_chart(
            "Updated sampling probabilities (boosting rare s4 & high-loss s2)",
            (
                ("s1 (common, low loss)", 0.157, "0.136 → 0.157", "#7b8c80"),
                ("s2 (high loss boosted)", 0.293, "0.322 → 0.293", "#8a5a19"),
                ("s3 (common, low loss)", 0.157, "0.136 → 0.157", "#7b8c80"),
                ("s4 (rare grade boosted)", 0.392, "0.406 → 0.392", "#205841"),
            ),
            max_val=0.45,
        )
        return inp, out

    if filename == "probe_grading_model_with_noise.py":
        inp = swatch_chart(
            "12 signal bags vs 12 Gaussian noise bags fed to null-aware scorer",
            (
                ("Signal bags (n=12)", "N(mean=1.5, std=0.4)", "#d5e5dc", "#205841"),
                ("Noise probe (n=12)", "N(mean=0.0, std=1.0)", "#f5d0c5", "#b3472a"),
            ),
        )
        out = bar_chart(
            "Median probability assigned to the outside-input (null) class",
            (
                ("Signal (0/12 null)", 0.009, "0.009 (0/12 calls)", "#205841"),
                ("Noise (12/12 null)", 0.683, "0.683 (12/12 calls)", "#b3472a"),
            ),
            max_val=0.75,
            note="Synthetic probe illustrating Appendix A.4's dedicated outside-input class.",
        )
        return inp, out

    # --- Goal: agreement (Model vs expert gap) ---
    if filename == "compare_assessor_errors.py":
        inp = mini_table(
            "Two matched samples scored by Assessor A, Assessor B and the model",
            ("Sample", "Assessor A", "Assessor B", "Consensus mean", "Model prediction"),
            (("a", "1.0", "2.0", "1.50", "1.40"), ("b", "2.0", "2.0", "2.00", "1.80")),
        )
        out = bar_chart(
            "Person-to-person disagreement vs model-to-consensus error (grade pts)",
            (
                ("Demo: Rater gap |A−B|", 0.50, "0.50 grade pts", "#8a5a19"),
                ("Demo: Model vs Mean", 0.15, "0.15 grade pts", "#205841"),
                ("Thesis: Rater gap", 0.382, "0.382 grade pts", "#8a5a19"),
                ("Thesis: Patch model", 0.238, "0.238 grade pts", "#205841"),
            ),
            max_val=0.55,
            note="The two numbers have distinct targets: rater gap compares two people, while model MAE compares predictions against their average.",
        )
        return inp, out

    if filename == "score_ordinal_agreement.py":
        inp = swatch_chart(
            "Four paired ratings on the 0–3 ordinal staining scale",
            (
                ("3 exact matches", "(0,0), (2,2), (3,3) · Δ²=0", "#d5e5dc", "#205841"),
                ("1 one-grade miss", "(1,2) · Δ²=1", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = bar_chart(
            "Chance-adjusted ordinal agreement (quadratic-weighted κ)",
            (
                ("Observed exact rate", 0.75, "3 / 4 pairs", "#527c67"),
                ("Quadratic weighted κ", 0.90, "κ = 0.90", "#205841"),
            ),
            max_val=1.0,
            note="Quadratic weighting penalises multi-grade disagreements by (a − b)² and adjusts for chance.",
        )
        return inp, out

    # --- Goal: subtype-cohort (Curate subtype cohort) ---
    if filename == "join_subtype_labels.py":
        inp = swatch_chart(
            "Three image IDs matched against supplied reference subtype table",
            (
                ("a → R1", "'ABC' (valid)", "#d5e5dc", "#205841"),
                ("b → R2", "'unclassified'", "#f7e7ba", "#8a5a19"),
                ("c → R3", "None (missing)", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Join outcome (separating unrecognised strings from missing records)",
            ("Image ID", "Reference ID", "Status", "Action"),
            (
                ("a", "R1", "✓ Accepted ('ABC')", "Advances to cohort eligibility filter"),
                ("b", "R2", "⚠ Unrecognised ('unclassified')", "Held for review (not in {'ABC', 'GCB'})"),
                ("c", "R3", "✕ Missing (no record)", "Held for review (never inferred)"),
            ),
            highlight_row=0,
        )
        return inp, out

    if filename == "audit_cohort_filters.py":
        inp = swatch_chart(
            "Three inclusion gates: valid label, required stain-a, and ≥ 8 patches",
            (
                ("Specimen a · ✓ Keep", "ABC · stain-a · 12 patches", "#d5e5dc", "#205841"),
                ("Specimen b · ✕ Drop", "Fails all 3 rules (4 patches)", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Specimen-by-criterion eligibility matrix (1 of 2 retained)",
            ("Specimen", "Target in {ABC, GCB}", "Has stain-a", "Patches ≥ 8", "Decision"),
            (
                ("Specimen a", "✓ ABC", "✓ Yes", "✓ 12 patches", "Retained (1 remaining)"),
                ("Specimen b", "✕ None", "✕ Missing", "✕ 4 patches", "Excluded (all 3 reasons logged)"),
            ),
            highlight_row=0,
        )
        return inp, out

    # --- Goal: interpret (Pool patches per case) ---
    if filename == "pool_patch_evidence.py":
        inp = bar_chart(
            "Softmax attention weights across the 3 patches in the bag",
            (
                ("Patch 1 [0.1, 0.9]", 0.212, "w = 0.212 (logit 0)", "#527c67"),
                ("Patch 2 [0.3, 0.7]", 0.212, "w = 0.212 (logit 0)", "#527c67"),
                ("Patch 3 [0.9, 0.2]", 0.576, "w = 0.576 (logit 1)", "#205841"),
            ),
            max_val=0.65,
        )
        out = mini_table(
            "Pooled bag vector under Mean, Max and Attention pooling",
            ("Pooling rule", "Feature 1", "Feature 2", "How Feature 1 was combined"),
            (
                ("mean", "0.433", "0.600", "(0.1 + 0.3 + 0.9) / 3"),
                ("maximum", "0.900", "0.900", "max(0.1, 0.3, 0.9) from Patch 3"),
                ("attention", "0.603", "0.454", "0.212×0.1 + 0.212×0.3 + 0.576×0.9"),
            ),
            highlight_row=2,
        )
        return inp, out

    if filename == "batch_variable_patch_sets.py":
        inp = (
            '<svg viewBox="0 0 300 94" class="lab-diagram" role="img" aria-label="Four specimens sorted by patch count into two batches with padded slots marked">'
            '<rect width="300" height="94" rx="6" fill="#f7f4ea"/>'
            '<text x="12" y="18" font-size="10.5" fill="#244035" font-weight="bold">Batch 1 (width 5): b (3) + 2 pad, c (5)</text>'
            '<rect x="12" y="24" width="54" height="12" rx="2" fill="#205841"/>'
            '<rect x="68" y="24" width="36" height="12" rx="2" fill="#f5d0c5" stroke="#b3472a" stroke-dasharray="2 2"/>'
            '<rect x="12" y="40" width="92" height="12" rx="2" fill="#205841"/>'
            '<text x="12" y="68" font-size="10.5" fill="#244035" font-weight="bold">Batch 2 (width 15): a (12) + 3 pad, d (15)</text>'
            '<rect x="12" y="74" width="160" height="12" rx="2" fill="#205841"/>'
            '<rect x="174" y="74" width="40" height="12" rx="2" fill="#f5d0c5" stroke="#b3472a" stroke-dasharray="2 2"/>'
            "</svg>"
        )
        out = bar_chart(
            "Dummy padding slots required across the 4 specimens (batch_size = 2)",
            (
                ("Unsorted (3 with 15; 5 with 12)", 19, "19 pad slots", "#b3472a"),
                ("Sorted ([b,c], [a,d])", 5, "5 pad slots (−74%)", "#205841"),
            ),
            max_val=19,
            note="This script groups the sets and counts padding. A downstream validity mask can exclude those slots from pooling.",
        )
        return inp, out

    if filename == "predict_subtypes_from_bags.py":
        inp = (
            '<svg viewBox="0 0 305 74" class="lab-diagram" role="img" aria-label="1D feature line showing ABC centroid at 0.15, held-out bag c at 0.70, and GCB centroid at 0.85">'
            '<rect width="305" height="74" rx="6" fill="#f7f4ea"/>'
            '<line x1="28" y1="40" x2="262" y2="40" stroke="#9ab0a2" stroke-width="2"/>'
            '<circle cx="52" cy="40" r="6" fill="#205841"/><text x="24" y="24" font-size="10" fill="#205841" font-weight="bold">Bag a · ABC (0.15)</text>'
            '<circle cx="196" cy="40" r="6" fill="#b3472a"/><text x="142" y="62" font-size="10" fill="#b3472a" font-weight="bold">Test bag c (mean 0.70)</text>'
            '<circle cx="238" cy="40" r="6" fill="#8a5a19"/><text x="178" y="24" font-size="10" fill="#8a5a19" font-weight="bold">Bag b · GCB (0.85)</text>'
            "</svg>"
        )
        out = mini_table(
            "Held-out bag c classification (score = dist_GCB − dist_ABC)",
            ("Held-out bag", "Dist to ABC (0.15)", "Dist to GCB (0.85)", "Signed score", "Call"),
            (("Bag c (mean 0.70)", "0.55", "0.15", "−0.400", "Closer to GCB (score < 0)"),),
        )
        return inp, out

    # --- Goal: subtype-ablations (Test position & hierarchy) ---
    if filename == "compare_spatial_attention.py":
        inp = swatch_chart(
            "2 valid patches + 1 masked pad slot with 2D rotary positions off vs on",
            (
                ("Patch 0 (0, 0)", "Value = 0.20 (valid)", "#d5e5dc", "#205841"),
                ("Patch 1 (2, 1)", "Value = 0.80 (valid)", "#f7e7ba", "#8a5a19"),
                ("Patch 2 (3, 1)", "Value = 100 (masked)", "#e2e8dc", "#7b8c80"),
            ),
        )
        out = bar_chart(
            "Pooled attention score on identical inputs (Positions False vs True)",
            (
                ("Positions False", 0.500, "0.500 (equal weights)", "#527c67"),
                ("Positions True (RoPE)", 0.369, "0.369 (rotated keys)", "#205841"),
            ),
            max_val=0.6,
            note="Thesis finding (Ch. 4, §4.6.3): adding 2D positions gave no clear subtype accuracy gain at patch scale.",
        )
        return inp, out

    if filename == "compare_flat_and_hierarchical_pooling.py":
        inp = (
            '<svg viewBox="0 0 300 84" class="lab-diagram" role="img" aria-label="4 valid cells nested inside 2 valid patches and 1 empty patch">'
            '<rect x="10" y="12" width="96" height="60" rx="4" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="16" y="27" font-size="10" fill="#1b3126" font-weight="bold">Patch 1 (3 cells)</text>'
            '<text x="16" y="45" font-size="10.5" fill="#244035">[0], [0], [0]</text>'
            '<text x="16" y="61" font-size="9.5" fill="#205841">Patch mean = 0.00</text>'
            '<rect x="114" y="12" width="94" height="60" rx="4" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="120" y="27" font-size="10" fill="#1b3126" font-weight="bold">Patch 2 (1 cell)</text>'
            '<text x="120" y="45" font-size="10.5" fill="#244035">[1], <tspan fill="#888">pad, pad</tspan></text>'
            '<text x="120" y="61" font-size="9.5" fill="#8a5a19">Patch mean = 1.00</text>'
            '<rect x="216" y="12" width="74" height="60" rx="4" fill="#f0eee6" stroke="#9ab0a2" stroke-dasharray="3 3"/>'
            '<text x="222" y="27" font-size="10" fill="#536052">Patch 3 (0)</text>'
            '<text x="222" y="50" font-size="9.5" fill="#b3472a">Excluded</text>'
            "</svg>"
        )
        out = bar_chart(
            "Flat cell average vs hierarchical patch-then-core average",
            (
                ("Flat (4 cells equal)", 0.25, "0.25 ((0+0+0+1)/4)", "#8a5a19"),
                ("Hierarchical (2 patches)", 0.50, "0.50 ((0.0+1.0)/2)", "#205841"),
            ),
            max_val=0.6,
        )
        return inp, out

    # --- Goal: validation (Cross-fold ROC & recall) ---
    if filename == "summarise_validation.py":
        inp = swatch_chart(
            "Example results for grading and subtyping across two folds",
            (
                ("Grading (MAE ↓)", "Fold 0: 0.25 · Fold 1: 0.30", "#d5e5dc", "#205841"),
                ("Subtype (Acc ↑)", "Fold 0: 100% · Fold 1: 50%", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = (
            bar_chart(
                "Fold-by-fold subtype accuracy (exposing the weaker 50% fold)",
                (("Fold 0 (n=2)", 1.0, "100% (2/2)", "#205841"), ("Fold 1 (n=2)", 0.5, "50% (1/2) ⚠", "#b3472a")),
                max_val=1.0,
                note="Grading MAE was 0.25 (Fold 0) and 0.30 (Fold 1) grade points.",
            )
        )
        return inp, out

    if filename == "evaluate_subtype_roc.py":
        inp = mini_table(
            "Four ranked subtype predictions (including tied score at 0.60)",
            ("Rank", "True label", "Predicted ABC score", "Note"),
            (
                ("1", "ABC (+)", "0.90", "Top score → TP=1, FP=0"),
                ("2–3 (tie)", "GCB (−) & ABC (+)", "0.60 (tied)", "Both enter together → TP=2, FP=1"),
                ("4", "GCB (−)", "0.20", "Lowest score → TP=2, FP=2"),
            ),
            highlight_row=1,
        )
        out = (
            '<svg viewBox="0 0 325 120" class="lab-diagram" role="img" aria-label="ROC curve plotting FPR vs TPR with area 0.875 shaded">'
            '<rect width="325" height="120" rx="6" fill="#f7f4ea"/>'
            '<polygon points="44,96 44,54 114,16 184,16 184,96" fill="#d5e5dc" opacity="0.75"/>'
            '<line x1="44" y1="96" x2="184" y2="16" stroke="#9ab0a2" stroke-dasharray="3 3"/>'
            '<polyline points="44,96 44,56 114,16 184,16" fill="none" stroke="#205841" stroke-width="2.5"/>'
            '<circle cx="44" cy="96" r="3.5" fill="#205841"/><circle cx="44" cy="56" r="3.5" fill="#205841"/>'
            '<circle cx="114" cy="16" r="4" fill="#8a5a19"/><circle cx="184" cy="16" r="3.5" fill="#205841"/>'
            '<text x="194" y="36" font-size="11" fill="#205841" font-weight="bold">AUC = 0.875</text>'
            '<text x="194" y="54" font-size="9.5" fill="#8a5a19">Tie at 0.60 → (0.5, 1.0)</text>'
            '<text x="64" y="112" font-size="9.5" fill="#244035">False Positive Rate (0 → 1) vs TPR</text>'
            "</svg>"
        )
        return inp, out

    if filename == "compare_fold_class_recall.py":
        inp = swatch_chart(
            "Each fold contains 1 ABC case and 1 GCB case (n=1 per cell)",
            (
                ("Fold 0", "ABC: 1/1 · GCB: 0/1", "#d5e5dc", "#205841"),
                ("Fold 1", "ABC: 0/1 · GCB: 1/1", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Per-fold class recall with explicit correct/total denominators",
            ("Fold", "Subtype class", "Correct / Total", "Recall"),
            (
                ("Fold 0", "ABC", "1 / 1", "1.00 (100%)"),
                ("Fold 0", "GCB", "0 / 1", "0.00 (0%)"),
                ("Fold 1", "ABC", "0 / 1", "0.00 (0%)"),
                ("Fold 1", "GCB", "1 / 1", "1.00 (100%)"),
            ),
            note="Displaying 1/1 and 0/1 prevents single-case proportions from being misread as large-sample percentages.",
        )
        return inp, out

    # --- Goal: cost (Accuracy vs compute cost) ---
    if filename == "estimate_representation_cost.py":
        inp = swatch_chart(
            "500 regions represented as raw RGB pixels vs 256-D float32 vectors",
            (
                ("RGB patch", "224×224×3 = 150,528 B", "#f7e7ba", "#8a5a19"),
                ("Feature vector", "256 × 4 B = 1,024 B", "#d5e5dc", "#205841"),
            ),
        )
        out = bar_chart(
            "Raw storage for 500 regions (147× reduction with feature vectors)",
            (
                ("RGB patches", 75.26, "75.26 MB", "#8a5a19"),
                ("Feature vectors", 0.51, "0.51 MB (147× smaller)", "#205841"),
            ),
            max_val=76.0,
        )
        return inp, out

    if filename == "rank_accuracy_compute_tradeoffs.py":
        inp = mini_table(
            "Three candidates compared on accuracy (↑), time (↓) and memory (↓)",
            ("Candidate", "Accuracy (↑)", "Time / epoch (↓)", "Peak RAM (↓)"),
            (("wide", "0.93", "40 s", "900 MiB"), ("small", "0.91", "21 s", "600 MiB"), ("slow", "0.90", "53 s", "950 MiB")),
            highlight_row=2,
        )
        out = mini_table(
            "Which candidates are worth comparing further?",
            ("Candidate", "Result", "Why"),
            (
                ("wide", "Keep", "Highest accuracy in the example."),
                ("small", "Keep", "Fastest and lowest peak memory."),
                ("slow", "Drop", "Both alternatives are faster, use less memory and have higher accuracy."),
            ),
        )
        return inp, out

    if filename == "audit_compute_measurements.py":
        inp = swatch_chart(
            "Expected run list checked for complete timing and memory logs",
            (
                ("('baseline', 0) · ⚠", "10.4 s · RAM missing", "#f7e7ba", "#8a5a19"),
                ("('compact', 0) · ✕", "No run record found", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Resource log audit distinguishing partial logs from missing runs",
            ("Run key", "Flagged status", "Follow-up action"),
            (
                ("('baseline', 0)", "missing or invalid peak_memory_mib", "Run finished (10.4 s), but memory profiling was not recorded."),
                ("('compact', 0)", "run missing", "No record for compact fold 0; launch or collect the missing job."),
            ),
        )
        return inp, out

    # --- Goal: heatmaps (Spatial score heatmaps) ---
    if filename == "map_patch_scores.py":
        inp = (
            '<svg viewBox="0 0 260 88" class="lab-diagram" role="img" aria-label="4 by 3 grid with two overlapping scored rectangles">'
            '<rect x="16" y="10" width="120" height="68" fill="#f0eee6" stroke="#9ab0a2"/>'
            '<rect x="16" y="10" width="90" height="45" fill="#527c67" fill-opacity="0.3" stroke="#205841" stroke-width="2"/>'
            '<rect x="76" y="33" width="60" height="45" fill="#b3472a" fill-opacity="0.3" stroke="#b3472a" stroke-width="2"/>'
            '<text x="20" y="26" font-size="9.5" fill="#1b3126" font-weight="bold">Patch 1 = 0.40</text>'
            '<text x="78" y="72" font-size="9.5" fill="#b3472a" font-weight="bold">Patch 2 = 0.80</text>'
            '<text x="148" y="36" font-size="10" fill="#244035">Overlap (2, 1):</text>'
            '<text x="148" y="52" font-size="10.5" fill="#205841" font-weight="bold">Mean = 0.60</text>'
            "</svg>"
        )
        out = mini_table(
            "4 × 3 spatial score grid (overlap = 0.60; uncovered cells = NaN)",
            ("Row", "x = 0", "x = 1", "x = 2", "x = 3"),
            (
                ("y = 0", "0.40", "0.40", "0.40", "NaN (unscored)"),
                ("y = 1", "0.40", "0.40", "0.60 (overlap)", "0.80"),
                ("y = 2", "NaN (unscored)", "NaN (unscored)", "0.80", "0.80"),
            ),
            highlight_row=1,
        )
        return inp, out

    if filename == "render_score_overlay.py":
        inp = figure_tag(
            "score_overlay_input.png",
            "Two outlined patches on a generated image",
            "Input (64 × 48 px): Patch 1 = 0.30, Patch 2 = 0.80. The rectangles overlap in the centre.",
        )
        out = (
            figure_tag(
                "score_overlay_output.png",
                "Heatmap of the same overlapping patches, with unscored pixels hatched",
                "Output (64 × 48 px): Overlap averages 0.30 and 0.80 to 0.55. Hatched pixels have no score.",
            )
            + swatch_chart(
                "Shared heatmap colour legend",
                (
                    ("0.30 · Lower", "Patch 1", "#f9d56e", "#8a5a19"),
                    ("0.55 · Overlap", "Mean of 0.3 & 0.8", "#ef8a47", "#b3472a"),
                    ("0.80 · Higher", "Patch 2", "#d94f3d", "#8a2be2"),
                ),
            )
        )
        return inp, out

    if filename == "summarise_overlay_coverage.py":
        inp = (
            '<svg viewBox="0 0 300 80" class="lab-diagram" role="img" aria-label="2 by 2 grid with 3 ROI points: 0.40, unscored NaN, and 0.80">'
            '<rect x="14" y="10" width="54" height="28" rx="3" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="20" y="28" font-size="10" fill="#1b3126" font-weight="bold">ROI: 0.40</text>'
            '<rect x="72" y="10" width="54" height="28" rx="3" fill="#f5d0c5" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="78" y="28" font-size="10" fill="#b3472a" font-weight="bold">ROI: NaN</text>'
            '<rect x="14" y="42" width="54" height="28" rx="3" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="20" y="60" font-size="10" fill="#1b3126" font-weight="bold">ROI: 0.80</text>'
            '<rect x="72" y="42" width="54" height="28" rx="3" fill="#e2e8dc" stroke="#9ab0a2" stroke-dasharray="2 2"/>'
            '<text x="76" y="60" font-size="9.5" fill="#536052">Outside: 0.50</text>'
            '<text x="140" y="34" font-size="10.5" fill="#205841" font-weight="bold">2 of 3 ROI points scored</text>'
            '<text x="140" y="52" font-size="10" fill="#536052">Median = 0.60 · Range 0.4–0.8</text>'
            "</svg>"
        )
        out = stat_cards(
            (("ROI coverage", "66.7% (2/3)"), ("Median score", "0.60"), ("Score range", "0.40–0.80"), ("Unscored in ROI", "1 point (NaN)")),
        )
        return inp, out

    # --- Goal: explain (Dimming & perturbation) ---
    if filename == "explain_prediction.py":
        inp = (
            '<svg viewBox="0 0 320 88" class="lab-diagram" role="img" aria-label="4 input regions and opposing Class A and Class B brightness masks">'
            '<text x="12" y="18" font-size="10.5" fill="#244035" font-weight="bold">Class A mask (1.00 = bright kept, 0.00 = dimmed):</text>'
            '<rect x="12" y="24" width="56" height="20" rx="3" fill="#f9ecb2" stroke="#205841" stroke-width="1.5"/><text x="26" y="38" font-size="9.5" fill="#1b3126">R1: 1.0</text>'
            '<rect x="74" y="24" width="56" height="20" rx="3" fill="#26382e"/><text x="88" y="38" font-size="9.5" fill="#fffae7">R2: 0.0</text>'
            '<rect x="136" y="24" width="56" height="20" rx="3" fill="#f9ecb2" stroke="#205841" stroke-width="1.5"/><text x="150" y="38" font-size="9.5" fill="#1b3126">R3: 1.0</text>'
            '<rect x="198" y="24" width="56" height="20" rx="3" fill="#26382e"/><text x="212" y="38" font-size="9.5" fill="#fffae7">R4: 0.0</text>'
            '<text x="12" y="58" font-size="10.5" fill="#244035" font-weight="bold">Class B mask (keeps the opposite regions):</text>'
            '<rect x="12" y="64" width="56" height="20" rx="3" fill="#26382e"/><text x="26" y="78" font-size="9.5" fill="#fffae7">R1: 0.0</text>'
            '<rect x="74" y="64" width="56" height="20" rx="3" fill="#f9ecb2" stroke="#8a5a19" stroke-width="1.5"/><text x="88" y="78" font-size="9.5" fill="#1b3126">R2: 1.0</text>'
            '<rect x="136" y="64" width="56" height="20" rx="3" fill="#26382e"/><text x="150" y="78" font-size="9.5" fill="#fffae7">R3: 0.0</text>'
            '<rect x="198" y="64" width="56" height="20" rx="3" fill="#f9ecb2" stroke="#8a5a19" stroke-width="1.5"/><text x="212" y="78" font-size="9.5" fill="#1b3126">R4: 1.0</text>'
            "</svg>"
        )
        out = bar_chart(
            "Class score before and after applying fitted dimming mask",
            (
                ("Class A baseline", 0.24, "0.24", "#7b8c80"),
                ("Class A masked", 1.16, "1.16 (+0.92)", "#205841"),
                ("Class B baseline", 0.01, "0.01", "#7b8c80"),
                ("Class B masked", 0.96, "0.96 (+0.95)", "#8a5a19"),
            ),
            max_val=1.2,
        )
        return inp, out

    if filename == "model_explanations.md":
        inp = swatch_chart(
            "Two-stage check for any highlighted tissue region",
            (
                ("1. Model check", "Targeted vs uniform control", "#d5e5dc", "#205841"),
                ("2. Biology check", "Expert & assay validation", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "What dimming masks establish vs what requires independent validation",
            ("Question", "What the mask shows", "What separate evidence is required"),
            (
                ("Model sensitivity", "Which pixels raise/lower the network's score when dimmed.", "Compare against a uniform mask of equal mean brightness."),
                ("Biological meaning", "Regions correlated with the label in this cohort.", "Pathologist review, multi-centre replication and wet-lab assays."),
            ),
        )
        return inp, out

    if filename == "test_mask_score_changes.py":
        inp = swatch_chart(
            "Targeted mask vs uniform control at identical 0.80 mean brightness",
            (
                ("Baseline (1.00)", "Score = 0.820", "#e2e8dc", "#527c67"),
                ("Uniform (0.80)", "All tiles × 0.80", "#f7e7ba", "#8a5a19"),
                ("Targeted (0.80)", "Top-left dimmed to 0.20", "#f5d0c5", "#b3472a"),
            ),
        )
        out = diverging_chart(
            "Score drop from baseline (0.820) at equal 0.80 mean brightness",
            (
                ("Uniform control", -0.164, "−0.164 (to 0.656)"),
                ("Targeted mask", -0.576, "−0.576 (to 0.244 · 3.5× drop)"),
            ),
            scale=0.6,
        )
        return inp, out

    if filename == "compare_patch_perturbations.py":
        inp = swatch_chart(
            "3-patch bag where Patch 0 favours Class 1 and Patch 2 favours Class 0",
            (
                ("Patch 0", "[0.1, 0.9] · Class 1", "#d5e5dc", "#205841"),
                ("Patch 1", "[0.2, 0.6] · Class 1", "#e2e8dc", "#527c67"),
                ("Patch 2", "[0.8, 0.1] · Class 0", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Class score shifts (Δ vs baseline) under patch removal vs repetition",
            ("Patch ID", "Remove patch Δ (Class 0, Class 1)", "Repeat-only Δ (Class 0, Class 1)", "Effect"),
            (
                ("Patch 0", "[+0.133, −0.183]", "[−0.267, +0.367]", "Drives Class 1 score"),
                ("Patch 1", "[+0.083, −0.033]", "[−0.167, +0.067]", "Moderate Class 1 contribution"),
                ("Patch 2", "[−0.217, +0.217]", "[+0.433, −0.433]", "Drives Class 0 score"),
            ),
        )
        return inp, out

    # --- Goal: cluster-runs (Schedule & resume jobs) ---
    if filename == "build_cluster_run_manifest.py":
        inp = swatch_chart(
            "Run grid expansion: 2 configs × 2 folds × 2 seeds = 8 jobs",
            (
                ("2 configs", "baseline, max_pool", "#d5e5dc", "#205841"),
                ("2 folds", "Fold 0, Fold 1", "#e2e8dc", "#527c67"),
                ("2 seeds", "Seed 7, Seed 11", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Deterministic 16-hex SHA-256 run IDs from canonical JSON specs",
            ("Job #", "run_id", "configuration", "fold", "seed", "pool"),
            (
                ("1", "55b2ba45f220d664", "baseline", "0", "7", "mean"),
                ("2", "9616e1407eb20cf1", "baseline", "0", "11", "mean"),
                ("5", "04a29607846ac864", "max_pool", "0", "7", "max"),
                ("6–8", "f2c8f509… / 59549bad… / 71b73014…", "max_pool", "0, 1", "11, 7, 11", "max"),
            ),
        )
        return inp, out

    if filename == "resume_chunked_experiment.py":
        inp = (
            '<svg viewBox="0 0 320 76" class="lab-diagram" role="img" aria-label="Three-step strip showing Chunk 1 committed, Chunk 2 interrupted, and resumption">'
            '<rect x="10" y="12" width="88" height="48" rx="4" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="16" y="30" font-size="10" fill="#1b3126" font-weight="bold">1. Chunk 2 → 4</text>'
            '<text x="16" y="46" font-size="9" fill="#205841">✓ Committed</text>'
            '<rect x="106" y="12" width="88" height="48" rx="4" fill="#f5d0c5" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="112" y="30" font-size="10" fill="#b3472a" font-weight="bold">2. Chunk 3 fails</text>'
            '<text x="112" y="46" font-size="9" fill="#536052">✕ Interrupted</text>'
            '<rect x="202" y="12" width="106" height="48" rx="4" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="208" y="30" font-size="10" fill="#1b3126" font-weight="bold">3. Resume</text>'
            '<text x="208" y="46" font-size="9" fill="#8a5a19">Reuses [4], runs 3, 4</text>'
            "</svg>"
        )
        out = mini_table(
            "Checkpoint state across interruption and retry (chunks = [2, 3, 4])",
            ("Chunk", "Run 1", "In checkpoint.json", "Run 2 (resumed)", "Final output"),
            (
                ("x = 2", "Computed 4", "✓ Saved [4]", "Skipped (reused [4])", "4"),
                ("x = 3", "InterruptedError", "Not committed", "Recomputed 3² = 9", "9"),
                ("x = 4", "Not reached", "Not committed", "Computed 4² = 16", "16"),
            ),
        )
        return inp, out

    # --- Goal: run-results (Audit completed runs) ---
    if filename == "collect_fold_results.py":
        inp = swatch_chart(
            "Result CSV streams keyed by (configuration, fold, seed)",
            (
                ("('baseline', 0, 11)", "metric = 0.28 · ✓ Unique", "#d5e5dc", "#205841"),
                ("Duplicate key", "Rejected before merge", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Collected run metrics with duplicate-key guard",
            ("Key (configuration, fold, seed)", "Metric", "Validation rule"),
            (
                ("('baseline', 0, 11)", "0.28", "✓ Accepted into summary table"),
                ("Repeated ('baseline', 0, 11)", "—", "✕ Raises ValueError('Duplicate result')"),
            ),
        )
        return inp, out

    if filename == "find_incomplete_runs.py":
        inp = swatch_chart(
            "Planned 3-job schedule audited against observed job states",
            (
                ("baseline (0, 7)", "✓ completed", "#d5e5dc", "#205841"),
                ("compact (0, 7)", "⚠ missing metrics", "#f7e7ba", "#8a5a19"),
                ("compact (1, 7)", "✕ missing run", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Incomplete runs flagged before aggregation",
            ("Run key", "State", "Action"),
            (
                ("('compact', 0, 7)", "⚠ missing metrics", "Job started but failed before writing final score; inspect log."),
                ("('compact', 1, 7)", "✕ missing", "No run record found; submit job from manifest."),
            ),
        )
        return inp, out

    # --- Goal: figures (Reproduce thesis figures) ---
    if filename == "build_grading_table.py":
        inp = swatch_chart(
            "Matched sample a scored at Core (1.6) and Patch (2.2) vs Ref (2.0)",
            (
                ("Core prediction", "|1.6 − 2.0| = 0.400", "#f7e7ba", "#8a5a19"),
                ("Patch prediction", "|2.2 − 2.0| = 0.200", "#d5e5dc", "#205841"),
            ),
        )
        out = bar_chart(
            "Aggregated mean absolute error (grade points, n = 1 matched sample)",
            (("Core scale", 0.400, "0.400 MAE", "#8a5a19"), ("Patch scale", 0.200, "0.200 MAE", "#205841")),
            max_val=0.45,
        )
        return inp, out

    if filename == "render_grading_figure.py":
        inp = bar_chart(
            "Input scale summaries passed to the SVG figure renderer (n = 6/scale)",
            (
                ("Core (n=6)", 0.350, "0.350 grade pts", "#8a5a19"),
                ("Patch (n=6)", 0.240, "0.240 grade pts ★", "#205841"),
                ("Cell (n=6)", 0.320, "0.320 grade pts", "#527c67"),
            ),
            max_val=0.40,
            note="Shorter bar = predictions stayed closer to the reference grade on the 0–3 scale.",
        )
        return inp, ""

    if filename == "run_grading_example.py":
        with (examples / "grading_case_trace.csv").open(encoding="utf-8", newline="") as stream:
            case = dict(list(csv.reader(stream))[1:])
        with (examples / "grading_predictions.csv").open(encoding="utf-8", newline="") as stream:
            predictions = {
                row["scale"]: (float(row["reference"]), float(row["prediction"]))
                for row in csv.DictReader(stream) if row["sample"] == case["Case"]
            }
        scales = ("core", "patch", "cell")
        selector = "".join(
            f'<option value="{scale}"{" selected" if scale == "patch" else ""}>{scale.title()}</option>'
            for scale in scales
        )
        panels = "".join(
            f'<div data-scale-result="{scale}"{" hidden" if scale != "patch" else ""}>'
            + stat_cards((("Reference (mean)", f"{ref:.3f}"), ("Prediction", f"{pred:.3f}"),
                          ("Absolute error", f"{abs(ref - pred):.3f}"))) + "</div>"
            for scale in scales for ref, pred in [predictions[scale]]
        )
        inp = (
            swatch_chart(
                "End-to-end trace for Case S02 (Fold 1 held-out evaluation)",
                (
                    ("Assessor A & B", "Grades 2 & 3", "#f7e7ba", "#8a5a19"),
                    ("Reference mean", "2.500 grade pts", "#e2e8dc", "#527c67"),
                    ("Held-out Fold 1", "3 scale predictions", "#d5e5dc", "#205841"),
                ),
            )
            + stat_cards((("Case", case["Case"]), ("Held-out fold", case["Validation fold"]),
                          ("Assessor A", case["Assessor A"]), ("Assessor B", case["Assessor B"])))
        )
        out = (
            f'<label class="lab-scale-picker">Image scale <select data-image-scale>{selector}</select></label>'
            f'<div aria-live="polite">{panels}</div>'
            '<p class="lab-card-note">Case S02 is 1 of 12 synthetic cases (36 predictions across 3 scales) that feed the linked grading chart.</p>'
        )
        return inp, out

    if filename == "bin_patch_distribution.py":
        rows = list(csv.DictReader(captured["stdout"].splitlines()))
        highest = max(int(row["cores"]) for row in rows)
        items = []
        table_rows = []
        examples_by_bin = ("0, 20, 42", "79", "115, 128", "209")
        for idx, row in enumerate(rows):
            low, high, count = row["lower_inclusive"], row["upper_exclusive"], int(row["cores"])
            label = f"{low}+ patches" if high == "None" else f"{low}–{int(high) - 1} patches"
            rule = f"≥ {low}" if high == "None" else f"{low} ≤ count < {high}"
            items.append((label, count, f"{count} cores", "#205841" if count >= 2 else "#8a5a19"))
            table_rows.append((label, rule, examples_by_bin[idx], str(count)))
        inp = mini_table(
            "7 core patch counts grouped into half-open bins [lower, upper)",
            ("Bin label", "Rule", "Counts in bin", "Cores"),
            table_rows,
            note="Lower-inclusive, upper-exclusive: a core with 50 patches enters 50–99, not 0–49.",
        )
        out = bar_chart("Cores in each patch-count range", items, max_val=highest)
        return inp, out

    if filename == "grading_figure.svg":
        inp = bar_chart(
            "3-scale MAE summaries feeding grading_figure.svg (12 cases/scale)",
            (
                ("Core (n=12)", 0.464, "0.464 MAE", "#8a5a19"),
                ("Patch (n=12)", 0.216, "0.216 MAE ★", "#205841"),
                ("Cell (n=12)", 0.371, "0.371 MAE", "#527c67"),
            ),
            max_val=0.50,
        )
        return inp, ""

    if filename == "verify_report_assets.py":
        inp = swatch_chart(
            "Expected report assets checked on disk and fingerprinted",
            (
                ("scores.csv · ✓", "27 B · SHA-256 verified", "#d5e5dc", "#205841"),
                ("figure.pdf · ✕", "Missing from report folder", "#f5d0c5", "#b3472a"),
            ),
        )
        out = mini_table(
            "Report asset audit and SHA-256 checksum verification",
            ("Asset", "Status", "Bytes", "SHA-256 prefix"),
            (
                ("scores.csv", "✓ Verified", "27 B", "cf1e81825e6bf460…"),
                ("figure.pdf", "✕ Missing", "—", "Flagged before publication"),
            ),
        )
        return inp, out

    # --- Goal: limits (Study limits & next tests) ---
    if filename == "research_limits.md":
        inp = swatch_chart(
            "Internal single-cohort evidence vs external multi-centre validation",
            (
                ("Internal (done)", "3-fold CV within 1 cohort", "#d5e5dc", "#205841"),
                ("External (next)", "Independent labs & scanners", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "How the study design scopes each headline thesis finding",
            ("Finding", "Internal result", "Next test required"),
            (
                ("IHC grading", "0.238 patch MAE vs rater mean (#agreement)", "Multi-centre slides scored by independent pathologists."),
                ("Subtype prediction", "0.970 acc / 0.992 AUC with UNI (#validation)", "External cohorts across different staining labs & scanners."),
                ("Spatial & masks", "No 2D RoPE gain (#subtype-ablations); masks show sensitivity (#explain)", "Whole-slide architecture tests and orthogonal wet-lab assays."),
            ),
        )
        return inp, out

    # --- Goal: pcam-bags & pcam-benchmarks (Appendix: PCam benchmark) ---
    if filename == "build_benchmark_bags.py":
        inp = swatch_chart(
            "Disjoint seeded bag manifests (4 bags/split, 4 patches/bag)",
            (
                ("Train (seed 11)", "2 pos bags (1 pos patch), 2 neg", "#d5e5dc", "#205841"),
                ("Test (seed 23)", "2 pos bags (1 pos patch), 2 neg", "#f7e7ba", "#8a5a19"),
            ),
        )
        out = mini_table(
            "Generated PCam-style bag manifests with preserved patch IDs",
            ("Split (seed)", "Bag label", "Positive patches", "Example patch IDs in bag"),
            (
                ("train (11)", "1 (positive)", "1 of 4", "train-04, train-00, train-05, train-06 (pos)"),
                ("train (11)", "0 (negative)", "0 of 4", "train-01, train-05, train-04, train-00"),
                ("test (23)", "1 (positive)", "1 of 4", "test-03, test-05, test-09 (pos), test-00"),
                ("test (23)", "0 (negative)", "0 of 4", "test-04, test-01, test-05, test-02"),
            ),
        )
        return inp, out

    if filename == "compare_benchmark_encoders.py":
        inp = swatch_chart(
            "Identical 8 train bags & 8 test bags fed to both encoders",
            (
                ("signal encoder", "Label + N(0, 0.1) noise", "#d5e5dc", "#205841"),
                ("noise encoder", "Pure N(0, 1) noise", "#f5d0c5", "#b3472a"),
            ),
        )
        out = bar_chart(
            "Held-out balanced accuracy on fixed benchmark bags (max pooling)",
            (
                ("signal encoder", 1.000, "1.000 (100%)", "#205841"),
                ("noise encoder", 0.625, "0.625 (62.5%)", "#b3472a"),
            ),
            max_val=1.0,
            note="Holding the bag manifests and max-pooling rule fixed cleanly separates the informative representation from random noise.",
        )
        return inp, out

    return "", ""


def section_tentpole(group_id):
    """Return a thesis-inspired tent-pole SVG banner for a section overview."""
    if group_id == "section-1-prepare-tissue-scales":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 128" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Multi-scale data reduction funnel from 925.93 GB whole-slide scans to cores, patches and single cells">'
            '<rect width="680" height="128" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="22" font-size="11" fill="#1b3126" font-weight="bold">Thesis Data Funnel (Fig. 1.2, 2.1 &amp; Table 2.4) · 925.9 GB raw scans → traceable cores, patches &amp; cells</text>'
            # Stage 1: Raw TMA Scans
            '<rect x="16" y="34" width="144" height="78" rx="6" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.8"/>'
            '<text x="24" y="53" font-size="10.2" fill="#1b3126" font-weight="bold">1. Whole TMA Scans</text>'
            '<text x="24" y="70" font-size="9.5" fill="#244035">63 slides · 0.25 µm/px</text>'
            '<text x="24" y="86" font-size="10" fill="#8a4b68" font-weight="bold">925.93 GB raw</text>'
            '<text x="24" y="102" font-size="9.2" fill="#536052">Too large for GPU RAM</text>'
            '<text x="165" y="76" font-size="13" fill="#205841" font-weight="bold">→</text>'
            # Stage 2: Cores
            '<rect x="180" y="34" width="150" height="78" rx="6" fill="#d5e5dc" stroke="#205841" stroke-width="1.8"/>'
            '<text x="188" y="53" font-size="10.2" fill="#1b3126" font-weight="bold">2. Tissue Cores (#crop)</text>'
            '<text x="188" y="70" font-size="9.5" fill="#244035">1,109 cores · 5,000² px</text>'
            '<text x="188" y="86" font-size="9.8" fill="#205841" font-weight="bold">5.24 GB WebP (3 s/core)</text>'
            '<text x="188" y="102" font-size="9.2" fill="#536052">1.00 prec &amp; recall</text>'
            '<text x="335" y="76" font-size="13" fill="#205841" font-weight="bold">→</text>'
            # Stage 3: Patches
            '<rect x="350" y="34" width="150" height="78" rx="6" fill="#d5e5dc" stroke="#205841" stroke-width="1.8"/>'
            '<text x="358" y="53" font-size="10.2" fill="#1b3126" font-weight="bold">3. Patches (#patches)</text>'
            '<text x="358" y="70" font-size="9.5" fill="#244035">229,683 tiles · 256² px</text>'
            '<text x="358" y="86" font-size="9.8" fill="#205841" font-weight="bold">3.63 GB WebP (−86.5%)</text>'
            '<text x="358" y="102" font-size="9.2" fill="#536052">Otsu tissue mask ≥ 50%</text>'
            '<text x="505" y="76" font-size="13" fill="#205841" font-weight="bold">→</text>'
            # Stage 4: Single Cells
            '<rect x="520" y="34" width="144" height="78" rx="6" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.8"/>'
            '<text x="528" y="53" font-size="10.2" fill="#1b3126" font-weight="bold">4. Single Cells (#cells)</text>'
            '<text x="528" y="70" font-size="9.5" fill="#244035">9,126,415 instances</text>'
            '<text x="528" y="86" font-size="9.8" fill="#8a5a19" font-weight="bold">12.51 GB HDF5/NPZ</text>'
            '<text x="528" y="102" font-size="9.2" fill="#536052">Exact (x, y) scan coords</text>'
            "</svg></figure>"
        )

    if group_id == "section-2-compress-into-features":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 132" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Three representation families compared on latent geometry and downstream cluster separation">'
            '<rect width="680" height="132" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="22" font-size="11" fill="#1b3126" font-weight="bold">Three ways to describe an image patch</text>'
            # Card 1: Autoencoder / VAE
            '<rect x="16" y="34" width="204" height="84" rx="6" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.6"/>'
            '<text x="26" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">1. Rebuild the patch</text>'
            '<text x="26" y="68" font-size="9.4" fill="#244035">Compress the patch, then rebuild it</text>'
            '<circle cx="48" cy="94" r="13" fill="#8a4b68" opacity="0.35"/><circle cx="54" cy="92" r="11" fill="#8a4b68" opacity="0.45"/>'
            '<text x="76" y="90" font-size="9.4" fill="#8a4b68" font-weight="bold">Groups overlap</text>'
            '<text x="76" y="105" font-size="9" fill="#536052">Silhouette: 0.015 · DB: 2.81</text>'
            # Card 2: Barlow Twins Contrastive
            '<rect x="238" y="34" width="204" height="84" rx="6" fill="#d5e5dc" stroke="#205841" stroke-width="1.8"/>'
            '<text x="248" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">2. Learn from two views</text>'
            '<text x="248" y="68" font-size="9.4" fill="#244035">Find what two versions have in common</text>'
            '<circle cx="262" cy="88" r="6.5" fill="#205841"/><circle cx="278" cy="100" r="6.5" fill="#8a5a19"/><circle cx="292" cy="86" r="6.5" fill="#b3472a"/>'
            '<text x="306" y="90" font-size="9.4" fill="#205841" font-weight="bold">Clearer groups</text>'
            '<text x="306" y="105" font-size="9" fill="#244035">Silhouette: 0.408</text>'
            # Card 3: Pretrained Frozen Backbones
            '<rect x="460" y="34" width="204" height="84" rx="6" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.6"/>'
            '<text x="470" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">3. Reuse a trained model</text>'
            '<text x="470" y="68" font-size="9.4" fill="#244035">Read out features from ResNet or UNI</text>'
            '<text x="470" y="88" font-size="9.4" fill="#8a5a19" font-weight="bold">Less storage than raw image patches</text>'
            '<text x="470" y="105" font-size="9" fill="#536052">Keep each patch’s original coordinates</text>'
            "</svg><figcaption>Thesis, chapter 2, figures 2.7–2.9 and 2.16–2.18.</figcaption></figure>"
        )

    if group_id == "section-3-task-1-staining-grades":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 132" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Attention-MIL grading pipeline and multi-scale MAE comparison against inter-observer disagreement">'
            '<rect width="680" height="132" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="22" font-size="11" fill="#1b3126" font-weight="bold">Task 1 · Expert IHC Staining Grades (Ch. 3, Fig. 3.3, 3.8 &amp; 3.10) · Attention-MIL vs Human Gap</text>'
            # Left: Attention-MIL 5-step flow
            '<rect x="16" y="34" width="330" height="84" rx="6" fill="#eef2eb" stroke="#9ab0a2"/>'
            '<text x="26" y="51" font-size="10.2" fill="#1b3126" font-weight="bold">5-Step Attention-MIL Grader (Fig. 3.3):</text>'
            '<text x="26" y="68" font-size="9.4" fill="#244035">1. N patch vectors → 2. Shared attention → 3. Softmax α_i</text>'
            '<text x="26" y="84" font-size="9.4" fill="#244035">4. Weighted sum → 5. 8 logits (Null + 0.0..3.0 half-steps)</text>'
            '<text x="26" y="104" font-size="9" fill="#205841" font-weight="bold">✓ Grouped folds + hybrid loss/rarity sampler (81-run grid)</text>'
            # Right: Scale MAE bars vs Expert gap
            '<text x="364" y="48" font-size="10.2" fill="#1b3126" font-weight="bold">Held-out MAE (0–3 scale, lower is closer):</text>'
            '<text x="364" y="67" font-size="9.8" fill="#205841" font-weight="bold">Patch-ResNet</text>'
            '<rect x="456" y="56" width="95" height="13" rx="3" fill="#205841"/><text x="557" y="67" font-size="9.8" fill="#205841" font-weight="bold">0.238 MAE ★</text>'
            '<text x="364" y="85" font-size="9.8" fill="#244035">Cell-Image</text>'
            '<rect x="456" y="74" width="111" height="13" rx="3" fill="#527c67"/><text x="573" y="85" font-size="9.8" fill="#244035">0.278 MAE</text>'
            '<text x="364" y="103" font-size="9.8" fill="#244035">Core-ResNet</text>'
            '<rect x="456" y="92" width="138" height="13" rx="3" fill="#8a5a19"/><text x="600" y="103" font-size="9.8" fill="#8a5a19">0.346 MAE</text>'
            '<text x="364" y="120" font-size="9.8" fill="#b3472a" font-weight="bold">Rater gap |A−B|</text>'
            '<rect x="456" y="109" width="152" height="13" rx="3" fill="#b3472a"/><text x="614" y="120" font-size="9.8" fill="#b3472a" font-weight="bold">0.382 gap</text>'
            "</svg></figure>"
        )

    if group_id == "section-4-task-2-subtype-labels":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 132" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Cohort curation funnel, parallel transformer architecture and scale jump in subtype ROC AUC">'
            '<rect width="680" height="132" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="22" font-size="11" fill="#1b3126" font-weight="bold">Task 2 · ABC vs GCB Subtype Prediction (Ch. 4, Fig. 4.2–4.6 &amp; Table 4.4) · Scale Jump &amp; RoPE Ablation</text>'
            # Left: Cohort funnel & Transformer
            '<rect x="16" y="34" width="328" height="84" rx="6" fill="#eef2eb" stroke="#9ab0a2"/>'
            '<text x="26" y="51" font-size="10.2" fill="#1b3126" font-weight="bold">Audited Cohort Funnel (Fig. 4.2): 1,109 → 962 cores</text>'
            '<text x="26" y="67" font-size="9.2" fill="#244035">Filters: cell ≤ 220 px · patches ≥ 87 · cells ≥ 1,000 · gap ≤ 1</text>'
            '<text x="26" y="85" font-size="10.2" fill="#1b3126" font-weight="bold">4-Block Parallel Transformer (Fig. 4.3):</text>'
            '<text x="26" y="101" font-size="9" fill="#8a5a19" font-weight="bold">Negative result (§4.6.3): 2D RoPE gave no patch subtype gain</text>'
            # Right: Scale jump in AUC
            '<text x="356" y="48" font-size="10.2" fill="#1b3126" font-weight="bold">3-Fold Macro ROC AUC by Scale (Fig. 4.5):</text>'
            '<text x="356" y="67" font-size="9.8" fill="#205841" font-weight="bold">Patch · UNI</text>'
            '<rect x="454" y="56" width="148" height="13" rx="3" fill="#205841"/><text x="608" y="67" font-size="9.8" fill="#205841" font-weight="bold">0.992 ★</text>'
            '<text x="356" y="85" font-size="9.8" fill="#205841">Patch · ResNet</text>'
            '<rect x="454" y="74" width="142" height="13" rx="3" fill="#2f6f55"/><text x="602" y="85" font-size="9.8" fill="#244035">0.958</text>'
            '<text x="356" y="103" font-size="9.8" fill="#527c67">Cell · ResNet</text>'
            '<rect x="454" y="92" width="140" height="13" rx="3" fill="#527c67"/><text x="600" y="103" font-size="9.8" fill="#244035">0.952</text>'
            '<text x="356" y="120" font-size="9.8" fill="#b3472a">Core · ResNet</text>'
            '<rect x="454" y="109" width="100" height="13" rx="3" fill="#b3472a"/><text x="560" y="120" font-size="9.8" fill="#b3472a">0.675 (coarse)</text>'
            "</svg></figure>"
        )

    if group_id == "section-5-explain-verify":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 132" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Four spatial interpretability methods and SHA-256 cluster run verification pipeline">'
            '<rect width="680" height="132" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="22" font-size="11" fill="#1b3126" font-weight="bold">Spatial Interpretability &amp; Reproducibility (Fig. 3.5, 4.11–4.15) · Tracing scores back onto tissue</text>'
            '<rect x="16" y="34" width="154" height="84" rx="6" fill="#d5e5dc" stroke="#205841" stroke-width="1.6"/>'
            '<text x="24" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">1. Score Heatmaps</text>'
            '<text x="24" y="68" font-size="9.3" fill="#244035">Shared RGBA scale</text>'
            '<text x="24" y="84" font-size="9.3" fill="#205841" font-weight="bold">Hatched NaN regions</text>'
            '<text x="24" y="100" font-size="9" fill="#536052">Never conflates 0 &amp; NaN</text>'
            '<rect x="182" y="34" width="166" height="84" rx="6" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.6"/>'
            '<text x="190" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">2. Dream Dimming (XAI)</text>'
            '<text x="190" y="68" font-size="9.3" fill="#244035">Class masks + occlusion</text>'
            '<text x="190" y="84" font-size="9.3" fill="#8a4b68" font-weight="bold">3.5× score drop vs uniform</text>'
            '<text x="190" y="100" font-size="9" fill="#536052">Crisp patch/cell masks</text>'
            '<rect x="360" y="34" width="150" height="84" rx="6" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.6"/>'
            '<text x="368" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">3. Cluster Checkpoints</text>'
            '<text x="368" y="68" font-size="9.3" fill="#244035">16-hex SHA-256 run IDs</text>'
            '<text x="368" y="84" font-size="9.3" fill="#8a5a19" font-weight="bold">Atomic chunk resume</text>'
            '<text x="368" y="100" font-size="9" fill="#536052">Catches crashed jobs</text>'
            '<rect x="522" y="34" width="142" height="84" rx="6" fill="#d5e5dc" stroke="#205841" stroke-width="1.6"/>'
            '<text x="530" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">4. Figure Provenance</text>'
            '<text x="530" y="68" font-size="9.3" fill="#244035">Case S02 → SVG chart</text>'
            '<text x="530" y="84" font-size="9.3" fill="#205841" font-weight="bold">SHA-256 asset audit</text>'
            '<text x="530" y="100" font-size="9" fill="#536052">+ Multi-centre limits</text>'
            "</svg></figure>"
        )

    if group_id == "section-6-appendix-pcam-benchmark":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="PCam synthetic multiple-instance bag benchmark comparing signal and noise encoders">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="22" font-size="11" fill="#1b3126" font-weight="bold">External Bag Benchmark (Appendix) · Disjoint Seeded Bag Manifests &amp; Max-Pooling Separation</text>'
            '<rect x="16" y="34" width="314" height="68" rx="6" fill="#d5e5dc" stroke="#205841" stroke-width="1.6"/>'
            '<text x="26" y="54" font-size="10.2" fill="#1b3126" font-weight="bold">1. Seeded Bag Manifests (#pcam-bags)</text>'
            '<text x="26" y="72" font-size="9.2" fill="#244035">Train (seed 11) &amp; Test (seed 23) · Pos bag = 1 pos in 4</text>'
            '<text x="26" y="89" font-size="9" fill="#205841">Locks exact patch IDs so all encoders face identical bags</text>'
            '<text x="335" y="72" font-size="13" fill="#205841" font-weight="bold">→</text>'
            '<rect x="350" y="34" width="314" height="68" rx="6" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.6"/>'
            '<text x="360" y="54" font-size="10.2" fill="#1b3126" font-weight="bold">2. Encoder Comparison (#pcam-benchmarks)</text>'
            '<text x="360" y="72" font-size="9.4" fill="#205841" font-weight="bold">Signal encoder: 1.000 bal acc ★ vs Noise: 0.625</text>'
            '<text x="360" y="89" font-size="9" fill="#536052">Max pooling isolates the single positive instance per bag</text>'
            "</svg></figure>"
        )

    return ""


def goal_tentpole(goal_id, examples=None):
    """Return a thesis-inspired tent-pole SVG diagram for a goal overview."""
    if examples is not None and (examples / "trial_waits.csv").is_file():
        return ""
    if goal_id == "question":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 124" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Thesis multi-scale hypothesis spine from 63 whole-slide scans to Task 1 staining grades and Task 2 molecular subtypes">'
            '<rect width="680" height="124" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Thesis Hypothesis Spine (Ch. 1–5) · 3 Biological Scales × 2 Clinical Tasks + Spatial Traceability</text>'
            '<rect x="16" y="34" width="148" height="76" rx="5" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.5"/>'
            '<text x="24" y="52" font-size="10" fill="#1b3126" font-weight="bold">1. Three Scales (Ch. 2)</text>'
            '<text x="24" y="68" font-size="9" fill="#244035">• 1,109 Cores (5,000² px)</text>'
            '<text x="24" y="83" font-size="9" fill="#205841" font-weight="bold">• 229k Patches (256² px)</text>'
            '<text x="24" y="98" font-size="9" fill="#244035">• 9.13M Single Cells</text>'
            '<text x="168" y="74" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<rect x="180" y="34" width="148" height="76" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="188" y="52" font-size="10" fill="#1b3126" font-weight="bold">2. Vectors (Ch. 2)</text>'
            '<text x="188" y="68" font-size="9" fill="#244035">• AE / VAE (32–256-D)</text>'
            '<text x="188" y="83" font-size="9" fill="#205841" font-weight="bold">• Barlow Twins (0.408 sil)</text>'
            '<text x="188" y="98" font-size="9" fill="#244035">• Frozen ResNet50 &amp; UNI</text>'
            '<text x="332" y="74" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<rect x="344" y="34" width="154" height="76" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="352" y="52" font-size="10" fill="#1b3126" font-weight="bold">3. Two Tasks (Ch. 3–4)</text>'
            '<text x="352" y="68" font-size="9" fill="#205841" font-weight="bold">• IHC Grade: 0.238 MAE ★</text>'
            '<text x="352" y="83" font-size="9" fill="#536052">  (vs 0.382 rater gap)</text>'
            '<text x="352" y="98" font-size="9" fill="#205841" font-weight="bold">• Subtype: 0.992 AUC ★</text>'
            '<text x="503" y="74" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<rect x="516" y="34" width="148" height="76" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="524" y="52" font-size="10" fill="#1b3126" font-weight="bold">4. Traceable (Ch. 3–5)</text>'
            '<text x="524" y="68" font-size="9" fill="#244035">• Hatched NaN heatmaps</text>'
            '<text x="524" y="83" font-size="9" fill="#8a4b68" font-weight="bold">• Dream Dimming (3.5×)</text>'
            '<text x="524" y="98" font-size="9" fill="#244035">• SHA-256 run provenance</text>'
            "</svg></figure>"
        )

    if goal_id == "storage":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Thesis Figure 2.12 WebP compression reducing 229,683 patches from 26.94 GB to 3.63 GB">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 2.12 &amp; Table 2.4 · 86.5% Storage Reduction + Pre-Flight Array Audits</text>'
            '<text x="16" y="46" font-size="10" fill="#8a5a19" font-weight="bold">PNG (229,683 patches)</text>'
            '<rect x="162" y="35" width="230" height="14" rx="3" fill="#8a5a19"/><text x="398" y="46" font-size="10" fill="#8a5a19" font-weight="bold">26.94 GB</text>'
            '<text x="16" y="68" font-size="10" fill="#205841" font-weight="bold">WebP (thesis)</text>'
            '<rect x="162" y="57" width="31" height="14" rx="3" fill="#205841"/><text x="200" y="68" font-size="10" fill="#205841" font-weight="bold">3.63 GB (−86.5% · saves 23.31 GB)</text>'
            '<text x="16" y="96" font-size="9.5" fill="#536052">• Pre-flight audit checks manifest keys vs disk shapes before GPU jobs start · Contiguous bundle avoids 20× file-open overhead.</text>'
            "</svg></figure>"
        )

    if goal_id == "frozen-features":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Frozen ResNet-50 and UNI feature extraction pipeline">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Pretrained Feature Extraction (Ch. 2 &amp; 4) · Standardised RGB → Frozen Backbone → Compact Vector Cache</text>'
            '<rect x="16" y="34" width="196" height="68" rx="5" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.5"/>'
            '<text x="26" y="53" font-size="10.5" fill="#1b3126" font-weight="bold">1. Input Standardisation</text>'
            '<text x="26" y="70" font-size="9.5" fill="#244035">Resize to 224 × 224 RGB</text>'
            '<text x="26" y="86" font-size="9.5" fill="#8a4b68">Channel norm: (I − μ) / σ</text>'
            '<text x="220" y="72" font-size="13" fill="#205841" font-weight="bold">→</text>'
            '<rect x="238" y="34" width="204" height="68" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="248" y="53" font-size="10.5" fill="#1b3126" font-weight="bold">2. Frozen Backbone Pass</text>'
            '<text x="248" y="70" font-size="9.5" fill="#205841" font-weight="bold">UNI (1024-D) / ResNet50 (2048-D)</text>'
            '<text x="248" y="86" font-size="9.5" fill="#536052">ID-ordered batch extraction</text>'
            '<text x="450" y="72" font-size="13" fill="#205841" font-weight="bold">→</text>'
            '<rect x="468" y="34" width="196" height="68" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="478" y="53" font-size="10.5" fill="#1b3126" font-weight="bold">3. Cached Float32 Arrays</text>'
            '<text x="478" y="70" font-size="9.5" fill="#8a5a19" font-weight="bold">4 bytes × width per patch</text>'
            '<text x="478" y="86" font-size="9.5" fill="#244035">147× smaller than raw RGB pixels</text>'
            "</svg></figure>"
        )

    if goal_id == "feature-benchmarks":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Latent cluster separation and planted-signal MIL bag benchmark">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Thesis Tables 2.7–2.9 &amp; MIL Signal Probe · Cluster Geometry &amp; Rare-Instance Detection</text>'
            '<rect x="16" y="34" width="318" height="72" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">1. Geometry &amp; Generalisation (Ch. 2)</text>'
            '<text x="26" y="69" font-size="9.3" fill="#205841" font-weight="bold">• Contrastive Silhouette: 0.408 vs 0.015 (AE)</text>'
            '<text x="26" y="85" font-size="9.3" fill="#244035">• PC1 + PC2 explain 97.8% + 2.2% variance in demo</text>'
            '<rect x="348" y="34" width="316" height="72" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">2. Planted-Signal Bag Probe (1 of 12 patches +5)</text>'
            '<text x="358" y="69" font-size="9.3" fill="#8a5a19">• Mean pooling: 0.830 AUC (11 noise tiles dilute signal)</text>'
            '<text x="358" y="85" font-size="9.2" fill="#205841" font-weight="bold">• Max pooling: 0.999 AUC ★ (isolates positive patch)</text>'
            "</svg></figure>"
        )

    if goal_id == "feature-export":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 112" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Coordinate-linked feature export and pre-training cache verification">'
            '<rect width="680" height="112" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Coordinate-Linked Feature Cache · Vectors Never Lose Their Tissue Bounding Box</text>'
            '<rect x="16" y="32" width="208" height="66" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="51" font-size="10.5" fill="#1b3126" font-weight="bold">1. Export With Bounds</text>'
            '<text x="26" y="68" font-size="9.5" fill="#244035">region_id + (l, t, r, b) + vector</text>'
            '<text x="26" y="84" font-size="9.2" fill="#205841">Coordinates travel in same row</text>'
            '<rect x="236" y="32" width="208" height="66" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="246" y="51" font-size="10.5" fill="#1b3126" font-weight="bold">2. Order-Safe ID Join</text>'
            '<text x="246" y="68" font-size="9.5" fill="#244035">Matches [''A'', ''B''] to [''B'', ''A'']</text>'
            '<text x="246" y="84" font-size="9.2" fill="#8a5a19">Never assumes row i == row i</text>'
            '<rect x="456" y="32" width="208" height="66" rx="5" fill="#f5d0c5" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="466" y="51" font-size="10.5" fill="#1b3126" font-weight="bold">3. Pre-Flight Cache Check</text>'
            '<text x="466" y="68" font-size="9.5" fill="#b3472a" font-weight="bold">Flags wrong encoder (v1 vs v2)</text>'
            '<text x="466" y="84" font-size="9.2" fill="#244035">&amp; verifies matrix shape (N, D)</text>'
            "</svg></figure>"
        )

    if goal_id == "grading-splits":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Reference grade consensus with assessor count and group-aware cross-validation splits">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Ch. 3 (§3.2) · Consensus Grades (Keeping Rater Count n) + Group-Aware Validation Folds</text>'
            '<rect x="16" y="34" width="318" height="68" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">1. Why Spread Needs Assessor Count (n)</text>'
            '<text x="26" y="69" font-size="9.5" fill="#244035">• Sample a (r1=1, r2=2): mean=1.5, n=2, spread=1.0</text>'
            '<text x="26" y="85" font-size="9.5" fill="#b3472a" font-weight="bold">• Sample b (r2=3 only): spread=0.0 is n=1, not agreement!</text>'
            '<rect x="348" y="34" width="316" height="68" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="358" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">2. Group-Aware Fold Assignment</text>'
            '<text x="358" y="69" font-size="9.5" fill="#205841" font-weight="bold">• Group g1 (Samples a, b) locked together in Fold 0</text>'
            '<text x="358" y="85" font-size="9.5" fill="#244035">• Prevents patient/slide leakage across train &amp; test splits</text>'
            "</svg></figure>"
        )

    if goal_id == "grading-models":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Thesis Figure 3.8 and 3.9 multi-scale grading MAE comparison and per-grade signed bias">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 3.8 &amp; 3.9 · Multi-Scale Out-of-Fold Grading Error &amp; Signed Boundary Bias</text>'
            '<text x="16" y="45" font-size="10" fill="#205841" font-weight="bold">Patch-ResNet (Attention-MIL)</text>'
            '<rect x="196" y="34" width="95" height="13" rx="3" fill="#205841"/><text x="298" y="45" font-size="10" fill="#205841" font-weight="bold">0.238 MAE ★</text>'
            '<text x="16" y="64" font-size="10" fill="#244035">Cell-Image (Attention-MIL)</text>'
            '<rect x="196" y="53" width="111" height="13" rx="3" fill="#527c67"/><text x="314" y="64" font-size="10" fill="#244035">0.278 MAE</text>'
            '<text x="16" y="83" font-size="10" fill="#8a5a19">Core-ResNet (Whole core)</text>'
            '<rect x="196" y="72" width="138" height="13" rx="3" fill="#8a5a19"/><text x="340" y="83" font-size="10" fill="#8a5a19">0.346 MAE</text>'
            '<rect x="418" y="32" width="246" height="74" rx="5" fill="#eef2eb" stroke="#9ab0a2"/>'
            '<text x="428" y="50" font-size="10" fill="#1b3126" font-weight="bold">Signed Bias by Ordinal Grade:</text>'
            '<text x="428" y="67" font-size="9.5" fill="#205841">• Grade 0: +0.45 (pulls upward)</text>'
            '<text x="428" y="83" font-size="9.5" fill="#b3472a">• Grade 3: −0.55 (pulls downward)</text>'
            '<text x="428" y="98" font-size="9" fill="#536052">Every case scored out-of-fold</text>'
            "</svg></figure>"
        )

    if goal_id == "sampling":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Dynamic loss-and-rarity sampler and generated Gaussian noise probe">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Thesis Appendix A (Alg. 3 &amp; §A.4) · Hybrid Rare/Hard Sampler &amp; Dedicated Null Class Probe</text>'
            '<rect x="16" y="34" width="318" height="68" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">1. Hybrid Sampler (Rarity + Loss + EMA)</text>'
            '<text x="26" y="69" font-size="9.2" fill="#205841" font-weight="bold">• Rare Grade 1 (s4) boosted to 0.392 probability</text>'
            '<text x="26" y="85" font-size="9.2" fill="#8a5a19">• High-loss Grade 0 (s2) boosted to 0.293 vs 0.157 easy</text>'
            '<rect x="348" y="34" width="316" height="68" rx="5" fill="#f5d0c5" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="358" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">2. Generated three-class noise probe</text>'
            '<text x="358" y="69" font-size="9.2" fill="#205841">• Tissue signal bags (n=12): 0.009 null prob (0/12)</text>'
            '<text x="358" y="85" font-size="9.2" fill="#b3472a" font-weight="bold">• Gaussian noise bags (n=12): 0.683 null prob (12/12)</text>'
            "</svg></figure>"
        )

    if goal_id == "interpret":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Bag pooling rules and size-sorted variable bag batching">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Multiple-Instance Bag Pooling &amp; Size-Sorted Batching (Ch. 4, Fig. 4.3)</text>'
            '<rect x="16" y="34" width="318" height="72" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">1. Mean vs Max vs Softmax Attention</text>'
            '<text x="26" y="69" font-size="9.2" fill="#244035">• Attention weights [0.212, 0.212, 0.576] emphasise Patch 3</text>'
            '<text x="26" y="85" font-size="9.2" fill="#205841" font-weight="bold">• Shifts pooled Feature 1 from 0.433 (mean) to 0.603</text>'
            '<rect x="348" y="34" width="316" height="72" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="52" font-size="10.2" fill="#1b3126" font-weight="bold">2. Size-Sorted Bag Batching + Validity Masks</text>'
            '<text x="358" y="69" font-size="9.2" fill="#b3472a">• Unsorted bags [3, 15] &amp; [12, 5] waste 21 pad slots</text>'
            '<text x="358" y="85" font-size="9.2" fill="#205841" font-weight="bold">• Sorted [3, 5] &amp; [12, 15] cuts padding about 74% (19 → 5 slots)</text>'
            "</svg></figure>"
        )

    if goal_id == "subtype-ablations":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="2D rotary positional encoding ablation and flat vs hierarchical cell-to-patch pooling">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Ch. 4 (§4.6.3 &amp; Fig. 4.3) · Testing 2D Spatial Positions (RoPE) &amp; Cell-to-Patch Hierarchy</text>'
            '<rect x="16" y="34" width="318" height="72" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">1. Negative Finding: 2D RoPE Positions (§4.6.3)</text>'
            '<text x="26" y="69" font-size="9.5" fill="#244035">• Rotates Q, K by (x, y) coordinates (0.500 off → 0.369 on)</text>'
            '<text x="26" y="85" font-size="9.5" fill="#8a5a19" font-weight="bold">• Added compute cost without patch-level subtype gain</text>'
            '<rect x="348" y="34" width="316" height="72" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="358" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">2. Flat vs Hierarchical Cell Pooling</text>'
            '<text x="358" y="69" font-size="9.5" fill="#244035">• Flat cell mean (0.25) lets dense patches dominate</text>'
            '<text x="358" y="85" font-size="9.5" fill="#205841" font-weight="bold">• Patch-then-core mean (0.50) weights regions equally</text>'
            "</svg></figure>"
        )

    if goal_id == "validation":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Thesis Table 4.4 and Figure 4.5 subtype validation ROC AUC across representations">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Table 4.4 &amp; Fig. 4.5 · Cross-Fold Subtype Accuracy, Macro AUC &amp; Explicit Fold Denominators</text>'
            '<text x="16" y="45" font-size="10" fill="#205841" font-weight="bold">Patch · UNI (1024-D)</text>'
            '<rect x="166" y="34" width="160" height="13" rx="3" fill="#205841"/><text x="332" y="45" font-size="10" fill="#205841" font-weight="bold">0.970 Acc · 0.992 AUC ★</text>'
            '<text x="16" y="64" font-size="10" fill="#244035">Patch · ResNet50</text>'
            '<rect x="166" y="53" width="152" height="13" rx="3" fill="#2f6f55"/><text x="324" y="64" font-size="10" fill="#244035">0.913 Acc · 0.958 AUC</text>'
            '<text x="16" y="83" font-size="10" fill="#527c67">Cell · ResNet50</text>'
            '<rect x="166" y="72" width="150" height="13" rx="3" fill="#527c67"/><text x="322" y="83" font-size="10" fill="#244035">0.892 Acc · 0.952 AUC</text>'
            '<text x="16" y="102" font-size="10" fill="#b3472a">Core · ResNet50</text>'
            '<rect x="166" y="91" width="108" height="13" rx="3" fill="#b3472a"/><text x="280" y="102" font-size="10" fill="#b3472a">0.630 Acc · 0.675 AUC</text>'
            '<rect x="466" y="32" width="198" height="74" rx="5" fill="#eef2eb" stroke="#9ab0a2"/>'
            '<text x="476" y="50" font-size="10" fill="#1b3126" font-weight="bold">Audit Rules:</text>'
            '<text x="476" y="66" font-size="9.3" fill="#244035">• Show every fold (100% vs 50%)</text>'
            '<text x="476" y="81" font-size="9.3" fill="#244035">• Tie-aware ROC step at 0.60</text>'
            '<text x="476" y="96" font-size="9.3" fill="#205841" font-weight="bold">• Show k/n beside recall</text>'
            "</svg></figure>"
        )

    if goal_id == "cost":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="147x feature compression ratio and Pareto frontier filtering">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Representation Footprint (147× Smaller) &amp; Multi-Objective Pareto Frontier</text>'
            '<rect x="16" y="34" width="318" height="72" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">1. Raw RGB vs Cached Vectors (500 regions)</text>'
            '<text x="26" y="69" font-size="9.5" fill="#8a5a19">• 224×224×3 uint8 RGB: 75.26 MB (150,528 B/patch)</text>'
            '<text x="26" y="85" font-size="9.5" fill="#205841" font-weight="bold">• 256-D float32 vector: 0.51 MB (1,024 B · 147× smaller)</text>'
            '<rect x="348" y="34" width="316" height="72" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">2. Pareto Efficiency (Acc ↑, Time ↓, RAM ↓)</text>'
            '<text x="358" y="69" font-size="9.5" fill="#205841" font-weight="bold">• Keeps undominated frontier: small (21 s) &amp; wide (0.93)</text>'
            '<text x="358" y="85" font-size="9.5" fill="#b3472a">• Drops slow (0.90 acc, 53 s, 950 MiB — beaten on all 3)</text>'
            "</svg></figure>"
        )

    if goal_id == "heatmaps":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Spatial heatmap projection with overlap averaging and hatched unscored NaN regions">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Spatial Score Projection · Averaging Overlaps &amp; Explicitly Hatching Unscored (NaN) Regions</text>'
            '<rect x="16" y="34" width="208" height="68" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">1. Coordinate Grid Map</text>'
            '<text x="26" y="69" font-size="9.5" fill="#244035">Patch 1 (0.40) ∩ Patch 2 (0.80)</text>'
            '<text x="26" y="85" font-size="9.5" fill="#205841" font-weight="bold">Overlap cell (2,1) = 0.60 mean</text>'
            '<rect x="236" y="34" width="212" height="68" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="246" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">2. Hatched Unscored Pixels</text>'
            '<text x="246" y="69" font-size="9.5" fill="#b3472a" font-weight="bold">Uncovered cells stay NaN (hatched)</text>'
            '<text x="246" y="85" font-size="9.5" fill="#244035">Never confused with a 0.0 score</text>'
            '<rect x="460" y="34" width="204" height="68" rx="5" fill="#e2e8dc" stroke="#527c67" stroke-width="1.5"/>'
            '<text x="470" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">3. ROI Coverage Receipt</text>'
            '<text x="470" y="69" font-size="9.5" fill="#205841" font-weight="bold">66.7% (2 of 3 ROI points scored)</text>'
            '<text x="470" y="85" font-size="9.5" fill="#244035">Median = 0.60 · Range 0.40–0.80</text>'
            "</svg></figure>"
        )

    if goal_id == "cluster-runs":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 112" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Deterministic SHA-256 cluster run IDs and atomic chunk checkpoint resumption">'
            '<rect width="680" height="112" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Cluster Job Provenance · Canonical SHA-256 Run IDs &amp; Atomic Checkpoint Resumption</text>'
            '<rect x="16" y="32" width="318" height="66" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">1. Deterministic Manifest (2×2×2 = 8 jobs)</text>'
            '<text x="26" y="67" font-size="9.5" fill="#205841" font-weight="bold">Canonical JSON → 16-hex SHA-256 (55b2ba45f220d664)</text>'
            '<text x="26" y="83" font-size="9.2" fill="#536052">Prevents duplicate runs &amp; names output folders uniquely</text>'
            '<rect x="348" y="32" width="316" height="66" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">2. Atomic Chunk Checkpoints</text>'
            '<text x="358" y="67" font-size="9.5" fill="#8a5a19" font-weight="bold">Chunk 2 saved [4] → Chunk 3 interrupted → Resume</text>'
            '<text x="358" y="83" font-size="9.2" fill="#244035">Reuses committed [4] and computes only unfinished [9, 16]</text>'
            "</svg></figure>"
        )

    if goal_id == "run-results":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 112" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Duplicate run guard and incomplete job state audit">'
            '<rect width="680" height="112" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Pre-Aggregation Audit · Rejecting Duplicate Keys &amp; Separating Crashed vs Unlaunched Jobs</text>'
            '<rect x="16" y="32" width="318" height="66" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">1. Duplicate-Key Guard</text>'
            '<text x="26" y="67" font-size="9.5" fill="#244035">Keyed by (configuration, fold, seed)</text>'
            '<text x="26" y="83" font-size="9.5" fill="#b3472a" font-weight="bold">Raises ValueError before silent double-counting</text>'
            '<rect x="348" y="32" width="316" height="66" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">2. Incomplete Run Triage</text>'
            '<text x="358" y="67" font-size="9.5" fill="#8a5a19" font-weight="bold">• missing metrics: job started but crashed (inspect log)</text>'
            '<text x="358" y="83" font-size="9.5" fill="#b3472a" font-weight="bold">• missing run: never launched (submit from manifest)</text>'
            "</svg></figure>"
        )

    if goal_id == "figures":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="End-to-end figure provenance from Case S02 ratings to SVG bar chart and SHA-256 verification">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">End-to-End Figure Provenance · Trace Any Error Bar Back to Case S02, Fold 1 &amp; Raw Ratings</text>'
            '<rect x="16" y="34" width="152" height="68" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="24" y="52" font-size="10" fill="#1b3126" font-weight="bold">1. Raw Ratings</text>'
            '<text x="24" y="68" font-size="9.3" fill="#244035">Case S02: A=2, B=3</text>'
            '<text x="24" y="84" font-size="9.3" fill="#8a5a19" font-weight="bold">Ref mean = 2.500</text>'
            '<text x="173" y="72" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<rect x="186" y="34" width="154" height="68" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="194" y="52" font-size="10" fill="#1b3126" font-weight="bold">2. Out-of-Fold Preds</text>'
            '<text x="194" y="68" font-size="9.3" fill="#244035">12 cases × 3 scales</text>'
            '<text x="194" y="84" font-size="9.3" fill="#205841" font-weight="bold">36 held-out rows</text>'
            '<text x="345" y="72" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<rect x="358" y="34" width="152" height="68" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="366" y="52" font-size="10" fill="#1b3126" font-weight="bold">3. SVG Bar Chart</text>'
            '<text x="366" y="68" font-size="9.3" fill="#205841" font-weight="bold">Patch: 0.216 MAE ★</text>'
            '<text x="366" y="84" font-size="9.3" fill="#536052">vs 0.371 cell, 0.464 core</text>'
            '<text x="515" y="72" font-size="12" fill="#205841" font-weight="bold">→</text>'
            '<rect x="528" y="34" width="136" height="68" rx="5" fill="#e2e8dc" stroke="#527c67" stroke-width="1.5"/>'
            '<text x="536" y="52" font-size="10" fill="#1b3126" font-weight="bold">4. Asset Audit</text>'
            '<text x="536" y="68" font-size="9.3" fill="#244035">SHA-256 checksums</text>'
            '<text x="536" y="84" font-size="9.3" fill="#b3472a" font-weight="bold">Flags missing PDFs</text>'
            "</svg></figure>"
        )

    if goal_id == "limits":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 112" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Scope boundary between internal single-cohort cross-validation and external multi-centre validation">'
            '<rect width="680" height="112" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Ch. 5 (§§5.5–5.6) · Internal Cohort Evidence vs External Multi-Centre Validation</text>'
            '<rect x="16" y="32" width="318" height="66" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">Established Within Main TMA Cohort (3-Fold CV)</text>'
            '<text x="26" y="67" font-size="9.5" fill="#205841" font-weight="bold">• Patch IHC grading: 0.238 MAE · Subtype UNI: 0.992 AUC</text>'
            '<text x="26" y="83" font-size="9.2" fill="#244035">• Controlled comparisons on identical splits &amp; seeds</text>'
            '<rect x="348" y="32" width="316" height="66" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">Required Before Clinical Deployment</text>'
            '<text x="358" y="67" font-size="9.5" fill="#8a5a19" font-weight="bold">• Independent hospitals, staining protocols &amp; scanners</text>'
            '<text x="358" y="83" font-size="9.2" fill="#244035">• Whole-slide architecture tests &amp; wet-lab assay checks</text>'
            "</svg></figure>"
        )

    if goal_id in ("pcam-bags", "pcam-benchmarks"):
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 112" class="lab-diagram lab-tentpole-svg" role="img" aria-label="PCam seeded bag construction and max-pooling encoder benchmark">'
            '<rect width="680" height="112" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">PCam Multiple-Instance Benchmark · Disjoint Seeded Splits (Seeds 11 &amp; 23) + Max-Pooling Probe</text>'
            '<rect x="16" y="32" width="318" height="66" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="26" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">Positive Bag = 1 Positive Patch + 3 Negative</text>'
            '<text x="26" y="67" font-size="9.5" fill="#244035">Negative Bag = 4 Negative Patches (0 positive)</text>'
            '<text x="26" y="83" font-size="9.2" fill="#205841">Exact patch IDs locked in manifest across encoders</text>'
            '<rect x="348" y="32" width="316" height="66" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="358" y="50" font-size="10.5" fill="#1b3126" font-weight="bold">Held-Out Balanced Accuracy (8 test bags)</text>'
            '<text x="358" y="67" font-size="9.5" fill="#205841" font-weight="bold">• Signal encoder: 1.000 (100%) ★</text>'
            '<text x="358" y="83" font-size="9.5" fill="#b3472a">• Random noise encoder: 0.625 (62.5%)</text>'
            "</svg></figure>"
        )

    if goal_id == "crop":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 134" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Four core extraction methods from Thesis Figure 2.3 and Table 2.5">'
            '<rect width="680" height="134" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Thesis Fig. 2.3 &amp; Table 2.5 · Comparing 4 ways to locate tissue microarray cores</text>'
            # Panel 1: Hough
            '<rect x="16" y="32" width="152" height="88" rx="5" fill="#f5d0c5" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="22" y="49" font-size="9.8" fill="#b3472a" font-weight="bold">1. Hough circles (0.06 s)</text>'
            '<circle cx="52" cy="74" r="13" fill="#c98ca7" stroke="#205841" stroke-width="1.5"/>'
            '<circle cx="92" cy="74" r="13" fill="#c98ca7" opacity="0.4" stroke="#b3472a" stroke-dasharray="3 2"/>'
            '<circle cx="130" cy="70" r="9" fill="none" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="22" y="108" font-size="9" fill="#1b3126">0.89 recall · misses 11%</text>'
            # Panel 2: Tilted Grid
            '<rect x="180" y="32" width="152" height="88" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="186" y="49" font-size="9.8" fill="#8a5a19" font-weight="bold">2. Tilted grid (0.5 s)</text>'
            '<line x1="202" y1="62" x2="310" y2="78" stroke="#8a5a19" stroke-dasharray="3 2"/>'
            '<circle cx="216" cy="64" r="11" fill="#c98ca7"/><rect x="204" y="52" width="24" height="24" fill="none" stroke="#205841"/>'
            '<circle cx="292" cy="66" r="11" fill="#c98ca7"/><rect x="274" y="64" width="24" height="24" fill="none" stroke="#b3472a" stroke-width="1.8"/>'
            '<text x="186" y="108" font-size="9" fill="#1b3126">0.98 prec · clips drifted</text>'
            # Panel 3: Manual Rectangles
            '<rect x="344" y="32" width="152" height="88" rx="5" fill="#e2e8dc" stroke="#527c67" stroke-width="1.5"/>'
            '<text x="350" y="49" font-size="9.8" fill="#244035" font-weight="bold">3. Drawn boxes (6.0 s)</text>'
            '<circle cx="384" cy="74" r="12" fill="#c98ca7"/><rect x="368" y="56" width="30" height="36" fill="none" stroke="#527c67" stroke-dasharray="3 2"/>'
            '<circle cx="446" cy="74" r="12" fill="#c98ca7"/><rect x="426" y="60" width="38" height="28" fill="none" stroke="#527c67" stroke-dasharray="3 2"/>'
            '<text x="350" y="108" font-size="9" fill="#1b3126">1.00 prec/rec · uneven</text>'
            # Panel 4: 1-Click Fixed Square
            '<rect x="508" y="32" width="156" height="88" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="2"/>'
            '<text x="514" y="49" font-size="9.8" fill="#205841" font-weight="bold">4. 1-click box (3.0 s ★)</text>'
            '<circle cx="552" cy="74" r="12" fill="#c98ca7"/><rect x="536" y="58" width="32" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<circle cx="552" cy="74" r="2.5" fill="#1b3126"/>'
            '<circle cx="616" cy="74" r="12" fill="#c98ca7"/><rect x="600" y="58" width="32" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<circle cx="616" cy="74" r="2.5" fill="#1b3126"/>'
            '<text x="514" y="108" font-size="9" fill="#205841" font-weight="bold">1.00 prec/rec · 5000² px</text>'
            "</svg></figure>"
        )

    if goal_id == "prepare":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 112" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Reversible coordinate mapping between downsampled preview crops and full-resolution whole-slide scans">'
            '<rect width="680" height="112" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Reversible Coordinate Chain · Every crop records its source scan origin and scale factor</text>'
            '<rect x="16" y="32" width="190" height="66" rx="5" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.5"/>'
            '<text x="26" y="51" font-size="10.2" fill="#1b3126" font-weight="bold">1. Preview Mark (1.25×)</text>'
            '<text x="26" y="68" font-size="9.3" fill="#244035">Local box: (10, 8) → (30, 28)</text>'
            '<text x="26" y="84" font-size="9.3" fill="#8a4b68">Saved in crops.csv manifest</text>'
            '<text x="218" y="68" font-size="12.5" fill="#205841" font-weight="bold">→ ×Scale + Origin →</text>'
            '<rect x="348" y="32" width="316" height="66" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.8"/>'
            '<text x="358" y="51" font-size="10.2" fill="#1b3126" font-weight="bold">2. Full-Resolution Scan Coordinates (50×)</text>'
            '<text x="358" y="68" font-size="9.3" fill="#205841" font-weight="bold">Scan = (1200, 800) + 4 × Local = (1240, 832, 1320, 912)</text>'
            '<text x="358" y="84" font-size="9" fill="#536052">Projects any patch or cell score back onto the source slide</text>'
            "</svg></figure>"
        )

    if goal_id == "patches":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 124" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Full bounding grid tiling over circular tissue core with Otsu foreground threshold">'
            '<rect width="680" height="124" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 2.4 &amp; 2.5 · Full-Core Grid Tiling + Otsu Tissue Mask (mean 207 ± 61 patches/core)</text>'
            # Circular core with grid
            '<circle cx="74" cy="74" r="38" fill="#c98ca7" opacity="0.85"/>'
            '<g fill="none" stroke="#205841" stroke-width="1.2">'
            '<rect x="34" y="34" width="26" height="26"/><rect x="60" y="34" width="26" height="26"/><rect x="86" y="34" width="26" height="26"/>'
            '<rect x="34" y="60" width="26" height="26"/><rect x="60" y="60" width="26" height="26"/><rect x="86" y="60" width="26" height="26"/>'
            '<rect x="34" y="86" width="26" height="26"/><rect x="60" y="86" width="26" height="26"/><rect x="86" y="86" width="26" height="26"/>'
            "</g>"
            '<text x="132" y="48" font-size="10.5" fill="#1b3126" font-weight="bold">Why tile the full bounding box?</text>'
            '<text x="132" y="65" font-size="9.6" fill="#244035">• An inscribed inner square discards peripheral rim tissue.</text>'
            '<text x="132" y="81" font-size="9.6" fill="#205841" font-weight="bold">• Otsu red mask + ≥ 50% coverage keeps rim tissue &amp; drops glass.</text>'
            '<text x="132" y="97" font-size="9.6" fill="#b3472a">• Explicit 0-patch core counter catches empty/damaged cores early.</text>'
            '<rect x="488" y="36" width="176" height="74" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="498" y="55" font-size="10.5" fill="#1b3126" font-weight="bold">Cohort Yield (Table 2.4)</text>'
            '<text x="498" y="73" font-size="10" fill="#205841" font-weight="bold">229,683 patches kept</text>'
            '<text x="498" y="89" font-size="9.5" fill="#244035">256 × 256 px · 3.63 GB WebP</text>'
            '<text x="498" y="103" font-size="9.2" fill="#536052">207 ± 61 patches per core</text>'
            "</svg></figure>"
        )

    if goal_id == "cells":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 124" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Cellpose gradient flow segmentation and 2D anomaly filter across 9.13M cells">'
            '<rect width="680" height="124" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 2.6 &amp; 2.14 · Cellpose Instance Flows → 9,126,415 Cells + Core Concentration Audit</text>'
            '<rect x="16" y="34" width="206" height="76" rx="5" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.5"/>'
            '<text x="26" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">1. Cellpose Flows (Fig. 2.6)</text>'
            '<text x="26" y="69" font-size="9.5" fill="#244035">Horizontal/vertical gradients → masks</text>'
            '<text x="26" y="85" font-size="9.5" fill="#8a4b68" font-weight="bold">Size gate rejects specks &amp; vacuoles</text>'
            '<text x="26" y="100" font-size="9.2" fill="#536052">Max cell diameter ≤ 220 px</text>'
            '<rect x="236" y="34" width="210" height="76" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="246" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">2. Global Scan Indexing</text>'
            '<text x="246" y="69" font-size="9.5" fill="#244035">Scan (x, y) = Core Origin + Offset</text>'
            '<text x="246" y="85" font-size="9.5" fill="#205841" font-weight="bold">Packed into aligned NPZ / HDF5</text>'
            '<text x="246" y="100" font-size="9.2" fill="#536052">IDs + coords + vectors in lockstep</text>'
            '<rect x="460" y="34" width="204" height="76" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="470" y="52" font-size="10.5" fill="#1b3126" font-weight="bold">3. Per-Core Audit (Fig. 2.14)</text>'
            '<text x="470" y="69" font-size="9.5" fill="#244035">8,229 ± 3,664 cells/core (mean)</text>'
            '<text x="470" y="85" font-size="9.5" fill="#b3472a" font-weight="bold">Flags 0-cell &amp; dominant cores</text>'
            '<text x="470" y="100" font-size="9.2" fill="#536052">Gate: ≥ 1,000 cells/core required</text>'
            "</svg></figure>"
        )

    if goal_id == "autoencoder":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 120" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Comparison of deterministic autoencoder, variational autoencoder and bottleneck width trade-off">'
            '<rect width="680" height="120" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Thesis Fig. 2.7 &amp; 2.8 · Deterministic AE vs Variational (μ, log σ²) &amp; Bottleneck Byte Trade-Off</text>'
            '<rect x="16" y="32" width="212" height="74" rx="5" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.5"/>'
            '<text x="26" y="50" font-size="10.2" fill="#1b3126" font-weight="bold">Standard Autoencoder</text>'
            '<text x="26" y="67" font-size="9.3" fill="#244035">Patch → Bottleneck z → Decoded</text>'
            '<text x="26" y="83" font-size="9.3" fill="#8a4b68" font-weight="bold">2 numbers cut MSE 2.9× vs 1 number</text>'
            '<text x="26" y="98" font-size="9" fill="#536052">Worst-first MSE queue flags outliers</text>'
            '<rect x="240" y="32" width="212" height="74" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="250" y="50" font-size="10.2" fill="#1b3126" font-weight="bold">Variational (VAE / NVAE)</text>'
            '<text x="250" y="67" font-size="9.3" fill="#244035">Splits code into mean μ &amp; log σ²</text>'
            '<text x="250" y="83" font-size="9.3" fill="#8a5a19" font-weight="bold">Loss = BCE (0.387) + β·KL (0.042)</text>'
            '<text x="250" y="98" font-size="9" fill="#536052">Prevents unregularised code spikes</text>'
            '<rect x="464" y="32" width="200" height="74" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="472" y="50" font-size="10.2" fill="#1b3126" font-weight="bold">Thesis Finding (Fig. 2.16)</text>'
            '<text x="472" y="67" font-size="9.3" fill="#244035">Reconstructing every pixel forces</text>'
            '<text x="472" y="82" font-size="9.3" fill="#244035">codes to store stain/background</text>'
            '<text x="472" y="98" font-size="9" fill="#b3472a" font-weight="bold">→ Motivated Barlow Twins (#features)</text>'
            "</svg></figure>"
        )

    if goal_id == "features":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 124" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Barlow Twins dual-view cross-correlation matrix pushed toward the identity matrix">'
            '<rect width="680" height="124" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11" fill="#1b3126" font-weight="bold">Thesis Fig. 2.9 &amp; 2.18 · Barlow Twins Cross-Correlation Matrix (C_ii → 1, C_ij → 0)</text>'
            '<rect x="16" y="34" width="194" height="76" rx="5" fill="#e2e8dc" stroke="#527c67" stroke-width="1.5"/>'
            '<text x="24" y="52" font-size="10" fill="#1b3126" font-weight="bold">1. Paired Views (seed=9)</text>'
            '<text x="24" y="69" font-size="9" fill="#244035">View A (×0.94) &amp; View B (flip, ×1.04)</text>'
            '<text x="24" y="85" font-size="9" fill="#205841" font-weight="bold">Shared patch ID + shared encoder W</text>'
            '<text x="24" y="100" font-size="8.8" fill="#536052">ResNet-50 → 2048 → 128 → 64 → 8-D</text>'
            # Cross-correlation matrix graphic
            '<rect x="220" y="34" width="222" height="76" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.8"/>'
            '<text x="230" y="51" font-size="10" fill="#1b3126" font-weight="bold">2. Cross-Correlation C → Identity</text>'
            '<rect x="232" y="58" width="14" height="14" fill="#205841"/><rect x="248" y="58" width="14" height="14" fill="#f7f4ea"/><rect x="264" y="58" width="14" height="14" fill="#f7f4ea"/>'
            '<rect x="232" y="74" width="14" height="14" fill="#f7f4ea"/><rect x="248" y="74" width="14" height="14" fill="#205841"/><rect x="264" y="74" width="14" height="14" fill="#f7f4ea"/>'
            '<rect x="232" y="90" width="14" height="14" fill="#f7f4ea"/><rect x="248" y="90" width="14" height="14" fill="#f7f4ea"/><rect x="264" y="90" width="14" height="14" fill="#205841"/>'
            '<text x="288" y="70" font-size="9.3" fill="#205841" font-weight="bold">Diag = 1 (invariance)</text>'
            '<text x="288" y="86" font-size="9.3" fill="#b3472a" font-weight="bold">Off-diag = 0 (no dupes)</text>'
            '<text x="288" y="101" font-size="9" fill="#244035">Loss: 0.1938 → 0.0003</text>'
            '<rect x="454" y="34" width="210" height="76" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="464" y="52" font-size="10" fill="#1b3126" font-weight="bold">3. Cluster Quality (Table 2.7)</text>'
            '<text x="464" y="69" font-size="9.3" fill="#205841" font-weight="bold">Silhouette: 0.408 vs 0.015 (AE)</text>'
            '<text x="464" y="85" font-size="9.3" fill="#244035">Davies-Bouldin: 0.82 vs 2.81 (AE)</text>'
            '<text x="464" y="100" font-size="9" fill="#536052">Zero train/val overfitting gap (Ch. 2)</text>'
            "</svg></figure>"
        )

    if goal_id == "compare":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 124" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Thesis Figure 3.4 and 3.7 81-run stratified ablation comparison">'
            '<rect width="680" height="124" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 3.4 &amp; 3.7 · 81-Run Single-Change Ablation Grid (Paired by Fold &amp; Seed)</text>'
            '<text x="16" y="44" font-size="10" fill="#244035">Why balanced accuracy matters: A7 (Uniform sampling) looked best on ordinary accuracy (52.2%) by favouring majority classes,</text>'
            '<text x="16" y="58" font-size="10" fill="#244035">but dropped balanced accuracy from 45.8% to 40.8%.</text>'
            '<text x="16" y="80" font-size="10" fill="#205841" font-weight="bold">A0 Baseline (Cosine LR + Weighted)</text>'
            '<rect x="230" y="69" width="160" height="13" rx="3" fill="#205841"/><text x="398" y="80" font-size="10" fill="#205841" font-weight="bold">45.8% bal acc ★ (49.7% acc)</text>'
            '<text x="16" y="98" font-size="10" fill="#8a5a19">A7 Uniform Sampling (majority bias)</text>'
            '<rect x="230" y="87" width="142" height="13" rx="3" fill="#8a5a19"/><text x="380" y="98" font-size="10" fill="#8a5a19">40.8% bal acc (52.2% raw acc ⚠)</text>'
            '<text x="16" y="115" font-size="10" fill="#b3472a">A8 Fixed Learning Rate (no decay)</text>'
            '<rect x="230" y="104" width="126" height="13" rx="3" fill="#b3472a"/><text x="364" y="115" font-size="10" fill="#b3472a">36.6% bal acc (−9.2 pts)</text>'
            "</svg></figure>"
        )

    if goal_id == "agreement":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 128" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Sorted inter-observer disagreement curve vs model-to-consensus error from Thesis Figure 3.10">'
            '<rect width="680" height="128" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 3.10 · Sorted Human Disagreement (0.382) vs Patch Model Error (0.238) Across 1,008 Cores</text>'
            # Mini step/curve plot
            '<rect x="16" y="32" width="356" height="82" rx="4" fill="#ffffff" stroke="#b5c2b7"/>'
            '<line x1="40" y1="100" x2="356" y2="100" stroke="#9ab0a2"/>'
            # Blue step curve: human disagreement (0 on ~62% of cores, then 1.0 step)
            '<polyline points="40,100 236,100 236,52 346,52 346,38 356,38" fill="none" stroke="#3b6e8c" stroke-width="2.5"/>'
            # Orange smooth curve: model error vs mean
            '<path d="M40,94 Q180,88 260,76 T356,56" fill="none" stroke="#d95f02" stroke-width="2.2"/>'
            '<text x="48" y="48" font-size="9.5" fill="#3b6e8c" font-weight="bold">— Human |Assessor A − B| step curve (mean 0.382)</text>'
            '<text x="48" y="64" font-size="9.5" fill="#d95f02" font-weight="bold">— Patch model |Pred − Consensus| (mean 0.238 ★)</text>'
            '<text x="48" y="111" font-size="9" fill="#536052">1,008 TMA cores sorted by human rater disagreement →</text>'
            # Right explanation box
            '<rect x="386" y="32" width="278" height="82" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="396" y="51" font-size="10.5" fill="#1b3126" font-weight="bold">Why both metrics are reported together</text>'
            '<text x="396" y="68" font-size="9.5" fill="#244035">• Rater gap (0.382) compares two people directly.</text>'
            '<text x="396" y="84" font-size="9.5" fill="#205841" font-weight="bold">• Model MAE (0.238) compares against their mean.</text>'
            '<text x="396" y="100" font-size="9.5" fill="#244035">• Quadratic κ penalises multi-grade jumps by Δ².</text>'
            "</svg></figure>"
        )

    if goal_id == "subtype-cohort":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 116" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Thesis Figure 4.2 cohort curation funnel from 1,109 extracted cores to 962 curated cores">'
            '<rect width="680" height="116" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 4.2 · 6-Gate Cohort Filtering Funnel (Every Excluded Core Logged by Rule)</text>'
            '<rect x="16" y="34" width="96" height="66" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="24" y="54" font-size="10.5" fill="#1b3126" font-weight="bold">1,109 cores</text><text x="24" y="70" font-size="9" fill="#536052">Extracted</text><text x="24" y="86" font-size="9" fill="#205841">100%</text>'
            '<text x="116" y="68" font-size="11" fill="#205841">→</text>'
            '<rect x="128" y="34" width="96" height="66" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="136" y="54" font-size="10.5" fill="#1b3126" font-weight="bold">1,103 cores</text><text x="136" y="70" font-size="9" fill="#536052">Cell ≤ 220 px</text><text x="136" y="86" font-size="9" fill="#b3472a">−6 vacuoles</text>'
            '<text x="228" y="68" font-size="11" fill="#205841">→</text>'
            '<rect x="240" y="34" width="96" height="66" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="248" y="54" font-size="10.5" fill="#1b3126" font-weight="bold">1,021 cores</text><text x="248" y="70" font-size="9" fill="#536052">Patches ≥ 87</text><text x="248" y="86" font-size="9" fill="#b3472a">−82 sparse</text>'
            '<text x="340" y="68" font-size="11" fill="#205841">→</text>'
            '<rect x="352" y="34" width="96" height="66" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="360" y="54" font-size="10.5" fill="#1b3126" font-weight="bold">1,003 cores</text><text x="360" y="70" font-size="9" fill="#536052">Cells ≥ 1,000</text><text x="360" y="86" font-size="9" fill="#b3472a">−18 low cell</text>'
            '<text x="452" y="68" font-size="11" fill="#205841">→</text>'
            '<rect x="464" y="34" width="92" height="66" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="472" y="54" font-size="10.5" fill="#1b3126" font-weight="bold">978 cores</text><text x="472" y="70" font-size="9" fill="#536052">Rater Δ ≤ 1</text><text x="472" y="86" font-size="9" fill="#b3472a">−25 discordant</text>'
            '<text x="560" y="68" font-size="11" fill="#205841">→</text>'
            '<rect x="572" y="34" width="92" height="66" rx="4" fill="#d5e5dc" stroke="#205841" stroke-width="2"/>'
            '<text x="580" y="54" font-size="10.5" fill="#205841" font-weight="bold">962 curated</text><text x="580" y="70" font-size="9" fill="#244035">−Slide 393936</text><text x="580" y="86" font-size="9" fill="#205841" font-weight="bold">86.7% retained</text>'
            "</svg></figure>"
        )

    if goal_id == "explain":
        return (
            '<figure class="lab-figure lab-tentpole"><svg viewBox="0 0 680 128" class="lab-diagram lab-tentpole-svg" role="img" aria-label="Four XAI interpretability methods from Thesis Figure 3.5 and 4.11">'
            '<rect width="680" height="128" rx="8" fill="#f7f4ea" stroke="#cdd6ca"/>'
            '<text x="16" y="21" font-size="11.5" fill="#1b3126" font-weight="bold">Thesis Fig. 3.5 &amp; 4.11–4.15 · Four Complementary XAI Probes vs Blurry Whole-Core Grad-CAM</text>'
            '<rect x="16" y="34" width="152" height="80" rx="5" fill="#e2e8dc" stroke="#527c67" stroke-width="1.5"/>'
            '<text x="24" y="51" font-size="10" fill="#1b3126" font-weight="bold">(A) Attention Weights</text>'
            '<text x="24" y="67" font-size="9.2" fill="#244035">Softmax α_i pooling share</text>'
            '<text x="24" y="83" font-size="9.2" fill="#527c67" font-weight="bold">Shows pooled routing,</text>'
            '<text x="24" y="97" font-size="9.2" fill="#536052">not class sign (+/−)</text>'
            '<rect x="180" y="34" width="152" height="80" rx="5" fill="#d5e5dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="188" y="51" font-size="10" fill="#1b3126" font-weight="bold">(B) Singleton Repeat</text>'
            '<text x="188" y="67" font-size="9.2" fill="#244035">Bag = K copies of patch i</text>'
            '<text x="188" y="83" font-size="9.2" fill="#205841" font-weight="bold">Isolates each patch’s</text>'
            '<text x="188" y="97" font-size="9.2" fill="#536052">standalone class preference</text>'
            '<rect x="344" y="34" width="152" height="80" rx="5" fill="#f7e7ba" stroke="#8a5a19" stroke-width="1.5"/>'
            '<text x="352" y="51" font-size="10" fill="#1b3126" font-weight="bold">(C) Leave-One-Out</text>'
            '<text x="352" y="67" font-size="9.2" fill="#244035">Remove patch i from bag</text>'
            '<text x="352" y="83" font-size="9.2" fill="#8a5a19" font-weight="bold">Measures marginal Δ</text>'
            '<text x="352" y="97" font-size="9.2" fill="#536052">in context of whole bag</text>'
            '<rect x="508" y="34" width="156" height="80" rx="5" fill="#e6c5d4" stroke="#8a4b68" stroke-width="1.8"/>'
            '<text x="516" y="51" font-size="10" fill="#1b3126" font-weight="bold">(D) Dream Dimming ★</text>'
            '<text x="516" y="67" font-size="9.2" fill="#244035">Optimise mask vs fixed net</text>'
            '<text x="516" y="83" font-size="9.2" fill="#8a4b68" font-weight="bold">3.5× drop vs uniform</text>'
            '<text x="516" y="97" font-size="9.2" fill="#536052">Tested at equal brightness</text>'
            "</svg></figure>"
        )

    return ""

