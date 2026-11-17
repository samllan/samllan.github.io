"""Render the goal navigation and file tables from the same records."""
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
    filename, alt, caption = figure
    return (
        f'<figure class="lab-figure"><img src="examples/{quote(filename)}" alt="{escape(alt, quote=True)}" '
        f'loading="lazy"><figcaption>{escape(caption)}</figcaption></figure>'
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
    if suffix != ".py":
        text = (examples / filename).read_text(encoding="utf-8")
        return f'<pre{" data-markdown" if suffix == ".md" else ""}>{escape(text)}</pre>'
    output = captured.get("stdout")
    if not output:
        raise ValueError(f"Missing row example output: {filename}")
    if filename == "render_grading_figure.py":
        encoded = quote(output, safe="")
        return f'<img src="data:image/svg+xml,{encoded}" alt="Example grading error bars by image scale">'
    if filename == "run_grading_example.py":
        return ('<img src="examples/grading_figure.svg" alt="Grading workflow figure for its 36 synthetic predictions">'
                f'<pre>{escape(output)}</pre>')
    note = captured.get("note")
    note_html = f'<p>{escape(note)}</p>' if note else ""
    visual = figure_markup(captured["figure"]) if "figure" in captured else ""
    return f'{visual}{note_html}<pre>{escape(output)}</pre>'


def narrative(goal, targets):
    def route(target):
        key, marker, name = target.partition("/")
        if key not in targets or (marker and name not in targets[key]):
            raise ValueError(f"Unknown goal or output: {target}")
        return "#" + key + ("/" + quote(name, safe="") if marker else "")

    blocks = []
    if "figure" in goal:
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
            f'<div><dt>{label}</dt><dd>{escape(story[key])}</dd></div>'
            for key, label in STORY_LABELS
        )
        blocks.append(f'<dl class="lab-story">{items}</dl>')
        if story.get("source"):
            blocks.append(f'<p class="lab-evidence">{escape(story["source"])}</p>')
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
    examples = project / "examples"
    template = (research / "logbook.html").read_text(encoding="utf-8")
    for name, value in settings.items():
        template = template.replace(f"<!-- {name} -->", escape(value, quote=True))
    crop_demo = (research / "crop_demo.html").read_text(encoding="utf-8") if project == research else ""
    navigation, tables = [], []
    goal_ids, script_names = set(), set()
    titles = {goal["id"]: goal["title"] for group in groups for goal in group["goals"]}
    targets = {goal["id"]: {f[0] for f in goal["files"]} for group in groups for goal in group["goals"]}

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
            script_links, rows, outputs = [], [], []
            for filename, date, outcome in goal["files"]:
                if Path(filename).name != filename or not (examples / filename).is_file():
                    raise ValueError(f"Invalid logbook file: {filename}")
                path = f"examples/{escape(filename, quote=True)}"
                name = f"<code>{escape(filename)}</code>"
                if filename.endswith(".py"):
                    if filename in script_names:
                        raise ValueError(f"Script is already listed under another goal: {filename}")
                    script_names.add(filename)
                    script_links.append(
                        f'<li><a class="lab-file lab-script" data-open-goal="{key}" href="{path}">{name}</a></li>'
                    )
                captured = snapshots.get(filename, {})
                quantity = captured.get("quantity")
                if quantity and filename.endswith(".py"):
                    quantity = f"Example · {quantity}"
                label_html = f'<small class="lab-quantity">{escape(quantity)}</small>' if quantity else ""
                year = max(map(int, re.findall(r"\b\d{4}\b", date)), default=0)
                rows.append(
                    f'<tr data-source-year="{year}"><td><a class="lab-file lab-row-file" href="{path}">{name}</a> '
                    f'<small>({escape(date)})</small></td><td>{escape(outcome)}{label_html}</td></tr>'
                )
                markup = example_markup(examples, filename, captured)
                kind = ("Thesis benchmark" if filename == "crop_benchmark.csv"
                        else "Research notes" if filename.endswith(".md") else "Synthetic example")
                outputs.append(f'<template data-file="{escape(filename, quote=True)}" data-kind="{kind}">{markup}</template>')

            scripts = '<ul class="lab-script-list">' + "\n".join(script_links) + "</ul>" if script_links else ""
            sidebar[key] = title, scripts

            rows_html = "\n      ".join(rows)
            demo_html = crop_demo if key == "crop" else ""
            output_html = "\n".join(outputs)
            related = goal.get("related", ())
            featured = {link[1].partition("/")[0] for field in ("links", "path") for link in goal.get(field, ())}
            links = "".join(
                f'<a href="#{target}">{escape(titles[target])} →</a>' for target in related if target not in featured
            )
            onward = f'<nav class="lab-next" aria-label="Related goals">{links}</nav>\n' if links else ""
            default_file = goal.get("default_file")
            if default_file is not None and default_file not in targets[key]:
                raise ValueError(f"Unknown default output for {key}: {default_file}")
            default_attr = f' data-default-file="{escape(default_file, quote=True)}"' if default_file else ""
            summary_open = "" if goal.get("path") else " open"
            story_html = narrative(goal, targets)
            tables.append(f'''<section id="{key}" class="lab-goal" data-goal>
  <h2>{title}</h2>
  <p class="lab-lede">{escape(goal["description"])}</p>
{story_html}
  <details class="lab-files-panel"{default_attr}{summary_open}>
  <summary>Files and outputs</summary>
  <div class="lab-order" hidden><label>Sort <select>
    <option value="workflow">Workflow order</option>
    <option value="file">Filename A–Z</option>
    <option value="year">Newest source year</option>
  </select></label></div>
  <table class="lab-files" aria-label="{title}">
    <thead><tr><th scope="col">File and date</th><th scope="col">Outcome</th></tr></thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
  <div class="lab-output" hidden>
    <div class="lab-output-head">
      <div><p class="eyebrow lab-output-kind"></p><h3 class="lab-output-title" aria-live="polite"></h3></div>
      <div class="lab-output-actions">
        <a class="lab-preview-link" data-preview>View file ↗</a>
        <a class="lab-share-link">Link to this output</a>
      </div>
    </div>
    <div class="lab-output-content"></div>
{demo_html}  </div>
  </details>
{output_html}
{onward}</section>''')

        def branch(parent):
            items = []
            for key in children[parent]:
                title, scripts = sidebar[key]
                link = f'<li><a href="#{key}">{title}</a>'
                subgoals = ""
                if children[key]:
                    subgoals = (
                        f'<button type="button" class="lab-branch-toggle" aria-label="Subgoals of {title}" '
                        f'aria-expanded="true" aria-controls="branch-{key}" hidden></button>'
                    )
                items.append(link + subgoals + scripts)
                if children[key]:
                    items.append(f'<ul class="lab-branch" id="branch-{key}">{branch(key)}</ul>')
                items.append("</li>")
            return "".join(items)

        tree_class = "lab-tree lab-group-tree" if label else "lab-tree"
        tree = f'<ul class="{tree_class}">{branch(None)}</ul>'
        if label:
            tree = f'<details class="lab-group"><summary>{label}</summary>{tree}</details>'
        navigation.append(tree)

    missing = {path.name for path in examples.glob("*.py")} - script_names
    if missing:
        raise ValueError(f"Scripts without a goal: {', '.join(sorted(missing))}")
    return template.replace("<!-- goal navigation -->", "\n".join(navigation)).replace(
        "<!-- goal tables -->", "\n".join(tables)
    )
