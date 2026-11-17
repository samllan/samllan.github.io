"""Render the goal tree and individual experiments from the same records."""
from calendar import month_abbr
from collections import defaultdict
import csv
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote


CROP_COLUMNS = (
    ("approach", "Approach"), ("seconds_per_sample", "Seconds per sample"),
    ("precision", "Precision"), ("recall", "Recall"), ("manual_intervention", "Manual intervention"),
)
STORY_LABELS = (("tried", "What I tried"), ("found", "What I found"), ("next", "Decision or next step"))


def figure_markup(figure):
    filename, alt, caption, *size = figure
    dimensions = f' width="{int(size[0])}" height="{int(size[1])}"' if size else ""
    return (
        f'<figure class="lab-figure"><img src="examples/{quote(filename)}" alt="{escape(alt, quote=True)}" '
        f'loading="lazy"{dimensions}><figcaption>{escape(caption)}</figcaption></figure>'
    )


def evidence_data(table, examples):
    if "csv" in table:
        with (examples / table["csv"]).open(encoding="utf-8", newline="") as stream:
            headings, *rows = csv.reader(stream)
        return headings, rows
    return table["headings"], table["rows"]


def evidence_table(table, examples):
    headings, rows = evidence_data(table, examples)
    columns = "".join(f'<th scope="col">{escape(heading)}</th>' for heading in headings)
    cells = "".join("<tr>" + "".join(f"<td>{escape(item)}</td>" for item in row) + "</tr>" for row in rows)
    note = f'<p>{escape(table["note"])}</p>' if table.get("note") else ""
    return (
        f'<div class="lab-evidence-table"><table class="lab-result-table">'
        f'<caption>{escape(table["title"])}</caption><thead><tr>{columns}</tr></thead>'
        f'<tbody>{cells}</tbody></table>{note}</div>'
    )


def example_markup(examples, filename, captured):
    suffix = Path(filename).suffix
    path = f"examples/{escape(filename, quote=True)}"
    if suffix in (".svg", ".png"):
        return f'<img src="{path}" alt="Output: {escape(filename, quote=True)}" loading="lazy">'
    if filename == "crop_benchmark.csv":
        with (examples / filename).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = "".join(
                "<tr>" + "".join(f"<td>{escape(row[key])}</td>" for key, _ in CROP_COLUMNS) + "</tr>"
                for row in reader
            )
        headings = "".join(f'<th scope="col">{label}</th>' for _, label in CROP_COLUMNS)
        return ('<table class="lab-result-table"><caption>Thesis Table 2.5</caption><thead><tr>'
                f'{headings}</tr></thead><tbody>{rows}</tbody></table>')
    if suffix == ".md":
        text = (examples / filename).read_text(encoding="utf-8")
        blocks = re.split(r"\n\s*\n", text.strip())
        paragraphs = []
        for block in blocks[1:]:
            block = escape(block)
            block = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", block)
            block = re.sub(r"\x60([^\x60]+)\x60", r"<code>\1</code>", block)
            block = re.sub(
                r"\[([^\]]+)\]\((https://[^\s()]+|[\w.-]+)\)",
                lambda m: f'<a href="{m[2] if m[2].startswith("https://") else "examples/" + m[2]}">{m[1]}</a>',
                block,
            )
            if block.startswith("- "):
                paragraphs.append("<ul>" + "".join(f"<li>{line[2:]}</li>" for line in block.splitlines()) + "</ul>")
            else:
                paragraphs.append(f"<p>{block}</p>")
        return '<div class="file-reading-guide">' + "".join(paragraphs) + "</div>"
    if suffix == ".csv" and filename != "crop_benchmark.csv":
        return evidence_table({"title": "Recorded measurements", "csv": filename}, examples)
    if suffix != ".py":
        text = (examples / filename).read_text(encoding="utf-8")
        return f'<pre>{escape(text)}</pre>'
    output = captured.get("stdout")
    if not output:
        raise ValueError(f"Missing row example output: {filename}")
    if filename == "render_grading_figure.py":
        encoded = quote(output, safe="")
        return f'<img src="data:image/svg+xml,{encoded}" alt="Example grading error bars by image scale">'
    if filename == "run_grading_example.py":
        worked_case = evidence_table(captured["table"], examples) if "table" in captured else ""
        files = "".join(
            f'<a href="examples/{quote(file)}">{escape(label)}</a>' for label, file in captured.get("assets", ())
        )
        return (worked_case + (f'<div class="lab-start">{files}</div>' if files else "") +
                '<img src="examples/grading_figure.svg" alt="Grading workflow figure for its 36 synthetic predictions">'
                f'<pre>{escape(output)}</pre>')
    note = captured.get("note")
    note_html = f'<p>{escape(note)}</p>' if note else ""
    visual = figure_markup(captured["figure"]) if "figure" in captured else ""
    return f'{visual}{note_html}<pre>{escape(output)}</pre>'


def narrative(goal, targets, examples):
    def route(target):
        key, marker, name = target.partition("/")
        if key not in targets or (marker and name not in targets[key]):
            raise ValueError(f"Unknown goal or output: {target}")
        return "#" + key + ("/" + quote(name, safe="") if marker else "")

    blocks = []
    if goal.get("start"):
        starters = "".join(f'<a href="{route(target)}">{escape(label)} →</a>' for label, target in goal["start"])
        blocks.append(f'<div class="lab-start">{starters}</div>')
    if "figure" in goal and goal["id"] != "question":
        blocks.append(figure_markup(goal["figure"]))
    if goal.get("path"):
        steps = "".join(
            f'<li><a href="{route(target)}">{escape(label)}</a><p>{escape(detail)}</p></li>'
            for label, target, detail in goal["path"]
        )
        blocks.append(f'<ol class="lab-path">{steps}</ol>')

    story = goal.get("story")
    if story:
        items = "".join(
            f'<div><dt>{escape(goal.get("next_label", label) if key == "next" else label)}</dt>'
            f'<dd>{escape(story[key])}</dd></div>'
            for key, label in STORY_LABELS
        )
        blocks.append(f'<dl class="lab-story">{items}</dl>')
        if story.get("source"):
            blocks.append(f'<p class="lab-evidence">{escape(story["source"])}</p>')
    if "table" in goal:
        blocks.append(evidence_table(goal["table"], examples))
    if "revision" in goal:
        date, previous, reason = goal["revision"]
        blocks.append(
            '<div class="lab-revision">'
            f'<p><strong>Decision revised</strong> · {escape(date)}</p>'
            f'<p><strong>Previous decision</strong> · {escape(previous)}</p>'
            f'<p><strong>Why it changed</strong> · {escape(reason)}</p></div>'
        )
    links = [
        f'<a href="{route(target)}">{escape(label)} →</a>' for label, target in goal.get("links", ())
    ]
    links += [
        f'<a href="{escape(target, quote=True)}">{escape(label)} →</a>'
        for label, target in goal.get("more", ())
    ]
    if links:
        blocks.append('<div class="lab-next">' + "".join(links) + "</div>")
    return "\n".join(blocks)


def date_label(date):
    months = {name: f"{number:02d}" for number, name in enumerate(month_abbr) if name}
    numeric = re.sub(
        r"\b([A-Z][a-z]{2}) (\d{4})\b",
        lambda match: f"{months[match[1]]}/{match[2]}" if match[1] in months else match[0],
        date,
    )
    return numeric.replace("–", " – ")


def load_leaf_details(project):
    path = project / "leaf_details.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def leaf_href(target):
    key, _, name = target.partition("/")
    return f"#{key}/{quote(name, safe='')}"


def labelled_values(values):
    return '<dl class="lab-values">' + "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>" for label, value in values
    ) + "</dl>"


def visual_pair(filename, examples, demo, captured):
    if filename == "research_questions.md":
        return (figure_markup(("image_scales.png", "Generated examples of a scan, a core, a patch and a cell crop",
                               "From a whole scan to a small region. These images are generated.")), "")
    if filename == "prepare_image_regions.py" and demo:
        return demo.split("<!-- output panel -->", 1)
    if filename == "render_score_overlay.py":
        return (
            figure_markup(("score_overlay_input.png", "Two outlined patches on a generated image",
                           "The patch scores are 0.30 and 0.80. The rectangles overlap.")),
            figure_markup(("score_overlay_output.png", "Heatmap of the same overlapping patches, with unscored pixels hatched",
                           "The overlap is 0.55. Hatching marks pixels with no score.")),
        )
    if filename == "crop_benchmark.csv":
        with (examples / filename).open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        chart = "".join(
            f'<li><span>{escape(row["approach"])}</span>'
            f'<meter min="0" max="6" value="{float(row["seconds_per_sample"]):g}" aria-label="{escape(row["approach"], quote=True)}"></meter>'
            f'<strong>{escape(row["seconds_per_sample"])} s</strong></li>'
            for row in rows
        )
        return ('<p class="lab-card-note">Each method was scored on speed, precision, recall and manual intervention.</p>',
                f'<p class="lab-card-note">Thesis Table 2.5 · seconds per sample</p><ul class="lab-bars">{chart}</ul>'
                '<p class="lab-card-note">Rectangles and point-and-click both reached 1.00 precision and recall.</p>')
    if filename == "bin_patch_distribution.py":
        rows = list(csv.DictReader(captured["stdout"].splitlines()))
        highest = max(int(row["cores"]) for row in rows)
        bars = []
        for row in rows:
            low, high, count = row["lower_inclusive"], row["upper_exclusive"], int(row["cores"])
            label = f"{low}+" if high == "None" else f"{low}–{int(high) - 1}"
            bars.append(f'<li><span>{label} patches</span><meter min="0" max="{highest}" value="{count}" '
                        f'aria-label="Cores with {label} patches"></meter><strong>{count}</strong></li>')
        return ("", '<p class="lab-card-note">Number of cores in each range</p>'
                    '<ul class="lab-bars">' + "".join(bars) + "</ul>")
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
            + labelled_values((("Reference", f"{ref:.3f}"), ("Prediction", f"{pred:.3f}"),
                               ("Absolute error", f"{abs(ref - pred):.3f}"))) + "</div>"
            for scale in scales for ref, pred in [predictions[scale]]
        )
        return (labelled_values((("Case", case["Case"]), ("Held-out fold", case["Validation fold"]),
                                ("Assessor A", case["Assessor A"]), ("Assessor B", case["Assessor B"]))),
                f'<label class="lab-scale-picker">Image scale <select data-image-scale>{selector}</select></label>'
                f'<div aria-live="polite">{panels}</div>')
    return "", ""


def render_leaf(goal, file, details, snapshots, examples, demo, context, downstream, labels):
    key = goal["id"]
    filename, date, outcome = file
    target = f"{key}/{filename}"
    path = f"examples/{quote(filename)}"
    captured = snapshots.get(filename, {})
    title = details.get("title", goal["title"])
    framing = escape(details.get("framing", goal["description"]))
    situation = escape(details["situation"]) if "situation" in details else ""
    situation_html = f'<p class="lab-card-note">{situation}</p>' if situation else ""
    method = details.get("method")
    method_html = f'<p>{escape(method)}</p>' if method else ""
    kind = ("Thesis benchmark" if filename == "crop_benchmark.csv" else
            "Fictional pilot" if date.startswith("Fictional") else
            "Research notes" if filename.endswith(".md") else "Synthetic example")

    def connections(targets, heading):
        if not targets:
            return ""
        links = "".join(f'<a href="{leaf_href(link)}">{escape(labels[link])}</a>' for link in targets)
        return f'<div class="lab-connections"><p>{heading}</p>{links}</div>'

    upstream = connections(details.get("from", ()), "Earlier in the workflow")
    onward = connections(downstream.get(target, ()), "Later in the workflow")
    input_visual, output_visual = visual_pair(filename, examples, demo, captured)
    captured_html = example_markup(examples, filename, captured)
    quantities = captured.get("quantity", "")
    if output_visual:
        extra = f'<details class="lab-detail"><summary>View recorded output</summary><div class="lab-output-content">{captured_html}</div></details>'
    else:
        extra = ""
        output_visual = f'<div class="lab-output-content">{captured_html}</div>'
    if filename == "prepare_image_regions.py" and demo:
        quantities = ""
    if quantities:
        metrics = "".join(f"<li>{escape(item)}</li>" for item in quantities.split(" · "))
        output_visual = f'<ul class="lab-metrics">{metrics}</ul>{output_visual}'
    input_text = f'<p class="lab-io-description">{escape(details["input"])}</p>' if details.get("input") else ""
    context_open = " open" if key == "question" else ""
    story = (f'<details class="lab-detail"{context_open}><summary>Research goal and evidence</summary>{context}</details>'
             if context else "")
    source_action = "View source" if filename.endswith(".py") else "Open original file"
    experiment = escape(target, quote=True)
    markup = f"""<article class="lab-experiment" id="{experiment}" data-experiment="{escape(filename, quote=True)}">
  <div class="lab-experiment-head">
    {f'<p class="lab-kicker">{escape(goal["title"])}</p>' if title != goal["title"] else ""}
    <h2 tabindex="-1">{escape(title)}</h2>
  </div>
  <section class="lab-framing" aria-label="Research question and notes">
    <div class="lab-framing-head"><h3>Question and notes</h3><button type="button" class="lab-edit" hidden>Edit</button></div>
    <p class="lab-framing-text">{framing}</p>
    {situation_html}
    <form class="lab-framing-form" hidden>
      <textarea aria-label="Question and notes" name="framing" rows="4" required></textarea>
      <div class="lab-form-actions"><button type="submit">Save</button><button type="button" data-cancel>Cancel</button>
      <button type="button" data-restore hidden>Restore original</button><small>Saved in this browser only.</small></div>
    </form>
    <small class="lab-framing-status" role="status"></small>
  </section>
  <div class="lab-io">
    <section class="lab-io-card lab-input"><h3>Input</h3>
      {input_text}{input_visual}{upstream}
    </section>
    <section class="lab-io-card lab-result"><div class="lab-io-head"><h3>Output</h3><span>{kind}</span></div>
      {output_visual}{onward}
    </section>
  </div>
  <section class="lab-experiment-notes">
    <h3>What this step did</h3>
    {method_html}<p>{escape(outcome)}</p>
    <div class="lab-next">
      <a data-preview href="{path}">{source_action} ↗</a>
      <a href="{leaf_href(target)}">Link to this entry</a>
    </div>
    {extra}{story}
  </section>
</article>"""
    return "\n".join(line.rstrip() for line in markup.splitlines())


def render_logbook(research, *, project=None):
    project = project or research
    settings_path = project / "project.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.is_file() else {
        "project title": "The PhD logbook",
        "back label": "PhD project",
        "back url": "../projects/phd.html",
        "source url": "https://github.com/samllan/samllan.github.io/tree/main/site/research/examples",
    }
    groups = json.loads((project / "goals.json").read_text(encoding="utf-8"))
    snapshots = json.loads((project / "row_examples.json").read_text(encoding="utf-8"))
    details = load_leaf_details(project)
    examples = project / "examples"
    template = (research / "logbook.html").read_text(encoding="utf-8")
    for name, value in settings.items():
        template = template.replace(f"<!-- {name} -->", escape(value, quote=True))
    demo = (research / "crop_demo.html").read_text(encoding="utf-8") if project == research else ""
    navigation, panels = [], []
    goal_ids, file_names = set(), set()
    goals = [goal for group in groups for goal in group["goals"]]
    titles = {goal["id"]: goal["title"] for goal in goals}
    targets = {goal["id"]: {file[0] for file in goal["files"]} for goal in goals}
    labels = {goal["id"] + "/" + file[0]: details.get(file[0], {}).get("title", file[0])
              for goal in goals for file in goal["files"]}
    downstream = defaultdict(list)
    for target in labels:
        for upstream in details.get(target.partition("/")[2], {}).get("from", ()):
            if upstream not in labels or upstream == target:
                raise ValueError(f"Invalid workflow link for {target}: {upstream}")
            downstream[upstream].append(target)

    for group in groups:
        label = escape(group["title"])
        children, sidebar = defaultdict(list), {}
        for goal in group["goals"]:
            key, title = goal["id"], escape(goal["title"])
            if key in goal_ids:
                raise ValueError(f"Repeated research goal: {key}")
            goal_ids.add(key)
            parent = goal.get("parent")
            if parent is not None and parent not in sidebar:
                raise ValueError(f"Parent of {key} must be an earlier goal in the same group")
            children[parent].append(key)
            if not goal["files"]:
                raise ValueError(f"Goal needs an entry: {key}")
            default_file = goal.get("default_file", goal["files"][0][0])
            if default_file not in targets[key]:
                raise ValueError(f"Unknown default entry for {key}: {default_file}")
            context = narrative(goal, targets, examples)
            featured = {link[1].partition("/")[0] for field in ("links", "path") for link in goal.get(field, ())}
            links = "".join(f'<a href="#{target}">{escape(titles[target])} →</a>'
                            for target in goal.get("related", ()) if target not in featured)
            if links:
                context += f'<nav class="lab-next" aria-label="Related goals">{links}</nav>'
            script_links, leaves = [], []
            for file in goal["files"]:
                filename, date, _ = file
                if Path(filename).name != filename or not (examples / filename).is_file():
                    raise ValueError(f"Invalid logbook file: {filename}")
                if filename in file_names:
                    raise ValueError(f"File is already listed under another goal: {filename}")
                file_names.add(filename)
                target = f"{key}/{filename}"
                audit = f' data-open-goal="{key}"' if filename.endswith(".py") else ""
                script_links.append(
                    f'<li><a class="lab-file lab-script"{audit} href="{leaf_href(target)}">'
                    f'<code>{escape(filename)}</code> <small>({escape(date_label(date))})</small></a></li>'
                )
                leaf_context = context if filename == default_file else ""
                leaves.append(render_leaf(goal, file, details.get(filename, {}), snapshots,
                                          examples, demo, leaf_context, downstream, labels))
            sidebar[key] = title, "".join(script_links)
            default = escape(default_file, quote=True)
            panels.append(f'<section id="{key}" class="lab-goal" data-goal>\n'
                          f'<div data-default-file="{default}">{"".join(leaves)}</div>\n</section>')

        def branch(parent):
            items = []
            for key in children[parent]:
                title, scripts = sidebar[key]
                items.append(
                    f'<li><a href="#{key}">{title}</a>'
                    f'<button type="button" class="lab-branch-toggle" aria-label="Entries under {title}" '
                    f'aria-expanded="true" aria-controls="branch-{key}" hidden></button>'
                    f'<div id="branch-{key}"><ul class="lab-script-list">{scripts}</ul>'
                )
                if children[key]:
                    items.append(f'<ul class="lab-branch">{branch(key)}</ul>')
                items.append("</div></li>")
            return "".join(items)

        tree_class = "lab-tree lab-group-tree" if label else "lab-tree"
        tree = f'<ul class="{tree_class}">{branch(None)}</ul>'
        if label:
            tree = f'<details class="lab-group"><summary>{label}</summary>{tree}</details>'
        navigation.append(tree)
    missing = {path.name for path in examples.glob("*.py")} - file_names
    if missing:
        raise ValueError(f"Scripts without a goal: {', '.join(sorted(missing))}")
    unused = details.keys() - file_names
    if unused:
        raise ValueError(f"Experiment details without an entry: {', '.join(sorted(unused))}")
    return template.replace("<!-- goal navigation -->", "\n".join(navigation)).replace(
        "<!-- experiments -->", "\n".join(panels)
    )
