"""Structured input and output visuals for each experiment leaf in the logbook."""
import csv
from html import escape
from urllib.parse import quote


def mini_table(title, headings, rows, *, note="", highlight_row=None):
    cols = "".join(f'<th scope="col">{escape(str(h))}</th>' for h in headings)
    body = []
    for idx, row in enumerate(rows):
        row_class = ' class="lab-row-highlight"' if idx == highlight_row else ""
        cells = "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
        body.append(f"<tr{row_class}>{cells}</tr>")
    caption = f"<caption>{escape(title)}</caption>" if title else ""
    note_html = f'<p class="lab-card-note">{escape(note)}</p>' if note else ""
    return (
        f'<div class="lab-evidence-table"><table class="lab-result-table">'
        f"{caption}<thead><tr>{cols}</tr></thead><tbody>{''.join(body)}</tbody></table>{note_html}</div>"
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


def leaf_visuals(filename, examples, demo, captured):
    # --- Overview ---
    if filename == "research_questions.md":
        inp = figure_tag(
            "image_scales.png",
            "Generated examples of a scan, a core, a patch and a cell crop",
            "Synthetic schematic: one whole-slide scan branches into a 5,000 × 5,000 px core (C01), patches and individual cells.",
        )
        out = (
            '<div class="lab-route-cards">'
            '<div class="lab-route-card"><p class="lab-card-note"><strong>1. Make the images usable</strong> — Can whole-slide scans be turned into traceable, compact regions that are practical to store and train on?</p>'
            '<p class="lab-next"><a href="#crop/crop_benchmark.csv">Extraction benchmark (6 s → 3 s) →</a><a href="#storage/compare_image_encodings.py">WebP storage (26.94 → 3.63 GB) →</a></p></div>'
            '<div class="lab-route-card"><p class="lab-card-note"><strong>2. Match assessor grades</strong> — How closely can models trained on cores, patches or cells reproduce expert staining scores on held-out cases?</p>'
            '<p class="lab-next"><a href="#figures/run_grading_example.py">End-to-end grading case S02 →</a><a href="#agreement/compare_assessor_errors.py">Model vs assessor gap →</a></p></div>'
            '<div class="lab-route-card"><p class="lab-card-note"><strong>3. Predict supplied subtypes</strong> — Which image representations best separate the supplied ABC and GCB subtype labels, and what drives their scores?</p>'
            '<p class="lab-next"><a href="#validation/summarise_validation.py">Fold-by-fold subtype validation →</a><a href="#explain/test_mask_score_changes.py">Dimming & perturbation checks →</a></p></div>'
            "</div>"
        )
        return inp, out

    if filename == "README.md":
        if (examples / "trial_waits.csv").is_file():
            return (
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
                "",
            )
        inp = (
            '<p class="lab-card-note"><strong>Dependencies</strong> · Python 3.9+ with NumPy and Pillow:</p>'
            '<pre class="lab-command">python -m pip install numpy pillow\npython run_grading_example.py --output grading-demo</pre>'
            '<p class="lab-card-note">Run from <code>site/research/examples/</code> to rebuild the synthetic splits, out-of-fold predictions, case trace and SVG chart.</p>'
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

    if filename == "decision.md":
        return (
            mini_table(
                "What changed between the first pilot summary and the review",
                ("Stage", "Observation", "Conclusion"),
                (
                    ("Initial pilot", "Median wait dropped from 8 min to 4 min", "Draft decision: adopt prepared arrival list"),
                    ("Session audit", "Paper list ran in morning; arrival list in afternoon", "Revised decision: alternate methods in matched time slots"),
                ),
                highlight_row=1,
            ),
            "",
        )

    # --- Pilot example ---
    if filename == "trial_waits.csv":
        return (
            stat_cards((("Paper list", "4 arrivals (morning)"), ("Arrival list", "4 arrivals (afternoon)")),
                       note="Each row records one fictional visitor wait in minutes."),
            mini_table(
                "Recorded wait times (fictional pilot)",
                ("Method", "Session", "Observed waits (min)", "Median (min)"),
                (
                    ("Paper list", "Morning", "7, 8, 9, 12", "8.5 / 8"),
                    ("Prepared arrival list", "Afternoon", "3, 4, 4, 6", "4.0"),
                ),
            ),
        )
    if filename == "summarise_waits.py":
        return (
            mini_table("Grouped observations", ("Method", "n", "Waits (min)"),
                       (("Paper list", "4", "7, 8, 9, 12"), ("Prepared list", "4", "3, 4, 4, 6"))),
            stat_cards((("Paper list median", "8 min (n=4)"), ("Prepared list median", "4 min (n=4)")),
                       note="The session notes show the two methods ran at different times of day."),
        )

    # --- Goal: crop (Mark and label tissue regions) ---
    if filename == "select_core_rectangles.py":
        inp = (
            '<svg viewBox="0 0 320 120" class="lab-diagram" role="img" aria-label="Two hand-drawn boxes of slightly different sizes around tissue cores">'
            '<rect width="320" height="120" rx="6" fill="#f7f4ea"/>'
            '<circle cx="78" cy="62" r="34" fill="#c98ca7" opacity="0.85"/>'
            '<rect x="38" y="24" width="78" height="82" fill="none" stroke="#205841" stroke-width="2" stroke-dasharray="4 2"/>'
            '<text x="42" y="20" font-size="11" fill="#205841" font-weight="bold">1A · 122 × 128 preview px</text>'
            '<circle cx="222" cy="60" r="34" fill="#c98ca7" opacity="0.85"/>'
            '<rect x="180" y="22" width="84" height="76" fill="none" stroke="#8a5a19" stroke-width="2" stroke-dasharray="4 2"/>'
            '<text x="184" y="18" font-size="11" fill="#8a5a19" font-weight="bold">1B · 129 × 123 preview px</text>'
            "</svg>"
            '<p class="lab-card-note">Preview zoom: <code>1.25×</code> · Scan multiplier: <code>50×</code> (scale factor <code>40×</code>).</p>'
        )
        out = mini_table(
            "Scaled full-scan bounds from hand-drawn boxes (generated example)",
            ("Core", "Preview box (x, y, w, h)", "Full-scan bounds (px)", "Resulting crop size"),
            (
                ("1A", "(18, 22, 122, 128)", "(720, 880, 5600, 6000)", "4,880 × 5,120 px"),
                ("1B", "(164, 20, 129, 123)", "(6560, 800, 11720, 5720)", "5,160 × 4,920 px"),
            ),
            note="Thesis Table 2.5: manual rectangles reached 1.00 precision and 1.00 recall at 6 s per sample, but every box had slightly different dimensions.",
        )
        return inp, out

    if filename == "interpolate_core_grid.py":
        inp = (
            '<svg viewBox="0 0 320 132" class="lab-diagram" role="img" aria-label="Tilted microarray grid projected from two reference corners, showing one drifted core">'
            '<rect width="320" height="132" rx="6" fill="#f7f4ea"/>'
            '<line x1="55" y1="24" x2="67" y2="108" stroke="#6b8577" stroke-width="1.5" stroke-dasharray="3 3"/>'
            '<circle cx="55" cy="24" r="13" fill="#c98ca7"/><circle cx="55" cy="24" r="3" fill="#1b3126"/>'
            '<text x="74" y="28" font-size="11" fill="#1b3126">1A corner click (20, 20)</text>'
            '<circle cx="61" cy="66" r="13" fill="#c98ca7"/>'
            '<rect x="46" y="51" width="30" height="30" fill="none" stroke="#205841" stroke-width="1.5"/>'
            '<circle cx="67" cy="108" r="13" fill="#c98ca7"/><circle cx="67" cy="108" r="3" fill="#1b3126"/>'
            '<text x="86" y="112" font-size="11" fill="#1b3126">3A corner click (26, 80)</text>'
            '<circle cx="222" cy="56" r="13" fill="#c98ca7"/>'
            '<rect x="195" y="47" width="30" height="30" fill="none" stroke="#b3472a" stroke-width="2"/>'
            '<text x="176" y="39" font-size="11" fill="#b3472a" font-weight="bold">2B drifted core (5.8 px off grid)</text>'
            "</svg>"
            '<p class="lab-card-note">Two reference clicks set the slide tilt θ and spacing; boxes are projected across rows and columns.</p>'
        )
        out = mini_table(
            "Projected grid slots vs observed core centres (generated example)",
            ("Core", "Projected centre", "Observed centre", "Centre drift", "Projected box (l, t, r, b)"),
            (
                ("1A", "(20, 20)", "(20, 20)", "0.0 px", "(5, 5, 35, 35)"),
                ("2A", "(23, 50)", "(23, 50)", "0.0 px", "(8, 35, 38, 65)"),
                ("3A", "(26, 80)", "(26, 80)", "0.0 px", "(11, 65, 41, 95)"),
                ("2B", "(53, 47)", "(58, 44)", "5.8 px (clipped)", "(38, 32, 68, 62)"),
            ),
            highlight_row=3,
            note="Thesis Table 2.5: grid projection took 0.5 s per sample with 1.00 recall, while off-grid cores reduced precision to 0.98.",
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
            '<p class="lab-card-note">Each method was evaluated on four criteria in Thesis Table 2.5 (p. 70):</p>'
            '<ul class="lab-card-list">'
            "<li><strong>Seconds per sample:</strong> human and compute time required per core.</li>"
            "<li><strong>Precision (1 − wrong selections):</strong> share of extracted regions that were valid target cores.</li>"
            "<li><strong>Recall (1 − missed cores):</strong> share of target cores on the slide that were successfully extracted.</li>"
            "<li><strong>Manual intervention:</strong> how much human guidance each slide required.</li>"
            "</ul>"
            '<p class="lab-card-note">The Hough transform result is preserved from Thesis Table 2.5 (its original script is not in the archive). '
            "Rectangle, grid and point-and-click scripts are preserved in the August 2020 archive and shown as adjacent leaves.</p>"
        )
        chart = metric_bars(
            "Thesis Table 2.5 · seconds per sample (lower is faster)",
            [(r["approach"], float(r["seconds_per_sample"]), f'{r["seconds_per_sample"]} s') for r in rows],
            max_value=6,
        )
        table = mini_table(
            "Point-and-click halved time vs rectangles (6 s → 3 s) at 1.00 precision and recall; Hough was fastest (0.06 s) and missed more cores (recall 0.89)",
            ("Approach", "Seconds / sample", "Precision (valid selections)", "Recall (cores found)", "Manual intervention"),
            [(r["approach"], f'{r["seconds_per_sample"]} s', r["precision"], r["recall"], r["manual_intervention"]) for r in rows],
            highlight_row=3,
            note="Source: Submitted thesis, Table 2.5, p. 70.",
        )
        return inp, chart + table

    if filename == "record_crop_marks.py":
        inp = (
            '<svg viewBox="0 0 288 126" class="lab-diagram" role="img" aria-label="96 by 72 scan showing Point A at (20, 16) and Rectangle B from (64, 44) to (88, 68)">'
            '<rect x="12" y="10" width="192" height="104" rx="4" fill="#f5f0e2" stroke="#9ab0a2"/>'
            '<circle cx="52" cy="36" r="14" fill="#c98ca7" opacity="0.8"/>'
            '<line x1="46" y1="36" x2="58" y2="36" stroke="#1b3126" stroke-width="2"/>'
            '<line x1="52" y1="30" x2="52" y2="42" stroke="#1b3126" stroke-width="2"/>'
            '<text x="69" y="40" font-size="11" fill="#1b3126" font-weight="bold">A · point (20, 16)</text>'
            '<circle cx="164" cy="86" r="15" fill="#c98ca7" opacity="0.8"/>'
            '<rect x="140" y="70" width="48" height="34" fill="none" stroke="#205841" stroke-width="2"/>'
            '<text x="92" y="65" font-size="11" fill="#205841" font-weight="bold">B · rectangle (64, 44)–(88, 68)</text>'
            "</svg>"
            '<p class="lab-card-note">Scan size: <code>96 × 72 px</code> · Coordinates use inclusive <code>(x, y)</code> and exclusive <code>(right, bottom)</code>.</p>'
        )
        out = mini_table(
            "Saved annotation CSV rows (2 marks on demo-scan)",
            ("image", "label", "kind", "x", "y", "right", "bottom"),
            (
                ("demo-scan", "A", "point", "20", "16", "— (blank)", "— (blank)"),
                ("demo-scan", "B", "rectangle", "64", "44", "88", "68"),
            ),
            highlight_row=0,
            note="Point rows leave right and bottom blank because fixed-size bounds are computed later during crop extraction.",
        )
        return inp, out

    # --- Goal: prepare (Extract crops and preserve their coordinates) ---
    if filename == "extract_labelled_crops.py":
        inp = (
            '<svg viewBox="0 0 280 120" class="lab-diagram" role="img" aria-label="32 by 24 source scan with two labelled crop boxes">'
            '<rect x="16" y="12" width="160" height="96" rx="4" fill="#b57594"/>'
            '<rect x="26" y="24" width="50" height="40" fill="none" stroke="#fffae7" stroke-width="2"/>'
            '<text x="28" y="21" font-size="10" fill="#fffae7" font-weight="bold">rectangle (2,3)–(12,13)</text>'
            '<rect x="121" y="44" width="40" height="32" fill="none" stroke="#f9ecb2" stroke-width="2"/>'
            '<text x="102" y="40" font-size="10" fill="#f9ecb2" font-weight="bold">crop-01 (21,8)–(29,16)</text>'
            '<rect x="200" y="18" width="36" height="36" rx="3" fill="#b57594" stroke="#205841" stroke-width="2"/>'
            '<text x="200" y="66" font-size="10" fill="#244035">crop-001.png</text>'
            '<rect x="200" y="74" width="30" height="30" rx="3" fill="#b57594" stroke="#205841" stroke-width="2"/>'
            '<text x="200" y="115" font-size="10" fill="#244035">crop-002.png</text>'
            "</svg>"
        )
        out = mini_table(
            "Generated crops.csv manifest linking each file back to demo-scan",
            ("image", "label", "file", "left (px)", "top (px)", "right (px)", "bottom (px)"),
            (
                ("demo-scan", "rectangle", "crop-001.png", "2", "3", "12", "13"),
                ("demo-scan", "crop-01", "crop-002.png", "21", "8", "29", "16"),
            ),
            highlight_row=1,
            note="Row 2 locates crop-002.png at (21, 8) to (29, 16) on demo-scan (an 8 × 8 px region).",
        )
        return inp, out

    if filename == "map_crop_to_scan.py":
        inp = (
            '<svg viewBox="0 0 320 118" class="lab-diagram" role="img" aria-label="Downsampled crop box mapped by 4x scale and offset onto the full scan">'
            '<rect x="14" y="20" width="84" height="76" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<rect x="34" y="38" width="36" height="36" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<text x="14" y="15" font-size="11" fill="#244035" font-weight="bold">Crop (1×) · box 20 × 20 px</text>'
            '<text x="22" y="88" font-size="10" fill="#244035">(10, 8) to (30, 28)</text>'
            '<text x="112" y="58" font-size="13" fill="#205841" font-weight="bold">×4 scale</text>'
            '<text x="105" y="74" font-size="10" fill="#536052">+ (1200, 800)</text>'
            '<rect x="178" y="14" width="128" height="90" rx="4" fill="#f5f0e2" stroke="#527c67"/>'
            '<rect x="214" y="34" width="56" height="52" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<text x="178" y="11" font-size="11" fill="#244035" font-weight="bold">Full scan · box 80 × 80 px</text>'
            '<text x="188" y="98" font-size="10" fill="#244035">(1240, 832) to (1320, 912)</text>'
            "</svg>"
        )
        out = mini_table(
            "Coordinate mapping from 4× downsampled crop to full scan",
            ("Coordinate", "Local crop (px)", "× 4 downsample", "+ Crop origin (px)", "Full-scan pixel"),
            (
                ("Left / Top", "(10, 8)", "(40, 32)", "+ (1200, 800)", "(1240, 832)"),
                ("Right / Bottom", "(30, 28)", "(120, 112)", "+ (1200, 800)", "(1320, 912)"),
                ("Box dimensions", "20 × 20 px", "80 × 80 px", "—", "80 × 80 px"),
            ),
            highlight_row=2,
        )
        return inp, out

    # --- Goal: patches (Build and inspect patch datasets) ---
    if filename == "filter_tissue_patches.py":
        inp = (
            '<svg viewBox="0 0 280 108" class="lab-diagram" role="img" aria-label="8 grid squares over a binary tissue mask with kept and skipped squares marked">'
            '<rect x="16" y="16" width="144" height="72" fill="#eef1eb" stroke="#9ab0a2"/>'
            '<rect x="16" y="16" width="81" height="72" fill="#c98ca7" opacity="0.8"/>'
            '<g fill="none" stroke="#244035" stroke-width="1.2">'
            '<rect x="16" y="16" width="36" height="36"/><rect x="52" y="16" width="36" height="36"/>'
            '<rect x="88" y="16" width="36" height="36"/><rect x="124" y="16" width="36" height="36"/>'
            '<rect x="16" y="52" width="36" height="36"/><rect x="52" y="52" width="36" height="36"/>'
            '<rect x="88" y="52" width="36" height="36"/><rect x="124" y="52" width="36" height="36"/>'
            "</g>"
            '<text x="23" y="38" font-size="10" fill="#1b3126" font-weight="bold">100%</text>'
            '<text x="59" y="38" font-size="10" fill="#1b3126" font-weight="bold">100%</text>'
            '<text x="97" y="38" font-size="10" fill="#b3472a" font-weight="bold">25%</text>'
            '<text x="135" y="38" font-size="10" fill="#536052">0%</text>'
            '<text x="23" y="74" font-size="10" fill="#1b3126" font-weight="bold">100%</text>'
            '<text x="59" y="74" font-size="10" fill="#1b3126" font-weight="bold">100%</text>'
            '<text x="97" y="74" font-size="10" fill="#b3472a" font-weight="bold">25%</text>'
            '<text x="135" y="74" font-size="10" fill="#536052">0%</text>'
            '<text x="172" y="38" font-size="11" fill="#205841" font-weight="bold">Threshold ≥ 50%</text>'
            '<text x="172" y="56" font-size="10" fill="#4b5c51">4 kept (100%)</text>'
            '<text x="172" y="72" font-size="10" fill="#b3472a">4 skipped (25%, 0%)</text>'
            "</svg>"
        )
        out = mini_table(
            "Tissue coverage filter across 8 grid squares (threshold ≥ 50%)",
            ("Patch ID", "Bounds (px)", "Tissue coverage", "Decision (≥ 50% rule)"),
            (
                ("patch-x0-y0, patch-x0-y4", "x=0..4", "100% (16/16 px)", "Keep"),
                ("patch-x4-y0, patch-x4-y4", "x=4..8", "100% (16/16 px)", "Keep"),
                ("patch-x8-y0, patch-x8-y4", "x=8..12", "25% (4/16 px)", "Skip (below 50% threshold)"),
                ("patch-x12-y0, patch-x12-y4", "x=12..16", "0% (0/16 px)", "Skip"),
            ),
            highlight_row=2,
        )
        return inp, out

    if filename == "summarise_patch_counts.py":
        inp = mini_table(
            "Expected cores vs saved patch manifest",
            ("Expected core ID", "Saved patch records in manifest"),
            (("A", "x0-y0, x16-y0"), ("B", "None recorded"), ("C", "x0-y0")),
            highlight_row=1,
        )
        out = metric_bars(
            "Saved patches per expected core (including zero-count cores)",
            (("Core A", 2, "2 patches"), ("Core B (missing)", 0, "0 patches"), ("Core C", 1, "1 patch")),
            max_value=2,
            note="Keeping Core B at 0 verifies that the core was expected in the cohort but produced no usable patches above the tissue threshold.",
        )
        return inp, out

    if filename == "extract_patch_images.py":
        inp = (
            '<svg viewBox="0 0 280 104" class="lab-diagram" role="img" aria-label="16 by 16 core split into four 8 by 8 patches alongside the two accepted thumbnails">'
            '<rect x="14" y="14" width="72" height="72" fill="#eef1eb" stroke="#9ab0a2"/>'
            '<rect x="14" y="14" width="54" height="36" fill="#bd7896"/>'
            '<line x1="50" y1="14" x2="50" y2="86" stroke="#244035" stroke-width="1.2"/>'
            '<line x1="14" y1="50" x2="86" y2="50" stroke="#244035" stroke-width="1.2"/>'
            '<text x="14" y="11" font-size="10" fill="#244035" font-weight="bold">core-1 (16 × 16 px)</text>'
            '<rect x="116" y="22" width="44" height="44" fill="#bd7896" stroke="#205841" stroke-width="2"/>'
            '<text x="112" y="79" font-size="10" fill="#244035">patch-x0-y0 (100%)</text>'
            '<rect x="196" y="22" width="44" height="44" fill="#eef1eb" stroke="#205841" stroke-width="2"/>'
            '<rect x="196" y="22" width="22" height="44" fill="#bd7896"/>'
            '<text x="192" y="79" font-size="10" fill="#244035">patch-x8-y0 (50%)</text>'
            "</svg>"
        )
        out = mini_table(
            "Saved patches.csv manifest (accepted patches ≥ 50% tissue)",
            ("core", "file", "left", "top", "right", "bottom", "tissue_fraction"),
            (
                ("core-1", "patch-x0-y0.png", "0", "0", "8", "8", "1.00 (100%)"),
                ("core-1", "patch-x8-y0.png", "8", "0", "16", "8", "0.50 (50%)"),
            ),
            note="The filename patch-x8-y0.png and bounds (8, 0, 16, 8) place the 50%-tissue square back on the top-right quadrant of core-1.",
        )
        return inp, out

    # --- Goal: cells (Build cell-level datasets) ---
    if filename == "extract_cell_crops.py":
        inp = (
            '<svg viewBox="0 0 290 105" class="lab-diagram" role="img" aria-label="Segmented cell regions with two accepted 8x8 cell crops and size filter bounds">'
            '<rect x="14" y="14" width="128" height="76" rx="4" fill="#dcdcdc" stroke="#9ab0a2"/>'
            '<circle cx="50" cy="46" r="10" fill="#7d4e6d"/>'
            '<rect x="34" y="30" width="32" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<text x="34" y="26" font-size="10" fill="#205841" font-weight="bold">Cell 1 (5 px)</text>'
            '<circle cx="102" cy="58" r="10" fill="#7d4e6d"/>'
            '<rect x="86" y="42" width="32" height="32" fill="none" stroke="#205841" stroke-width="2"/>'
            '<text x="84" y="38" font-size="10" fill="#205841" font-weight="bold">Cell 2 (5 px)</text>'
            '<circle cx="24" cy="78" r="2.5" fill="#888"/>'
            '<text x="160" y="32" font-size="11" fill="#244035" font-weight="bold">Allowed width: 3–7 px</text>'
            '<text x="160" y="50" font-size="10" fill="#205841">✓ Cell 1 & Cell 2 → 8 × 8 px crops</text>'
            '<text x="160" y="68" font-size="10" fill="#b3472a">✕ 1–2 px speck or >7 px clump skipped</text>'
            "</svg>"
        )
        out = mini_table(
            "Extracted 8 × 8 px cell crops with full-scan centres (origin 240, 520)",
            ("Instance", "Local centre (px)", "Scan origin offset", "Full-scan centre (px)", "Crop shape"),
            (
                ("Cell 1", "(9.0, 10.0)", "+ (240, 520)", "(249.0, 530.0)", "8 × 8 px"),
                ("Cell 2", "(22.0, 14.0)", "+ (240, 520)", "(262.0, 534.0)", "8 × 8 px"),
            ),
        )
        return inp, out

    if filename == "index_segmented_cells.py":
        inp = mini_table(
            "Core origin and local cell detections (relative to top-left of core C1)",
            ("Core ID", "Core scan origin (x, y)", "Cell ID", "Local offset in core (x, y)"),
            (
                ("C1", "(640, 480) px", "Cell 1", "(29, 18) px"),
                ("C1", "(640, 480) px", "Cell 2", "(61, 70) px"),
            ),
        )
        out = mini_table(
            "Indexed cell coordinates on the full scan (origin = top-left scan pixel 0, 0)",
            ("Cell key", "Core ID", "scan_x (px)", "scan_y (px)", "Calculation"),
            (
                ("C1 · Cell 1", "C1", "669", "498", "640 + 29, 480 + 18"),
                ("C1 · Cell 2", "C1", "701", "550", "640 + 61, 480 + 70"),
            ),
        )
        return inp, out

    if filename == "package_cell_arrays.py":
        inp = mini_table(
            "Aligned cell records before packaging (2 cells)",
            ("Row", "identifiers", "xy (scan px)", "features (float32)"),
            (("0", "C1-1", "[7, 6]", "[0.3]"), ("1", "C1-2", "[9, 3]", "[0.8]")),
        )
        out = mini_table(
            "Compressed archive arrays and round-trip check",
            ("Array name", "Shape", "Dtype", "Row 0 value (round-trip check)"),
            (
                ("identifiers", "(2,)", "str", "'C1-1'"),
                ("xy", "(2, 2)", "int", "[7, 6]"),
                ("features", "(2, 1)", "float32", "[0.3]"),
            ),
            note="Reading row 0 across all three arrays returns Cell C1-1 at [7, 6] with feature [0.3].",
        )
        return inp, out

    if filename == "summarise_cells_by_core.py":
        inp = stat_cards(
            (("Expected cores", "A, B, C"), ("Indexed cells", "A, A, A, B (4 total)")),
            note="Core A contributes 3 of the 4 cells (75%), while Core C contributes 0.",
        )
        out = metric_bars(
            "Cell count per core (showing concentration and zero-cell cores)",
            (("Core A (75% share)", 3, "3 cells"), ("Core B (25% share)", 1, "1 cell"), ("Core C (empty)", 0, "0 cells")),
            max_value=3,
            note="Total = 4 cells, median = 1 cell/core, largest core share = 75%. Reporting only total cells would hide that Core A dominates and Core C is empty.",
        )
        return inp, out

    # --- Goal: storage (Check, bundle and compress datasets) ---
    if filename == "compare_image_encodings.py":
        inp = stat_cards(
            (("Generated input", "48 × 48 RGB gradient patch"), ("WebP setting", "Quality 75")),
            note="Both encodings are decoded back to RGB pixels so file size is paired with pixel fidelity.",
        )
        out = mini_table(
            "Encoding comparison across scopes (single tiny synthetic patch vs full thesis collection)",
            ("Scope", "PNG size", "WebP size", "Mean channel diff (0–255)"),
            (
                ("One 48 × 48 synthetic gradient patch", "129 B", "174 B", "0.00 (PNG) vs 1.95 (WebP)"),
                ("Thesis patch collection (229,683 patches)", "26.94 GB", "3.63 GB (−86.5%)", "Evaluated in Thesis Ch. 2, p. 72"),
            ),
            highlight_row=1,
            note="A tiny smooth gradient compresses into 129 B with PNG's predictor, smaller than WebP's container header. On the 229,683 histological patches, WebP cut storage from 26.94 GB to 3.63 GB.",
        )
        return inp, out

    if filename == "audit_dataset_structure.py":
        inp = mini_table(
            "Expected manifest vs observed storage arrays",
            ("Dataset key", "Expected shape", "Observed in storage"),
            (
                ("A", "(10, 64)", "(10, 32)"),
                ("B", "(8, 64)", "Not found"),
                ("spillover", "Not in manifest", "(1, 64)"),
            ),
        )
        out = mini_table(
            "Three dataset faults surfaced before training",
            ("Issue type", "Affected key", "Observed vs expected", "Action before training"),
            (
                ("Wrong shape", "A", "(10, 32) vs expected (10, 64)", "Re-export A with all 64 feature columns."),
                ("Missing file", "B", "Absent vs expected (8, 64)", "Run extraction for B or check why it was skipped."),
                ("Unexpected file", "spillover", "(1, 64) not in manifest", "Quarantine or remove unindexed array."),
            ),
        )
        return inp, out

    if filename == "measure_storage_reads.py":
        inp = (
            '<svg viewBox="0 0 300 88" class="lab-diagram" role="img" aria-label="20 separate 4 KB files compared with one contiguous bundle file">'
            '<rect x="12" y="14" width="24" height="24" rx="2" fill="#e2e8dc" stroke="#527c67"/>'
            '<rect x="42" y="14" width="24" height="24" rx="2" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<rect x="72" y="14" width="24" height="24" rx="2" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<rect x="102" y="14" width="24" height="24" rx="2" fill="#c98ca7" stroke="#205841" stroke-width="2"/>'
            '<text x="136" y="30" font-size="11" fill="#244035">Separate files: open <code>2.bin</code>, <code>5.bin</code>, <code>9.bin</code></text>'
            '<rect x="12" y="52" width="114" height="24" rx="2" fill="#e2e8dc" stroke="#527c67"/>'
            '<rect x="30" y="52" width="18" height="24" fill="#c98ca7"/><rect x="60" y="52" width="18" height="24" fill="#c98ca7"/><rect x="96" y="52" width="18" height="24" fill="#c98ca7"/>'
            '<text x="136" y="68" font-size="11" fill="#244035">Single bundle: seek inside <code>bundle.bin</code></text>'
            "</svg>"
        )
        out = mini_table(
            "Local read comparison for 3 chunks × 4,096 B = 12,288 bytes",
            ("Storage layout", "Chunks read", "Total bytes verified", "Recorded local time"),
            (
                ("Separate files (0.bin … 19.bin)", "Indices 2, 5, 9", "12,288 B", "11.244 ms"),
                ("Single bundled file (bundle.bin)", "Indices 2, 5, 9", "12,288 B", "10.052 ms"),
            ),
            note="Both layouts return the same 12,288 bytes. Single-run timings vary with OS and filesystem caching.",
        )
        return inp, out

    # --- Goal: autoencoder (Learn by reconstructing images) ---
    if filename == "fit_linear_autoencoder.py":
        inp = mini_table(
            "Three 3-value input patches compressed to a 2-number code (linear SVD demo)",
            ("Sample", "Original 3 values", "Compressed 2-number code"),
            (
                ("Patch 1", "[0.100, 0.200, 0.300]", "[-0.436, -0.253]"),
                ("Patch 2", "[0.600, 0.900, 0.800]", "[ 0.550, -0.123]"),
                ("Patch 3", "[0.800, 0.200, 0.400]", "[-0.114,  0.376]"),
            ),
        )
        out = mini_table(
            "Reconstructed values decoded from the 2-number codes",
            ("Sample", "2-number code", "Decoded 3 values", " Note"),
            (
                ("Patch 1", "[-0.436, -0.253]", "[0.100, 0.200, 0.300]", "3 points span a 2D plane around their mean"),
                ("Patch 2", "[ 0.550, -0.123]", "[0.600, 0.900, 0.800]", "Tiny linear analogue of the thesis autoencoders"),
                ("Patch 3", "[-0.114,  0.376]", "[0.800, 0.200, 0.400]", "See score_reconstructions.py for held-out error"),
            ),
        )
        return inp, out

    if filename == "score_reconstructions.py":
        inp = mini_table(
            "Original vs reconstructed arrays with largest pixel residual highlighted",
            ("Sample ID", "Original array", "Reconstructed array", "Per-value residuals"),
            (
                ("a", "[0.0, 1.0]", "[0.1, 0.9]", "[-0.1, +0.1]"),
                ("b (largest residual)", "[0.2, 0.4]", "[0.4, 0.4]", "[-0.2,  0.0]"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Samples ranked worst-first by mean squared reconstruction error (MSE)",
            ("Rank", "Sample ID", "Mean squared error", "Inspection priority"),
            (
                ("1 (inspect first)", "b", "0.020", "Largest error (residual 0.2 on value 1)"),
                ("2", "a", "0.010", "Smaller uniform residual (0.1 on both values)"),
            ),
            highlight_row=0,
        )
        return inp, out

    if filename == "compare_bottleneck_sizes.py":
        inp = stat_cards(
            (("Training set", "3 patches × 3 values"), ("Held-out test set", "2 patches × 3 values"), ("Candidate widths", "1 vs 2 numbers")),
            note="Both bottleneck widths are fitted on the same training set and scored on the same two held-out test rows.",
        )
        out = mini_table(
            "Held-out reconstruction error vs code storage across bottleneck widths",
            ("Bottleneck width", "Test code bytes (2 samples, float64)", "Held-out MSE", "Trade-off"),
            (
                ("1 number per patch", "16 bytes", "0.00141", "Half the code size, 2.9× higher reconstruction error"),
                ("2 numbers per patch", "32 bytes", "0.00049", "Retains finer detail at double the code size"),
            ),
            highlight_row=1,
        )
        return inp, out

    if filename == "score_variational_reconstruction.py":
        inp = stat_cards(
            (("Image error term (BCE)", "0.387"), ("Raw code KL penalty", "0.083"), ("Applied weight (β)", "0.5")),
            note="Separates pixel reconstruction fidelity from the KL penalty on the latent code distribution.",
        )
        out = mini_table(
            "Variational objective receipt: Total = Reconstruction + β × KL",
            ("Component", "Formula / role", "Value"),
            (
                ("Image reconstruction error", "Binary cross-entropy on target vs decoded pixels", "0.387"),
                ("Code distribution penalty (raw KL)", "Divergence of latent (μ, log σ²) from standard normal", "0.083"),
                ("Weighted penalty (β × KL)", "0.5 × 0.083", "0.042"),
                ("Total variational loss", "0.387 + 0.5 × 0.083", "0.429"),
            ),
            highlight_row=3,
        )
        return inp, out

    # --- Goal: features (Learn features from two views) ---
    if filename == "learn_image_features.py":
        inp = mini_table(
            "Four samples represented by two orthogonal vs two duplicated feature columns",
            ("Arrangement", "Feature column 1", "Feature column 2", "Cross-column correlation"),
            (
                ("Independent features", "[-1, -1, +1, +1]", "[-1, +1, -1, +1]", "0.00 (uncorrelated)"),
                ("Duplicated feature", "[-1, -1, +1, +1]", "[-1, -1, +1, +1]", "1.00 (repeats column 1)"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Barlow Twins loss breakdown (redundancy weight λ = 0.005)",
            ("Feature arrangement", "Agreement loss (on-diagonal)", "Redundancy penalty (λ × off-diagonal²)", "Total loss"),
            (
                ("Independent features", "0.000", "0.000", "0.000"),
                ("Duplicated feature", "0.000", "0.010 (0.005 × 2.0)", "0.010"),
            ),
            highlight_row=1,
            note="Duplicating a column still matches perfectly across views (agreement loss 0.000), but the off-diagonal redundancy penalty raises total loss.",
        )
        return inp, out

    if filename == "prepare_paired_views.py":
        inp = mini_table(
            "Source patch p1 (2 × 2 grayscale pixels, seed = 9)",
            ("Patch ID", "Row 1", "Row 2", "Applied stochastic transforms"),
            (("p1 (original)", "[0.10, 0.50]", "[0.70, 1.00]", "Horizontal flip + brightness gain in [0.85, 1.15]"),),
        )
        out = mini_table(
            "Two altered views retaining shared patch ID p1",
            ("Output view", "Shared ID", "Row 1", "Row 2", "Transformation applied"),
            (
                ("View 1", "p1", "[0.09, 0.47]", "[0.66, 0.94]", "Unflipped · brightness gain ×0.94"),
                ("View 2", "p1", "[0.52, 0.10]", "[1.00, 0.72]", "Flipped horizontally · brightness gain ×1.04 (clipped at 1.0)"),
            ),
        )
        return inp, out

    if filename == "audit_feature_variation.py":
        inp = mini_table(
            "Sample-by-feature matrix (3 patches × 3 feature columns)",
            ("Patch", "Column 0 (varies)", "Column 1 (constant)", "Column 2 (5 × Column 0)"),
            (
                ("Sample 1", "1.0", "0.0", "5.0"),
                ("Sample 2", "2.0", "0.0", "10.0"),
                ("Sample 3", "3.0", "0.0", "15.0"),
            ),
        )
        out = mini_table(
            "Feature audit flags (distinguishing zero variation from redundant overlap)",
            ("Check", "Flagged column(s)", "Measured statistic", "Why inspect before training"),
            (
                ("Zero variation (collapse)", "Column 1", "Std dev = 0.0 (≤ 1e-8)", "Carries no signal across patches."),
                ("Near-duplicate signal", "Columns (0, 2)", "|r| = 1.00 (≥ 0.99)", "Both columns vary, but Column 2 repeats Column 0."),
            ),
        )
        return inp, out

    if filename == "fit_shared_view_encoder.py":
        inp = (
            '<svg viewBox="0 0 300 84" class="lab-diagram" role="img" aria-label="Two altered views passing through one shared 2x2 weight matrix to compute the Barlow Twins objective">'
            '<rect x="12" y="12" width="74" height="26" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="20" y="29" font-size="11" fill="#244035">View 1 (4×2)</text>'
            '<rect x="12" y="46" width="74" height="26" rx="4" fill="#e2e8dc" stroke="#527c67"/>'
            '<text x="20" y="63" font-size="11" fill="#244035">View 2 (4×2)</text>'
            '<line x1="86" y1="25" x2="122" y2="38" stroke="#205841" stroke-width="1.5"/>'
            '<line x1="86" y1="59" x2="122" y2="46" stroke="#205841" stroke-width="1.5"/>'
            '<rect x="122" y="24" width="88" height="36" rx="4" fill="#f9ecb2" stroke="#205841" stroke-width="2"/>'
            '<text x="130" y="46" font-size="11" fill="#1b3126" font-weight="bold">Shared W (2×2)</text>'
            '<line x1="210" y1="42" x2="232" y2="42" stroke="#205841" stroke-width="1.5"/>'
            '<text x="236" y="46" font-size="11" fill="#205841" font-weight="bold">Loss ↓</text>'
            "</svg>"
        )
        out = mini_table(
            "Shared encoder optimization over 40 update steps",
            ("Stage", "Barlow Twins objective", "Shared weight matrix W"),
            (
                ("Step 0 (initial)", "0.1938", "[[1.000, 1.000], [0.150, -0.150]]"),
                ("Step 40 (fitted)", "0.0003", "[[0.520, 0.520], [0.884, -0.884]]"),
            ),
            highlight_row=1,
        )
        return inp, out

    # --- Goal: frozen-features (Extract features with existing models) ---
    if filename == "batch_frozen_features.py":
        inp = mini_table(
            "Three identified patches processed in batches of 2 (weights frozen)",
            ("Batch", "Patch ID", "Input pixels"),
            (("Batch 1", "p1", "[[0.1, 0.4]]"), ("Batch 1", "p2", "[[0.7, 0.9]]"), ("Batch 2", "p3", "[[0.4, 0.2]]")),
        )
        out = mini_table(
            "Extracted feature vectors in original patch ID order",
            ("Patch ID", "Feature 1 (mean)", "Feature 2 (std)", "Fixed during extraction"),
            (
                ("p1", "0.250", "0.150", "Encoder weights & input ID order"),
                ("p2", "0.800", "0.100", "Encoder weights & input ID order"),
                ("p3", "0.300", "0.100", "Encoder weights & input ID order"),
            ),
        )
        return inp, out

    if filename == "compare_encoder_dimensions.py":
        inp = stat_cards(
            (("Fixed sample count", "30 patches"), ("Number format", "float32 (4 bytes / value)")),
            note="Compares in-memory array sizes (not compressed disk files) for two feature widths on the same 30 patches.",
        )
        out = mini_table(
            "Feature array dimensions and raw byte footprint (30 examples, float32)",
            ("Encoder", "Examples", "Feature width", "Number format", "Array size (bytes)"),
            (
                ("small", "30", "16 dimensions", "float32 (4 B)", "1,920 B"),
                ("wide", "30", "64 dimensions", "float32 (4 B)", "7,680 B (4× larger)"),
            ),
        )
        return inp, out

    if filename == "standardise_encoder_inputs.py":
        inp = (
            '<svg viewBox="0 0 260 86" class="lab-diagram" role="img" aria-label="16 by 20 RGB patch resized to 8 by 8 and normalised across 3 channels">'
            '<rect x="16" y="12" width="48" height="60" rx="3" fill="#95bbaf" stroke="#244035"/>'
            '<text x="12" y="82" font-size="10" fill="#244035">Input 16 × 20 RGB</text>'
            '<text x="78" y="45" font-size="12" fill="#205841" font-weight="bold">→ resize &amp; norm →</text>'
            '<rect x="184" y="22" width="36" height="36" rx="3" fill="#95bbaf" stroke="#205841" stroke-width="2"/>'
            '<text x="172" y="72" font-size="10" fill="#244035">Output (3, 8, 8) float32</text>'
            "</svg>"
        )
        out = mini_table(
            "Standardised encoder tensor (channels-first RGB, mean = 0.5, std = 0.25)",
            ("Channel", "Source 8-bit value", "Scaled [0, 1]", "Normalised (x − 0.5) / 0.25", "Output tensor shape"),
            (
                ("R (channel 0)", "149", "0.584", "+0.337", "(3, 8, 8)"),
                ("G (channel 1)", "187", "0.733", "+0.933", "(3, 8, 8)"),
                ("B (channel 2)", "175", "0.686", "+0.745", "(3, 8, 8)"),
            ),
            note="The preview swatch shows the unnormalised RGB colour (#95bbaf); the model receives the signed float32 array.",
        )
        return inp, out

    # --- Goal: feature-benchmarks (Test which features are useful) ---
    if filename == "benchmark_frozen_features.py":
        inp = mini_table(
            "Fixed train/test split across both candidate representations",
            ("Split role", "Sample indices", "Expected labels", "First encoder values", "Second encoder values"),
            (
                ("Train centroids", "Indices 0, 1", "['a', 'b']", "[0.0], [4.0]", "[0.0], [4.0]"),
                ("Held-out test", "Indices 2, 3", "['a', 'b']", "[0.3], [3.7]", "[3.5], [3.7]"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Held-out nearest-centroid accuracy on the shared 2-sample test split",
            ("Representation", "Predictions on test [2, 3]", "Correct / Total", "Held-out accuracy"),
            (
                ("first", "['a', 'b'] vs ['a', 'b']", "2 / 2", "1.00 (100%)"),
                ("second", "['b', 'b'] vs ['a', 'b']", "1 / 2", "0.50 (50%)"),
            ),
            highlight_row=0,
            note="Holding the train/test indices and classifier fixed isolates the difference between the two feature representations.",
        )
        return inp, out

    if filename == "measure_feature_separation.py":
        inp = (
            '<svg viewBox="0 0 290 74" class="lab-diagram" role="img" aria-label="Four 1D points in two groups showing within-group distance 0.5 vs nearest other-group distance 3.25">'
            '<line x1="24" y1="38" x2="266" y2="38" stroke="#9ab0a2" stroke-width="2"/>'
            '<circle cx="40" cy="38" r="6" fill="#205841"/><text x="32" y="24" font-size="10" fill="#205841" font-weight="bold">s0 (0.0)</text>'
            '<circle cx="70" cy="38" r="6" fill="#205841"/><text x="62" y="24" font-size="10" fill="#205841" font-weight="bold">s1 (0.5)</text>'
            '<circle cx="220" cy="38" r="6" fill="#8a5a19"/><text x="208" y="24" font-size="10" fill="#8a5a19" font-weight="bold">s2 (3.5)</text>'
            '<circle cx="250" cy="38" r="6" fill="#8a5a19"/><text x="242" y="24" font-size="10" fill="#8a5a19" font-weight="bold">s3 (4.0)</text>'
            '<text x="36" y="60" font-size="10" fill="#205841">Group g1 (within = 0.5)</text>'
            '<text x="186" y="60" font-size="10" fill="#8a5a19">Group g2 (other mean = 3.25–3.75)</text>'
            "</svg>"
        )
        out = mini_table(
            "Per-sample silhouette scores (one representation split into groups g1 and g2)",
            ("Sample", "Group", "Feature value", "Within-group distance", "Nearest other-group mean", "Silhouette score"),
            (
                ("Sample 0", "g1", "0.0", "0.50", "3.75", "0.87"),
                ("Sample 1", "g1", "0.5", "0.50", "3.25", "0.85"),
                ("Sample 2", "g2", "3.5", "0.50", "3.25", "0.85"),
                ("Sample 3", "g2", "4.0", "0.50", "3.75", "0.87"),
            ),
            note="All four scores come from one feature representation divided into two groups (g1 and g2).",
        )
        return inp, out

    if filename == "project_feature_space.py":
        inp = mini_table(
            "Three 3D feature vectors before PCA projection",
            ("Sample ID", "Feature 1", "Feature 2", "Feature 3"),
            (("Sample 1", "0.10", "0.30", "0.20"), ("Sample 2", "0.20", "0.45", "0.17"), ("Sample 3", "0.75", "0.60", "0.90")),
        )
        out = (
            '<svg viewBox="0 0 280 112" class="lab-diagram" role="img" aria-label="2D PCA scatter plot of three samples with variance explained on each axis">'
            '<rect x="36" y="10" width="224" height="78" rx="4" fill="#f7f4ea" stroke="#9ab0a2"/>'
            '<line x1="36" y1="49" x2="260" y2="49" stroke="#d0d8cd" stroke-dasharray="3 3"/>'
            '<circle cx="74" cy="34" r="5" fill="#205841"/><text x="83" y="37" font-size="10" fill="#205841" font-weight="bold">S1 (-0.359, +0.080)</text>'
            '<circle cx="88" cy="66" r="5" fill="#205841"/><text x="97" y="69" font-size="10" fill="#205841" font-weight="bold">S2 (-0.282, -0.086)</text>'
            '<circle cx="222" cy="48" r="5" fill="#8a5a19"/><text x="150" y="44" font-size="10" fill="#8a5a19" font-weight="bold">S3 (+0.640, +0.007)</text>'
            '<text x="100" y="104" font-size="10" fill="#244035">Axis 1 (97.8% variance) · Axis 2 (2.2% variance)</text>'
            "</svg>"
            '<p class="lab-card-note">Visible separation here reflects the synthetic 3-point input; pair with numerical silhouette scores on held-out data.</p>'
        )
        return inp, out

    if filename == "check_bag_classifier_on_known_signal.py":
        inp = (
            '<svg viewBox="0 0 300 84" class="lab-diagram" role="img" aria-label="Positive bag with 1 planted +5 signal among 12 patches vs negative bag of background noise">'
            '<text x="12" y="22" font-size="11" fill="#244035" font-weight="bold">Positive bag (1 of 12 patches carries +5 signal):</text>'
            + "".join(
                f'<rect x="{12 + i * 22}" y="28" width="18" height="16" rx="2" fill="{"#b3472a" if i == 4 else "#d7ddd2"}"/>'
                for i in range(12)
            )
            + '<text x="12" y="60" font-size="11" fill="#244035" font-weight="bold">Negative bag (all 12 patches N(0, 1) noise):</text>'
            + "".join(
                f'<rect x="{12 + i * 22}" y="66" width="18" height="14" rx="2" fill="#d7ddd2"/>'
                for i in range(12)
            )
            + "</svg>"
        )
        out = mini_table(
            "Bag-level ROC AUC on 64 synthetic bags (32 positive, 32 negative, 12 patches/bag)",
            ("Pooling rule", "How it combines the 12 patch scores", "Area under ROC (AUC)"),
            (
                ("Mean pooling", "Averages all 12 patches (dilutes 1 planted signal with 11 noise patches)", "0.830"),
                ("Maximum pooling", "Takes the strongest single patch in the bag", "0.999"),
            ),
            highlight_row=1,
        )
        return inp, out

    # --- Goal: feature-export (Link feature vectors to the source image) ---
    if filename == "export_feature_vectors.py":
        inp = (
            '<svg viewBox="0 0 260 76" class="lab-diagram" role="img" aria-label="Two adjacent 4x4 patches on an 8x4 grid with their IDs and bounds">'
            '<rect x="16" y="14" width="48" height="48" fill="#e2e8dc" stroke="#205841" stroke-width="2"/>'
            '<text x="20" y="36" font-size="10" fill="#1b3126" font-weight="bold">patch-x0-y0</text>'
            '<text x="20" y="50" font-size="9" fill="#536052">(0, 0, 4, 4)</text>'
            '<rect x="64" y="14" width="48" height="48" fill="#f5f0e2" stroke="#205841" stroke-width="2"/>'
            '<text x="68" y="36" font-size="10" fill="#1b3126" font-weight="bold">patch-x4-y0</text>'
            '<text x="68" y="50" font-size="9" fill="#536052">(4, 0, 8, 4)</text>'
            '<text x="126" y="36" font-size="11" fill="#244035" font-weight="bold">Width = 2 features</text>'
            '<text x="126" y="52" font-size="10" fill="#536052">Coordinates travel with each row</text>'
            "</svg>"
        )
        out = mini_table(
            "Exported feature table (2 regions × 2 features, coordinates preserved)",
            ("region_id", "left", "top", "right", "bottom", "feature_1", "feature_2"),
            (
                ("patch-x0-y0", "0", "0", "4", "4", "0.12", "0.68"),
                ("patch-x4-y0", "4", "0", "8", "4", "0.43", "0.19"),
            ),
        )
        return inp, out

    if filename == "align_features_to_regions.py":
        inp = mini_table(
            "Region coordinates and feature vectors arriving in different orders",
            ("Input table", "Row 1", "Row 2"),
            (
                ("Regions (ordered A, B)", "A → (12, 6)", "B → (80, 5)"),
                ("Vectors (ordered B, A)", "B → (0.1, 0.2)", "A → (0.3, 0.4)"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Joined records aligned by region ID (plus missing-ID safeguard)",
            ("Region ID", "Joined coordinates (x, y)", "Joined vector", "Verification status"),
            (
                ("A (reordered match)", "(12, 6)", "(0.3, 0.4)", "Matched by ID across reordered inputs"),
                ("B", "(80, 5)", "(0.1, 0.2)", "Matched by ID"),
                ("If an ID is absent", "—", "—", "Raises ValueError listing missing vs unknown IDs"),
            ),
            highlight_row=0,
        )
        return inp, out

    if filename == "check_feature_cache.py":
        inp = mini_table(
            "Expected metadata vs cached feature array metadata",
            ("Metadata field", "Expected by experiment", "Stored in cache", "Status"),
            (
                ("Region ID order", "['A', 'B']", "['B', 'A']", "Mismatch (reordered)"),
                ("Encoder name", "encoder-v2", "encoder-v1", "Mismatch (outdated encoder)"),
                ("Array shape (n, width)", "(2, 8)", "(2, 8)", "Passed (2 rows × 8 features)"),
            ),
        )
        out = mini_table(
            "Cache validation report and follow-up action",
            ("Check", "Result", "Required action"),
            (
                ("region IDs or ordering changed", "Flagged", "Re-align rows by ID or regenerate cache in canonical order."),
                ("encoder changed", "Flagged", "Re-extract features with encoder-v2 before training."),
                ("vector shape (2, 8)", "Passed", "Width 8 matches expected dimension."),
            ),
        )
        return inp, out

    # --- Goal: grading-splits (Prepare reference grades and splits) ---
    if filename == "prepare_reference_grades.py":
        inp = mini_table(
            "Individual assessor ratings supplied for two samples",
            ("Sample ID", "Assessor r1", "Assessor r2", "Ratings available"),
            (("a", "1", "2", "2 assessors"), ("b", "— (not rated)", "3", "1 assessor only")),
        )
        out = mini_table(
            "Combined reference grade with rating count and spread preserved",
            ("Sample ID", "Reference (mean)", "Rating count (n)", "Spread (max − min)", "How to read spread = 0"),
            (
                ("a", "1.5", "2", "1", "Two assessors differed by 1 grade level (1 vs 2)."),
                ("b", "3.0", "1", "0", "Zero spread from n=1 means uncorroborated, not two agreeing assessors."),
            ),
            highlight_row=1,
        )
        return inp, out

    if filename == "assign_validation_folds.py":
        inp = mini_table(
            "Four samples in three groups before fold assignment",
            ("Group ID", "Member samples", "Group size"),
            (("g1 (paired samples)", "a, b", "2 samples"), ("g2", "c", "1 sample"), ("g3", "d", "1 sample")),
            highlight_row=0,
        )
        out = mini_table(
            "Balanced 2-fold split keeping group g1 together",
            ("Sample", "Group ID", "Held-out fold", "Role in Fold 0 eval", "Role in Fold 1 eval"),
            (
                ("a", "g1", "Fold 0", "Held-out test", "Training"),
                ("b", "g1", "Fold 0", "Held-out test (kept with a)", "Training (kept with a)"),
                ("c", "g2", "Fold 1", "Training", "Held-out test"),
                ("d", "g3", "Fold 1", "Training", "Held-out test"),
            ),
            highlight_row=1,
            note="Related samples a and b share group g1 and never sit on opposite sides of the train/test split.",
        )
        return inp, out

    # --- Goal: grading-models (Train and compare graders at three scales) ---
    if filename == "train_scale_graders.py":
        inp = mini_table(
            "Shared training/test split across scale-specific feature sets",
            ("Sample", "Split role", "Reference grade", "Patch feature", "Cell feature"),
            (
                ("a", "Train", "1.0", "[0.1]", "[0.3]"),
                ("b", "Train", "2.0", "[0.5]", "[0.6]"),
                ("c", "Held-out test", "3.0", "[0.9]", "[0.7]"),
            ),
            highlight_row=2,
        )
        out = mini_table(
            "Held-out predictions for sample c (2-scale demo of the 3-scale thesis workflow)",
            ("Scale model", "Trained on", "Held-out sample", "Reference grade", "Predicted grade", "Absolute error"),
            (
                ("Patch grader", "a, b", "c", "3.000", "2.167", "0.833"),
                ("Cell grader", "a, b", "c", "3.000", "1.759", "1.241"),
            ),
        )
        return inp, out

    if filename == "save_held_out_grades.py":
        inp = mini_table(
            "Two-fold cross-validation schedule (4 samples, patch scale)",
            ("Evaluation fold", "Training samples (fit model)", "Held-out samples (predict)"),
            (("Fold 0", "b, c", "a, d"), ("Fold 1", "a, d", "b, c")),
        )
        out = mini_table(
            "Saved out-of-fold predictions (every case predicted by a model that did not train on it)",
            ("sample", "scale", "fold", "reference", "prediction", "abs_error"),
            (
                ("a", "patch", "0", "0.0", "1.039", "1.039"),
                ("d", "patch", "0", "3.0", "1.907", "1.093"),
                ("b", "patch", "1", "1.0", "1.071", "0.071"),
                ("c", "patch", "1", "2.0", "2.071", "0.071"),
            ),
        )
        return inp, out

    if filename == "summarise_errors_by_grade.py":
        inp = mini_table(
            "Five held-out predictions grouped by ordinal reference grade",
            ("Reference grade", "Predicted grades in example", "Sample count (n)"),
            (("Grade 0", "0.7, 0.2", "n = 2"), ("Grade 1", "1.2", "n = 1"), ("Grade 3", "2.1, 2.8", "n = 2")),
            highlight_row=2,
        )
        out = mini_table(
            "Signed and absolute error by reference grade (signed = prediction − reference)",
            ("Reference grade", "Count (n)", "Signed error (direction)", "Absolute error (magnitude)"),
            (
                ("Grade 0", "2", "+0.45 (runs high)", "0.45"),
                ("Grade 1", "1", "+0.20 (runs slightly high)", "0.20"),
                ("Grade 3", "2", "−0.55 (under-predicts high grade)", "0.55"),
            ),
            highlight_row=2,
            note="Positive signed error means predictions exceed the reference; negative (−0.55 at Grade 3 across 2 cases) shows under-prediction at the top of the scale.",
        )
        return inp, out

    # --- Goal: compare (Test changes against matched baseline runs) ---
    if filename == "compare_experiments.py":
        inp = mini_table(
            "Matched baseline and compact runs across 2 folds (seed = 7)",
            ("Configuration", "Fold", "Seed", "Error", "Time / epoch (s)", "Peak memory (MiB)"),
            (
                ("baseline", "0", "7", "0.31", "52 s", "92 MiB"),
                ("compact", "0", "7", "0.32", "29 s", "60 MiB"),
                ("baseline", "1", "7", "0.33", "55 s", "91 MiB"),
                ("compact", "1", "7", "0.34", "31 s", "59 MiB"),
            ),
        )
        out = mini_table(
            "Paired percentage change vs baseline (averaged across Folds 0 and 1, seed 7)",
            ("Variant", "Matched pairs", "Error change", "Time / epoch change", "Peak memory change"),
            (("compact vs baseline", "2 folds × 1 seed", "+3.1% (slightly worse)", "−43.9% (faster)", "−35.0% (smaller)"),),
            highlight_row=0,
            note="Time and memory fell substantially while error rose by 3.1% across the two matched folds.",
        )
        return inp, out

    if filename == "plan_matched_runs.py":
        inp = mini_table(
            "Single-setting changes expanded across shared folds (0, 1) and seeds (7, 11)",
            ("Configuration", "pool setting", "batch_size setting", "What changed vs baseline"),
            (
                ("baseline", "mean", "16", "Reference configuration"),
                ("max_pool", "max", "16", "Only pooling rule changed (mean → max)"),
                ("large_batch", "mean", "32", "Only batch size changed (16 → 32)"),
            ),
        )
        out = mini_table(
            "Planned 3 × 2 × 2 = 12 run schedule (highlighting shared fold 0, seed 7 pair)",
            ("Configuration", "Fold 0 · Seed 7", "Fold 0 · Seed 11", "Fold 1 · Seed 7", "Fold 1 · Seed 11"),
            (
                ("baseline", "mean, bs=16 (pair #1)", "mean, bs=16", "mean, bs=16", "mean, bs=16"),
                ("max_pool", "max, bs=16 (pair #1)", "max, bs=16", "max, bs=16", "max, bs=16"),
                ("large_batch", "mean, bs=32 (pair #1)", "mean, bs=32", "mean, bs=32", "mean, bs=32"),
            ),
            highlight_row=1,
        )
        return inp, out

    if filename == "verify_run_configuration.py":
        inp = mini_table(
            "Planned settings vs startup record for seed = 7",
            ("Setting", "Planned value", "Recorded at startup"),
            (
                ("seed", "7", "7 (matches)"),
                ("depth", "2", "1 (wrong value)"),
                ("position_encoding", "True", "Absent from startup log"),
            ),
        )
        out = mini_table(
            "Configuration verification flags before including run in an ablation table",
            ("Setting", "Planned", "Effective", "Recorded?", "Why it undermines a comparison"),
            (
                ("depth", "2", "1", "True", "Ran a shallower model than the experiment plan specified."),
                ("position_encoding", "True", "None", "False", "Startup log never confirmed whether positions were active."),
            ),
        )
        return inp, out

    if filename == "summarise_matched_training_traces.py":
        inp = mini_table(
            "Per-epoch validation traces across 2 matched (fold, seed) pairs (window = epochs 2–3)",
            ("Run pair", "Epoch 1 (excluded warmup)", "Epoch 2 (in window)", "Epoch 3 (in window)"),
            (
                ("baseline · (0, 11) & (1, 11)", "acc 0.745, 22 s", "acc 0.755, 44 s", "acc 0.765, 66 s"),
                ("variant · (0, 11) & (1, 11)", "acc 0.755, 17 s", "acc 0.765, 34 s", "acc 0.775, 51 s"),
            ),
        )
        out = mini_table(
            "Window summary over final epochs 2–3 (2 folds, seed 11)",
            ("Configuration", "Included epochs", "Mean balanced accuracy", "Mean elapsed time at epoch 3"),
            (
                ("baseline", "Epochs 2, 3 (n=2 runs)", "0.760", "66.0 s"),
                ("variant", "Epochs 2, 3 (n=2 runs)", "0.770 (+0.010)", "51.0 s (−15.0 s)"),
            ),
            highlight_row=1,
        )
        return inp, out

    # --- Goal: sampling (Choose which training examples to revisit) ---
    if filename == "weight_grading_examples.py":
        inp = mini_table(
            "Four training samples with class frequency and per-epoch losses",
            ("Sample", "Grade label (frequency)", "Epoch 1 loss", "Epoch 2 loss"),
            (
                ("Sample 1", "Grade 0 (3 in class)", "0.10", "0.20"),
                ("Sample 2", "Grade 0 (3 in class · high loss)", "0.90", "0.60"),
                ("Sample 3", "Grade 0 (3 in class)", "0.10", "0.20"),
                ("Sample 4", "Grade 1 (1 in class · rare grade)", "0.40", "0.30"),
            ),
        )
        out = mini_table(
            "Hybrid sampling probabilities (higher weight = revisited more often during training)",
            ("Sample", "Why weighted", "Initial weight", "Next-epoch weight"),
            (
                ("Sample 1 (Grade 0, low loss)", "Common class, small error", "0.136", "0.157"),
                ("Sample 2 (Grade 0, high loss)", "Boosted by large training loss", "0.322", "0.293"),
                ("Sample 3 (Grade 0, low loss)", "Common class, small error", "0.136", "0.157"),
                ("Sample 4 (Grade 1, rare class)", "Boosted by rare class balance", "0.406", "0.392"),
            ),
            highlight_row=3,
        )
        return inp, out

    if filename == "probe_grading_model_with_noise.py":
        inp = mini_table(
            "Generated signal bags vs independent Gaussian noise probe (12 bags each)",
            ("Input batch", "Bag count", "Distribution (20 instances × 2 features)", "Example bag mean"),
            (
                ("Generated signal", "12 bags", "N(mean = 1.5, std = 0.4)", "+1.50"),
                ("Gaussian noise probe", "12 bags", "N(mean = 0.0, std = 1.0)", "≈ 0.00"),
            ),
        )
        out = mini_table(
            "Outside-input (null class 2) response on generated probe",
            ("Probe batch", "Median null-class probability", "Predicted as outside-input (null calls)", "Interpretation in demo"),
            (
                ("Signal bags", "0.009", "0 / 12 bags", "Assigned to regular grade classes (0 or 1)"),
                ("Gaussian noise bags", "0.683", "12 / 12 bags", "Flagged by the dedicated outside-input class"),
            ),
            highlight_row=1,
            note="Synthetic probe illustrating Appendix A.4's null-class structure.",
        )
        return inp, out

    # --- Goal: agreement (Compare model error with assessor disagreement) ---
    if filename == "compare_assessor_errors.py":
        inp = mini_table(
            "Two matched samples with two assessor grades and one model prediction",
            ("Sample", "Assessor A", "Assessor B", "Assessor mean (reference)", "Model prediction"),
            (
                ("a", "1.0", "2.0", "1.50", "1.40"),
                ("b", "2.0", "2.0", "2.00", "1.80"),
            ),
        )
        out = mini_table(
            "Two distinct error definitions on the same 2 matched samples",
            ("Metric", "What it compares", "Sample a", "Sample b", "Mean (MAE)"),
            (
                ("Assessor-to-assessor gap", "|Assessor A − Assessor B| (between people)", "1.00", "0.00", "0.50 grade pts"),
                ("Model-to-consensus MAE", "|Prediction − Mean(A, B)| (against average)", "0.10", "0.20", "0.15 grade pts"),
            ),
            note="The two numbers have different targets: 0.50 compares one person with another, while 0.15 compares the model with their average.",
        )
        return inp, out

    if filename == "score_ordinal_agreement.py":
        inp = mini_table(
            "Four aligned ordinal grade pairs across levels [0, 1, 2, 3]",
            ("Pair", "First rating", "Second rating", "Ordinal distance |a − b|", "Quadratic penalty (a − b)²"),
            (
                ("Case 1", "0", "0", "0 (exact match)", "0"),
                ("Case 2", "1", "2", "1 (one-level miss)", "1"),
                ("Case 3", "2", "2", "0 (exact match)", "0"),
                ("Case 4", "3", "3", "0 (exact match)", "0"),
            ),
            highlight_row=1,
        )
        out = stat_cards(
            (("Quadratic weighted κ", "0.90"), ("Exact matches", "3 of 4 pairs"), ("One-grade miss", "1 of 4 pairs (1 vs 2)")),
            note="Quadratic weighting penalises a 2- or 3-grade jump by 4× or 9× a 1-grade miss, adjusted for chance agreement.",
        )
        return inp, out

    # --- Goal: subtype-cohort (Prepare the subtype dataset) ---
    if filename == "join_subtype_labels.py":
        inp = mini_table(
            "Three image records matched against the supplied reference table",
            ("Image ID", "Reference ID", "Value in reference table"),
            (("a", "R1", "'ABC'"), ("b", "R2", "'unclassified'"), ("c", "R3", "None (absent)")),
        )
        out = mini_table(
            "Label join outcome (distinguishing unrecognised values from missing rows)",
            ("Image ID", "Reference ID", "Supplied status", "Outcome"),
            (
                ("a", "R1", "ABC (allowed)", "Kept for eligibility check →"),
                ("b", "R2", "unrecognised ('unclassified')", "Held for review (not in {'ABC', 'GCB'})"),
                ("c", "R3", "missing (no entry for R3)", "Held for review (never inferred)"),
            ),
            highlight_row=0,
        )
        return inp, out

    if filename == "audit_cohort_filters.py":
        inp = mini_table(
            "Eligibility criteria checked for each specimen (required stain = stain-a, min patches = 8)",
            ("Specimen", "Target label in {ABC, GCB}?", "Has stain-a?", "Retained patches ≥ 8?"),
            (
                ("Specimen a", "✓ Pass (ABC)", "✓ Pass ({stain-a})", "✓ Pass (12 patches)"),
                ("Specimen b", "✕ Fail (None)", "✕ Fail (empty set)", "✕ Fail (4 patches)"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Cohort filter audit result (1 of 2 specimens retained)",
            ("Specimen", "Decision", "Recorded exclusion reasons"),
            (
                ("Specimen a", "Retained (1 remaining)", "All 3 eligibility criteria passed"),
                ("Specimen b", "Excluded", "target unavailable · required stain unavailable · not enough retained patches"),
            ),
            highlight_row=0,
        )
        return inp, out

    # --- Goal: interpret (How do many patches give one case prediction?) ---
    if filename == "pool_patch_evidence.py":
        inp = mini_table(
            "Three patch feature vectors and attention logits for one specimen",
            ("Patch", "Feature 1", "Feature 2", "Attention logit → softmax weight"),
            (
                ("Patch 1", "0.100", "0.900 (max F2)", "0 → weight 0.212"),
                ("Patch 2", "0.300", "0.700", "0 → weight 0.212"),
                ("Patch 3", "0.900 (max F1)", "0.200", "1 → weight 0.576"),
            ),
        )
        out = mini_table(
            "Comparison of three pooling rules on the same 3 patches",
            ("Pooling method", "Pooled Feature 1", "Pooled Feature 2", "How Feature 1 was formed"),
            (
                ("mean", "0.433", "0.600", "(0.1 + 0.3 + 0.9) / 3 = 0.433"),
                ("maximum", "0.900", "0.900", "max(0.1, 0.3, 0.9) = 0.900 from Patch 3"),
                ("attention", "0.603", "0.454", "0.212×0.1 + 0.212×0.3 + 0.576×0.9 = 0.603"),
            ),
        )
        return inp, out

    if filename == "batch_variable_patch_sets.py":
        inp = (
            '<svg viewBox="0 0 300 94" class="lab-diagram" role="img" aria-label="Four specimens sorted by patch count into two batches with padded slots marked">'
            '<text x="12" y="18" font-size="11" fill="#244035" font-weight="bold">Batch 1 (max 5): b (3) + 2 pad, c (5)</text>'
            '<rect x="12" y="24" width="54" height="12" rx="2" fill="#527c67"/>'
            '<rect x="68" y="24" width="36" height="12" rx="2" fill="#e2e8dc" stroke="#b3472a" stroke-dasharray="2 2"/>'
            '<rect x="12" y="40" width="92" height="12" rx="2" fill="#527c67"/>'
            '<text x="12" y="68" font-size="11" fill="#244035" font-weight="bold">Batch 2 (max 15): a (12) + 3 pad, d (15)</text>'
            '<rect x="12" y="74" width="160" height="12" rx="2" fill="#527c67"/>'
            '<rect x="174" y="74" width="40" height="12" rx="2" fill="#e2e8dc" stroke="#b3472a" stroke-dasharray="2 2"/>'
            "</svg>"
        )
        out = mini_table(
            "Size-sorted batches (batch_size = 2) and masked padding counts",
            ("Batch", "Grouped specimens (patch counts)", "Batch width", "Padded dummy slots", "Mask role"),
            (
                ("Batch 1", "b (3 patches), c (5 patches)", "5 slots", "2 padded slots", "Validity mask zeroes out the 2 dummy slots"),
                ("Batch 2", "a (12 patches), d (15 patches)", "15 slots", "3 padded slots", "Validity mask zeroes out the 3 dummy slots"),
            ),
            note="Sorting by count before batching keeps total padding to 5 slots (vs 21 slots if b=3 and d=15 were paired).",
        )
        return inp, out

    if filename == "predict_subtypes_from_bags.py":
        inp = mini_table(
            "Two labelled training bags and one held-out test bag",
            ("Bag ID", "Split role", "Supplied label", "Patch values", "Bag mean centroid"),
            (
                ("a", "Training", "ABC", "[[0.1], [0.2]]", "0.15"),
                ("b", "Training", "GCB", "[[0.9], [0.8]]", "0.85"),
                ("c", "Held-out test", "To predict", "[[0.6], [0.7], [0.8]]", "0.70"),
            ),
            highlight_row=2,
        )
        out = mini_table(
            "Held-out score for bag c (score = distance_to_GCB − distance_to_ABC)",
            ("Held-out bag", "Distance to ABC (0.15)", "Distance to GCB (0.85)", "Signed score", "Threshold = 0 call"),
            (("c (mean 0.70)", "0.55", "0.15", "−0.400", "< 0 (closer to GCB centroid)"),),
        )
        return inp, out

    # --- Goal: subtype-ablations (Test spatial positions and model hierarchy) ---
    if filename == "compare_spatial_attention.py":
        inp = mini_table(
            "Single-change ablation: identical query, keys and values with 2D rotary positions off vs on",
            ("Patch index", "Valid?", "Position (x, y)", "Key vector", "Value"),
            (
                ("Patch 0", "True (valid)", "(0, 0)", "[1, 0, 1, 0]", "0.200"),
                ("Patch 1", "True (valid)", "(2, 1)", "[1, 0, 1, 0]", "0.800"),
                ("Patch 2", "False (padded)", "(3, 1)", "[10, 10, 10, 10]", "100.0 (ignored by mask)"),
            ),
        )
        out = mini_table(
            "Pooled attention output with 2D rotary position encoding off vs on",
            ("Setting", "Attention weights on valid patches [0, 1]", "Pooled score", "Why it changed"),
            (
                ("Positions False", "[0.500, 0.500] (equal keys)", "0.500", "Identical unrotated keys weight 0.2 and 0.8 equally."),
                ("Positions True", "[0.719, 0.281] (rotated by x, y)", "0.369", "Rotating Patch 1 at (2, 1) reduces its alignment with query."),
            ),
            note="In the thesis comparison (Ch. 4, §4.6.3), adding 2D positions gave no clear subtype advantage at patch scale.",
        )
        return inp, out

    if filename == "compare_flat_and_hierarchical_pooling.py":
        inp = (
            '<svg viewBox="0 0 300 86" class="lab-diagram" role="img" aria-label="4 valid cells nested inside 2 valid patches and 1 empty patch">'
            '<rect x="12" y="14" width="96" height="58" rx="4" fill="#e2e8dc" stroke="#205841"/>'
            '<text x="18" y="29" font-size="10" fill="#1b3126" font-weight="bold">Patch 1 (3 cells)</text>'
            '<text x="18" y="48" font-size="11" fill="#244035">[0], [0], [0]</text>'
            '<text x="18" y="64" font-size="10" fill="#536052">Patch mean = 0.00</text>'
            '<rect x="116" y="14" width="92" height="58" rx="4" fill="#e2e8dc" stroke="#205841"/>'
            '<text x="122" y="29" font-size="10" fill="#1b3126" font-weight="bold">Patch 2 (1 cell)</text>'
            '<text x="122" y="48" font-size="11" fill="#244035">[1], <tspan fill="#999">pad, pad</tspan></text>'
            '<text x="122" y="64" font-size="10" fill="#536052">Patch mean = 1.00</text>'
            '<rect x="216" y="14" width="74" height="58" rx="4" fill="#f0eee6" stroke="#9ab0a2" stroke-dasharray="3 3"/>'
            '<text x="222" y="29" font-size="10" fill="#536052">Patch 3 (empty)</text>'
            '<text x="222" y="52" font-size="10" fill="#b3472a">Excluded</text>'
            "</svg>"
        )
        out = mini_table(
            "Flat cell pooling vs hierarchical patch-then-core pooling",
            ("Pooling order", "Calculation on the 4 valid cells", "Result", "What gets equal weight"),
            (
                ("Flat pooling", "(0 + 0 + 0 + 1) / 4 valid cells", "0.25", "Every cell gets 1/4 vote (Patch 1 has 3× the weight of Patch 2)."),
                ("Hierarchical pooling", "(mean(0,0,0) + mean(1)) / 2 valid patches", "0.50", "Every valid patch gets 1/2 vote; padded slots (999) are masked out."),
            ),
        )
        return inp, out

    # --- Goal: validation (Check performance across folds) ---
    if filename == "summarise_validation.py":
        inp = mini_table(
            "Independent example predictions across 2 folds (2 cases per fold per task)",
            ("Task", "Fold 0 cases (ref → pred)", "Fold 1 cases (ref → pred)"),
            (
                ("Grading (continuous score)", "n=2: (2 → 2.4), (1 → 0.9)", "n=2: (3 → 2.6), (1 → 1.2)"),
                ("Subtyping (class label)", "n=2: (A → A), (B → B)", "n=2: (A → B), (B → B)"),
            ),
        )
        out = (
            mini_table(
                "Grading validation summary (unit: grade-point mean absolute error, lower is better)",
                ("Validation fold", "Cases (n)", "Individual errors", "Mean absolute error (MAE)"),
                (("Fold 0", "2", "0.40, 0.10", "0.25 grade pts"), ("Fold 1", "2", "0.40, 0.20", "0.30 grade pts")),
            )
            + mini_table(
                "Subtyping validation summary (unit: classification accuracy, higher is better)",
                ("Validation fold", "Cases (n)", "Correct / Total", "Fold accuracy"),
                (("Fold 0", "2", "2 / 2", "100%"), ("Fold 1", "2", "1 / 2", "50%")),
                highlight_row=1,
                note="Reporting each fold separately reveals the weaker 50% fold that a pooled 75% average would hide.",
            )
        )
        return inp, out

    if filename == "evaluate_subtype_roc.py":
        inp = mini_table(
            "Four held-out subtype scores ranked highest-first (including tied score at 0.60)",
            ("Rank", "Reference label", "Predicted ABC score", "Note"),
            (
                ("1", "ABC (positive)", "0.90", "Highest score"),
                ("2–3 (tie)", "GCB (negative)", "0.60", "Tied with rank 2–3 positive"),
                ("2–3 (tie)", "ABC (positive)", "0.60", "Evaluated together with tied negative"),
                ("4", "GCB (negative)", "0.20", "Lowest score"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "ROC curve operating points as threshold moves (AUC = 0.875)",
            ("Score threshold", "True positive rate (ABC recall)", "False positive rate (GCB false alarms)", "What changed"),
            (
                ("> 0.90", "0.0 (0/2)", "0.0 (0/2)", "No cases called positive"),
                ("≥ 0.90", "0.5 (1/2)", "0.0 (0/2)", "Top ABC case detected with 0 false alarms"),
                ("≥ 0.60 (tie)", "1.0 (2/2)", "0.5 (1/2)", "Both tied 0.60 cases enter together (+1 TP, +1 FP)"),
                ("≥ 0.20", "1.0 (2/2)", "1.0 (2/2)", "All 4 cases called positive"),
            ),
            highlight_row=2,
        )
        return inp, out

    if filename == "compare_fold_class_recall.py":
        inp = mini_table(
            "Subtype predictions across 2 folds (1 ABC and 1 GCB example per fold)",
            ("Fold", "ABC case (ref → pred)", "GCB case (ref → pred)"),
            (("Fold 0", "ABC → ABC (correct)", "GCB → ABC (missed)"), ("Fold 1", "ABC → GCB (missed)", "GCB → GCB (correct)")),
        )
        out = mini_table(
            "Class recall by fold with explicit numerator / denominator counts",
            ("Validation fold", "Subtype class", "Correct / Total (n)", "Class recall"),
            (
                ("Fold 0", "ABC", "1 / 1", "1.00 (100%)"),
                ("Fold 0", "GCB", "0 / 1", "0.00 (0%)"),
                ("Fold 1", "ABC", "0 / 1", "0.00 (0%)"),
                ("Fold 1", "GCB", "1 / 1", "1.00 (100%)"),
            ),
            note="Showing 1/1 and 0/1 beside each proportion makes clear that each cell in this toy example rests on a single case.",
        )
        return inp, out

    # --- Goal: cost (Compare accuracy, runtime and memory) ---
    if filename == "estimate_representation_cost.py":
        inp = stat_cards(
            (("Regions", "500 patches"), ("Patch dimensions", "224 × 224 × 3 uint8"), ("Feature vector", "256 × float32 (4 B)")),
            note="Raw uncompressed byte calculation: 224 × 224 × 3 = 150,528 B vs 256 × 4 = 1,024 B per region.",
        )
        out = mini_table(
            "Estimated raw storage for 500 regions (uncompressed bytes, excluding container overhead)",
            ("Representation", "Number format", "Bytes per region", "Total for 500 regions", "Relative footprint"),
            (
                ("RGB patches (224 × 224 × 3)", "uint8 (1 B / channel)", "150,528 B", "75,264,000 B (75.26 MB)", "100% (baseline)"),
                ("Feature vectors (256 values)", "float32 (4 B / value)", "1,024 B", "512,000 B (0.51 MB)", "0.68% (147× smaller)"),
            ),
            highlight_row=1,
        )
        return inp, out

    if filename == "rank_accuracy_compute_tradeoffs.py":
        inp = mini_table(
            "Three candidate models measured on accuracy, runtime and peak memory",
            ("Candidate", "Held-out accuracy (↑)", "Runtime per epoch (↓)", "Peak memory (↓)"),
            (
                ("wide", "0.93", "40 s", "900 MiB"),
                ("small", "0.91", "21 s", "600 MiB"),
                ("slow", "0.90", "53 s", "950 MiB"),
            ),
            highlight_row=2,
        )
        out = mini_table(
            "Pareto frontier selection (surviving vs dominated candidates)",
            ("Candidate", "Frontier status", "Reason"),
            (
                ("wide", "Keep (on frontier)", "Highest accuracy (0.93) among all candidates."),
                ("small", "Keep (on frontier)", "Fastest (21 s) and lowest memory (600 MiB)."),
                ("slow", "Drop (dominated)", "Beaten on all three criteria by both wide and small."),
            ),
            highlight_row=2,
        )
        return inp, out

    if filename == "audit_compute_measurements.py":
        inp = mini_table(
            "Expected (model, fold) run list vs recorded resource logs",
            ("Expected run", "seconds_per_epoch", "peak_memory_mib"),
            (
                ("('baseline', 0)", "10.4 s", "Missing (None)"),
                ("('compact', 0)", "No run record found", "No run record found"),
            ),
        )
        out = mini_table(
            "Resource audit report distinguishing partial logs from absent runs",
            ("Expected run", "Audit status", "Follow-up action"),
            (
                ("('baseline', 0)", "missing or invalid peak_memory_mib", "Run exists (10.4 s recorded), but memory profiling was not logged."),
                ("('compact', 0)", "run missing", "No record for compact fold 0; check job schedule or incomplete runs."),
            ),
        )
        return inp, out

    # --- Goal: heatmaps (Map scores back onto the image) ---
    if filename == "map_patch_scores.py":
        inp = (
            '<svg viewBox="0 0 260 92" class="lab-diagram" role="img" aria-label="4 by 3 grid with two overlapping scored rectangles">'
            '<rect x="16" y="12" width="120" height="72" fill="#f0eee6" stroke="#9ab0a2"/>'
            '<rect x="16" y="12" width="90" height="48" fill="#527c67" fill-opacity="0.28" stroke="#205841" stroke-width="2"/>'
            '<rect x="76" y="36" width="60" height="48" fill="#b3472a" fill-opacity="0.28" stroke="#b3472a" stroke-width="2"/>'
            '<text x="20" y="28" font-size="10" fill="#1b3126" font-weight="bold">Patch 1: (0,0)–(3,2) = 0.4</text>'
            '<text x="52" y="78" font-size="10" fill="#b3472a" font-weight="bold">Patch 2: (2,1)–(4,3) = 0.8</text>'
            '<text x="148" y="38" font-size="10" fill="#244035">Overlap at (x=2, y=1):</text>'
            '<text x="148" y="54" font-size="10" fill="#205841" font-weight="bold">(0.4 + 0.8) / 2 = 0.6</text>'
            "</svg>"
        )
        out = mini_table(
            "4 × 3 score grid (overlapping cell averaged to 0.6; uncovered cells marked unscored)",
            ("Grid row", "x = 0", "x = 1", "x = 2", "x = 3"),
            (
                ("y = 0", "0.40", "0.40", "0.40", "Unscored (NaN)"),
                ("y = 1", "0.40", "0.40", "0.60 (overlap)", "0.80"),
                ("y = 2", "Unscored (NaN)", "Unscored (NaN)", "0.80", "0.80"),
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
            + mini_table(
                "Shared colour scale legend",
                ("Region state", "Score value", "Display treatment"),
                (
                    ("Lower-score patch", "0.30", "Warm yellow-orange tint"),
                    ("Overlapping region", "0.55 (mean)", "Intermediate orange-red tint"),
                    ("Higher-score patch", "0.80", "Deeper red tint"),
                    ("Outside scored patches", "No score (NaN)", "Transparent / hatched (never shown as zero)"),
                ),
            )
        )
        return inp, out

    if filename == "summarise_overlay_coverage.py":
        inp = mini_table(
            "2 × 2 score grid with 3 reference points in the region of interest",
            ("Grid position", "In reference region?", "Available score"),
            (
                ("(row 0, col 0)", "Yes (Point 1)", "0.40"),
                ("(row 0, col 1)", "Yes (Point 2)", "Unscored (NaN)"),
                ("(row 1, col 0)", "Yes (Point 3)", "0.80"),
                ("(row 1, col 1)", "No (outside ROI)", "0.50 (ignored)"),
            ),
            highlight_row=1,
        )
        out = stat_cards(
            (("ROI coverage", "2 of 3 points (66.7%)"), ("Median of scored", "0.60"), ("Scored range", "0.40 to 0.80"), ("Unscored in ROI", "1 point (NaN)")),
            note="Summary statistics use the 2 scored points while explicitly reporting that 1 of the 3 ROI points had no score.",
        )
        return inp, out

    # --- Goal: explain (Test what happens when regions are dimmed) ---
    if filename == "explain_prediction.py":
        inp = mini_table(
            "Four input regions scored by a fixed two-class linear model",
            ("Input / Weight", "Region 1", "Region 2", "Region 3", "Region 4"),
            (
                ("Region value", "0.80", "0.60", "0.90", "0.40"),
                ("Class A weights", "+1.0", "−1.0", "+0.4", "−0.8"),
                ("Class B weights", "−0.4", "+1.0", "−0.7", "+0.9"),
            ),
        )
        out = mini_table(
            "Fitted class-specific brightness masks (1.00 = kept, 0.00 = dimmed)",
            ("Target class", "Baseline score", "Masked score", "Region 1", "Region 2", "Region 3", "Region 4"),
            (
                ("Class A mask", "0.24", "1.16 (+0.92)", "1.00 (kept)", "0.00 (dimmed)", "1.00 (kept)", "0.00 (dimmed)"),
                ("Class B mask", "0.01", "0.96 (+0.95)", "0.00 (dimmed)", "1.00 (kept)", "0.00 (dimmed)", "1.00 (kept)"),
            ),
            note="The two masks keep opposite regions to raise their respective class scores; compare against a uniform dimming control in test_mask_score_changes.py.",
        )
        return inp, out

    if filename == "model_explanations.md":
        inp = (
            '<div class="lab-route-card"><p class="lab-card-note"><strong>Question to ask of any highlighted region:</strong> '
            "Does dimming this region change the model score more than dimming the whole image by the same average amount—and does that sensitivity reflect biology, staining, or a cohort artefact?</p></div>"
        )
        out = mini_table(
            "What model masks establish vs what requires separate validation",
            ("Question", "What the mask / perturbation shows", "What additional evidence is required"),
            (
                ("Model sensitivity", "Which regions raise or lower a specific class score when dimmed or removed.", "Compare against a uniform-dimming control at the same mean brightness."),
                ("Biological meaning", "Highlights image regions the fitted network relied on in this cohort.", "Expert review, repeatable signal across cohorts, and orthogonal biological assays."),
            ),
        )
        return inp, out

    if filename == "test_mask_score_changes.py":
        inp = mini_table(
            "Targeted explanation mask vs uniform control (both have mean brightness = 0.80)",
            ("Mask type", "Top-left (w=0.8)", "Top-right (w=0.1)", "Bottom-left (w=0.1)", "Bottom-right (w=0.0)", "Mean brightness"),
            (
                ("Input image", "0.90", "0.50", "0.50", "0.20", "—"),
                ("Targeted spatial mask", "0.20 (dimmed)", "1.00", "1.00", "1.00", "0.80"),
                ("Uniform control mask", "0.80", "0.80", "0.80", "0.80", "0.80"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Score change against baseline (0.820) in one generated test",
            ("Condition", "Mean mask brightness", "Model score", "Change from baseline (Δ)"),
            (
                ("Unmasked baseline", "1.00", "0.820", "0.000"),
                ("Uniform dimming control", "0.80", "0.656", "−0.164"),
                ("Targeted spatial mask", "0.80", "0.244", "−0.576 (3.5× larger drop)"),
            ),
            highlight_row=2,
        )
        return inp, out

    if filename == "compare_patch_perturbations.py":
        inp = mini_table(
            "Three-patch bag scored by mean pooling (baseline scores: Class 0 = 0.367, Class 1 = 0.533)",
            ("Patch ID", "Class 0 feature", "Class 1 feature", "Dominant signal"),
            (
                ("Patch 0", "0.100", "0.900", "Strong Class 1"),
                ("Patch 1", "0.200", "0.600", "Moderate Class 1"),
                ("Patch 2", "0.800", "0.100", "Strong Class 0"),
            ),
        )
        out = mini_table(
            "Score changes (Δ vs baseline) when removing one patch vs repeating only that patch",
            ("Patch ID", "Remove patch Δ (Class 0, Class 1)", "Repeat-only patch Δ (Class 0, Class 1)", "Interpretation"),
            (
                ("Patch 0", "[+0.133, −0.183]", "[−0.267, +0.367]", "Removing Patch 0 drops Class 1; repeating it boosts Class 1."),
                ("Patch 1", "[+0.083, −0.033]", "[−0.167, +0.067]", "Small effect in the same Class 1 direction."),
                ("Patch 2", "[−0.217, +0.217]", "[+0.433, −0.433]", "Removing Patch 2 drops Class 0; repeating it boosts Class 0."),
            ),
            note="Positive Δ means the class score rose; negative Δ means the class score fell relative to the unperturbed 3-patch bag.",
        )
        return inp, out

    # --- Goal: cluster-runs (Plan and resume experiment jobs) ---
    if filename == "build_cluster_run_manifest.py":
        inp = stat_cards(
            (("Configurations", "2 (baseline, max_pool)"), ("Validation folds", "2 (Fold 0, Fold 1)"), ("Random seeds", "2 (Seed 7, Seed 11)")),
            note="2 configurations × 2 folds × 2 seeds = 8 deterministic jobs.",
        )
        out = mini_table(
            "Expanded 8-job manifest with deterministic SHA-256 run IDs",
            ("Job #", "run_id (16-hex SHA-256)", "configuration", "fold", "seed", "pool", "batch_size"),
            (
                ("1", "55b2ba45f220d664", "baseline", "0", "7", "mean", "16"),
                ("2", "9616e1407eb20cf1", "baseline", "0", "11", "mean", "16"),
                ("3–4", "23ef391e… / 055a5ebb…", "baseline", "1", "7, 11", "mean", "16"),
                ("5", "04a29607846ac864", "max_pool", "0", "7", "max", "16"),
                ("6–8", "f2c8f509… / 59549bad… / 71b73014…", "max_pool", "0, 1", "11, 7, 11", "max", "16"),
            ),
            highlight_row=0,
        )
        return inp, out

    if filename == "resume_chunked_experiment.py":
        inp = (
            '<svg viewBox="0 0 300 76" class="lab-diagram" role="img" aria-label="Three-step strip showing Chunk 1 committed, Chunk 2 interrupted, and resumption from Chunk 2">'
            '<rect x="10" y="14" width="84" height="46" rx="4" fill="#e2e8dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="16" y="32" font-size="10" fill="#1b3126" font-weight="bold">1. Chunk 2 → 4</text>'
            '<text x="16" y="48" font-size="9" fill="#205841">Committed to disk</text>'
            '<rect x="106" y="14" width="84" height="46" rx="4" fill="#f9ecb2" stroke="#b3472a" stroke-width="1.5"/>'
            '<text x="112" y="32" font-size="10" fill="#b3472a" font-weight="bold">2. Chunk 3 fails</text>'
            '<text x="112" y="48" font-size="9" fill="#536052">Uncommitted work dropped</text>'
            '<rect x="202" y="14" width="88" height="46" rx="4" fill="#e2e8dc" stroke="#205841" stroke-width="1.5"/>'
            '<text x="208" y="32" font-size="10" fill="#1b3126" font-weight="bold">3. Resume</text>'
            '<text x="208" y="48" font-size="9" fill="#205841">Reuses [4], runs 3, 4</text>'
            "</svg>"
        )
        out = mini_table(
            "Chunk execution state across interruption and retry (plan = [2, 3, 4])",
            ("Chunk input", "First attempt", "Saved in checkpoint.json", "Retry action", "Final result"),
            (
                ("Chunk 1 (x = 2)", "Computed 4", "Committed ([4])", "Reused from disk (skipped)", "4"),
                ("Chunk 2 (x = 3)", "InterruptedError", "Not committed", "Recomputed on resume", "9"),
                ("Chunk 3 (x = 4)", "Not reached", "Not committed", "Computed on resume", "16"),
            ),
            highlight_row=0,
        )
        return inp, out

    # --- Goal: run-results (Collect and check completed runs) ---
    if filename == "collect_fold_results.py":
        inp = mini_table(
            "Input result stream keyed by (configuration, fold, seed)",
            ("Source CSV", "configuration", "fold", "seed", "metric"),
            (("Stream 1", "baseline", "0", "11", "0.28"),),
        )
        out = mini_table(
            "Collected metrics table (with duplicate-key safeguard)",
            ("Key (configuration, fold, seed)", "Collected metric", "Duplicate-key rule"),
            (
                ("('baseline', 0, 11)", "0.28", "Accepted (unique key)"),
                ("Repeated ('baseline', 0, 11)", "Rejected", "Raises ValueError('Duplicate result') before aggregation"),
            ),
        )
        return inp, out

    if filename == "find_incomplete_runs.py":
        inp = mini_table(
            "Planned 3-run schedule vs observed completion states",
            ("Planned job (config, fold, seed)", "Observed status in storage"),
            (
                ("('baseline', 0, 7)", "completed"),
                ("('compact', 0, 7)", "missing metrics (started, no final score)"),
                ("('compact', 1, 7)", "Not in status table"),
            ),
        )
        out = mini_table(
            "Incomplete runs flagged before building comparison tables",
            ("Run key", "Flagged state", "Follow-up action"),
            (
                ("('compact', 0, 7)", "missing metrics", "Inspect job log/checkpoint; run started but failed before saving metrics."),
                ("('compact', 1, 7)", "missing (no run record)", "Submit job from build_cluster_run_manifest.py schedule."),
            ),
        )
        return inp, out

    # --- Goal: figures (Rebuild tables and figures from saved results) ---
    if filename == "build_grading_table.py":
        inp = mini_table(
            "Matched held-out predictions for sample a across two scales (fold 0)",
            ("sample", "scale", "fold", "reference (grade pts)", "prediction (grade pts)", "|prediction − reference|"),
            (
                ("a", "core", "0", "2.0", "1.6", "0.400"),
                ("a", "patch", "0", "2.0", "2.2", "0.200"),
            ),
        )
        out = mini_table(
            "Scale comparison summary (1 matched sample, unit: grade points)",
            ("Image scale", "Matched samples (n)", "Mean absolute error (grade points)"),
            (
                ("core", "1", "0.400"),
                ("patch", "1", "0.200"),
            ),
            highlight_row=1,
            note="Single-sample illustration; see run_grading_example.py for the 12-case × 3-scale synthetic rerun.",
        )
        return inp, out

    if filename == "render_grading_figure.py":
        inp = mini_table(
            "Built-in 3-scale summary passed to the SVG figure renderer",
            ("Scale", "Sample count (n)", "Mean absolute error (grade points)"),
            (
                ("Core", "n = 6", "0.350"),
                ("Patch", "n = 6", "0.240 (lowest error)"),
                ("Cell", "n = 6", "0.320"),
            ),
            highlight_row=1,
            note="A grade point is one step on the 0–3 ordinal staining scale; a shorter bar means predictions stayed closer to the reference grade. This summary chart shows point estimates without intervals.",
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
            stat_cards((("Case", case["Case"]), ("Held-out fold", case["Validation fold"]),
                        ("Assessor A", case["Assessor A"]), ("Assessor B", case["Assessor B"]),
                        ("Mean reference", "2.500")),
                       note="Trace line: Ratings (2, 3) → Reference 2.500 → Held-out Fold 1 prediction → Scale MAE bar in grading_figure.svg.")
        )
        out = (
            f'<label class="lab-scale-picker">Image scale <select data-image-scale>{selector}</select></label>'
            f'<div aria-live="polite">{panels}</div>'
            '<p class="lab-card-note">Case S02 is one of 12 synthetic cases (36 predictions across 3 scales) that feed the aggregate chart below.</p>'
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
            label = f"{low}+ patches" if high == "None" else f"{low} to {int(high) - 1} patches"
            rule = f"≥ {low}" if high == "None" else f"{low} ≤ count < {high}"
            items.append((label, count, f"{count} cores"))
            table_rows.append((label, rule, examples_by_bin[idx], str(count)))
        inp = mini_table(
            "Seven per-core patch counts and half-open bin rules [lower, upper)",
            ("Range label", "Boundary rule", "Source counts in bin", "Core count"),
            table_rows,
            note="Boundaries are lower-inclusive and upper-exclusive: a core with exactly 50 patches belongs in 50–99, not 0–49.",
        )
        out = metric_bars("Number of cores in each patch-count range", items, max_value=highest)
        return inp, out

    if filename == "grading_figure.svg":
        inp = mini_table(
            "Scale summaries feeding grading_figure.svg (from 36 synthetic held-out predictions)",
            ("Image scale", "Held-out cases (n)", "Mean absolute error (grade points)"),
            (
                ("Core", "12", "0.464"),
                ("Patch", "12", "0.216 (lowest error in synthetic rerun)"),
                ("Cell", "12", "0.371"),
            ),
            highlight_row=1,
            note="Generated by run_grading_example.py and rendered by render_grading_figure.py.",
        )
        return inp, ""

    if filename == "verify_report_assets.py":
        inp = mini_table(
            "Expected report assets checked against the generated report directory",
            ("Asset filename", "Role in report", "Present on disk?"),
            (
                ("scores.csv", "Model score summary table (27 bytes)", "✓ Found"),
                ("figure.pdf", "Rendered publication figure", "✕ Missing"),
            ),
            highlight_row=1,
        )
        out = mini_table(
            "Asset verification and SHA-256 fingerprint table",
            ("Asset", "Status", "Size", "SHA-256 prefix (verifies exact file identity)"),
            (
                ("scores.csv", "Verified", "27 B", "cf1e81825e6bf460… (full 64-char hash in raw output)"),
                ("figure.pdf", "Missing", "—", "Flagged before publication so stale or absent files are caught"),
            ),
            note="Any change to a single byte in scores.csv changes its SHA-256 fingerprint, letting a reviewer confirm the published table matches the run output.",
        )
        return inp, out

    # --- Goal: limits (Record what needs another test) ---
    if filename == "research_limits.md":
        inp = (
            '<div class="lab-route-card"><p class="lab-card-note"><strong>1. What internal validation measured:</strong> '
            "Agreement with supplied assessor grades and ABC/GCB subtype labels across validation folds drawn from the same main clinical cohort.</p>"
            '<p class="lab-card-note"><strong>2. What an independent cohort would test:</strong> '
            "Whether fixed models and preprocessing transfer across different laboratories, staining batches, scanners and patient populations.</p></div>"
        )
        out = mini_table(
            "How the study design qualifies each headline thesis result",
            ("Result area", "Internal finding", "Scope limit & next test"),
            (
                ("IHC grading", "Patch features reached 0.238 MAE vs averaged assessor grades (#agreement).", "Requires multi-centre cohorts and multiple annotators per slide (#grading-splits)."),
                ("Subtype prediction", "UNI patch features reached 0.970 accuracy / 0.992 AUC (#validation).", "Pooled across 3 folds within one cohort; requires external scanner & lab validation."),
                ("Spatial & explanation checks", "Positions gave no clear patch-scale gain (#subtype-ablations); masks show model sensitivity (#explain).", "Biological interpretation requires orthogonal experimental validation."),
            ),
        )
        return inp, out

    # --- Goal: pcam-bags & pcam-benchmarks (Appendix: separate benchmark work) ---
    if filename == "build_benchmark_bags.py":
        inp = mini_table(
            "Split parameters for repeatable positive and negative benchmark bags",
            ("Split", "Random seed", "Source patches (0 = neg, 1 = pos)", "Bags built", "Composition rule"),
            (
                ("train", "seed = 11", "train-00..05 (neg), train-06..09 (pos)", "4 bags (2 pos, 2 neg)", "4 patches/bag; pos bag has 1 pos patch"),
                ("test", "seed = 23", "test-00..05 (neg), test-06..09 (pos)", "4 bags (2 pos, 2 neg)", "4 patches/bag; pos bag has 1 pos patch"),
            ),
        )
        out = mini_table(
            "Generated bag manifests (positive instances highlighted in bold text)",
            ("Split (seed)", "Bag #", "Bag label", "Positive count", "Patch IDs in bag"),
            (
                ("train (11)", "1", "1 (positive)", "1", "train-04, train-00, train-05, train-06 (pos)"),
                ("train (11)", "2", "1 (positive)", "1", "train-04, train-06 (pos), train-00, train-03"),
                ("train (11)", "3–4", "0 (negative)", "0", "All patches from negative pool train-00..05"),
                ("test (23)", "1, 3", "1 (positive)", "1", "Contains test-09 (pos) or test-06 (pos)"),
                ("test (23)", "2, 4", "0 (negative)", "0", "All patches from negative pool test-00..05"),
            ),
        )
        return inp, out

    if filename == "compare_benchmark_encoders.py":
        inp = stat_cards(
            (("Fixed training split", "8 bags (4 pos, 4 neg · seed 11)"),
             ("Fixed test split", "8 bags (4 pos, 4 neg · seed 23)"),
             ("Pooling & classifier", "Max pooling + nearest centroid")),
            note="Both encoders receive the exact same train and test bag manifests from build_benchmark_bags.py.",
        )
        out = mini_table(
            "Encoder comparison on fixed benchmark bags (8 train bags, 8 test bags)",
            ("Stand-in encoder", "Feature definition", "Test bags (n)", "Balanced accuracy (mean of class recalls)"),
            (
                ("signal encoder", "Patch label + N(0, 0.1) noise", "8 (4 pos, 4 neg)", "1.000 (100%)"),
                ("noise encoder", "Pure N(0, 1) random noise", "8 (4 pos, 4 neg)", "0.625 (62.5%)"),
            ),
            highlight_row=0,
            note="Holding the bag manifests and pooling rule fixed verifies that the evaluation pipeline separates a known signal representation from random noise.",
        )
        return inp, out

    return "", ""
