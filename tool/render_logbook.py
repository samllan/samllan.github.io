"""Render the goal navigation and file tables from the same records."""
from collections import defaultdict
import csv
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote


def example_markup(examples, filename, captured):
    suffix = Path(filename).suffix
    path = f"examples/{escape(filename, quote=True)}"
    if suffix in (".svg", ".png"):
        return f'<img src="{path}" alt="Output: {escape(filename, quote=True)}" loading="lazy">'
    if filename == "crop_benchmark.csv":
        with (examples / filename).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = "".join(
                "<tr>" + "".join(f"<td>{escape(row[key])}</td>" for key in
                                  ("approach", "seconds_per_sample", "precision", "recall")) + "</tr>"
                for row in reader
            )
        return ('<table class="lab-result-table"><caption>Thesis Table 2.5</caption><thead><tr>'
                '<th scope="col">Approach</th><th scope="col">Seconds per sample</th>'
                '<th scope="col">Precision</th><th scope="col">Recall</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>')
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
    note = '<p>Timings depend on the machine and filesystem cache.</p>' if filename == "measure_storage_reads.py" else ""
    return f'{note}<pre>{escape(output)}</pre>'


def render_logbook(research):
    groups = json.loads((research / "goals.json").read_text(encoding="utf-8"))
    snapshots = json.loads((research / "row_examples.json").read_text(encoding="utf-8"))
    examples = research / "examples"
    template = (research / "logbook.html").read_text(encoding="utf-8")
    crop_demo = (research / "crop_demo.html").read_text(encoding="utf-8")
    navigation, tables = [], []
    goal_ids, script_names = set(), set()
    titles = {goal["id"]: goal["title"] for group in groups for goal in group["goals"]}

    for group in groups:
        label = escape(group["title"])
        if label:
            navigation.append(f'<h3 class="lab-group">{label}</h3>')
        eyebrow = f'<p class="eyebrow">{label}</p>\n  ' if label else ""
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
                outputs.append(f'<template data-file="{escape(filename, quote=True)}">{markup}</template>')

            scripts = '<ul class="lab-script-list">' + "\n".join(script_links) + "</ul>" if script_links else ""
            sidebar[key] = title, scripts

            rows_html = "\n      ".join(rows)
            demo_html = crop_demo if key == "crop" else ""
            output_html = "\n".join(outputs)
            related = goal.get("related", ())
            links = "".join(
                f'<a href="#{target}">{escape(titles[target])} →</a>' for target in related
            )
            onward = f'<nav class="lab-next" aria-label="Related goals">{links}</nav>\n' if links else ""
            tables.append(f'''<section id="{key}" class="lab-goal" data-goal>
  {eyebrow}<h2>{title}</h2>
  <p class="lab-lede">{escape(goal["description"])}</p>
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
      <a class="lab-preview-link" data-preview>View file ↗</a>
    </div>
    <div class="lab-output-content"></div>
{demo_html}  </div>
{output_html}
{onward}</section>''')

        def branch(parent):
            return "".join(
                f'<li><a href="#{key}">{sidebar[key][0]}</a>{sidebar[key][1]}'
                + (f'<ul class="lab-branch">{branch(key)}</ul>' if children[key] else "") + "</li>"
                for key in children[parent]
            )

        tree_class = "lab-tree lab-group-tree" if label else "lab-tree"
        navigation.append(f'<ul class="{tree_class}">{branch(None)}</ul>')

    missing = {path.name for path in examples.glob("*.py")} - script_names
    if missing:
        raise ValueError(f"Scripts without a goal: {', '.join(sorted(missing))}")
    return template.replace("<!-- goal navigation -->", "\n".join(navigation)).replace(
        "<!-- goal tables -->", "\n".join(tables)
    )
