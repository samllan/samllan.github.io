"""Render the goal tree and individual experiments from the same records."""
from calendar import month_abbr
from collections import defaultdict
import csv
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote

from leaf_visuals import goal_tentpole, leaf_visuals, mini_table, section_tentpole, table_cell


CROP_COLUMNS = (
    ("approach", "Approach"), ("seconds_per_sample", "Seconds per sample"),
    ("precision", "Precision"), ("recall", "Recall"), ("manual_intervention", "Manual intervention"),
)
STORY_LABELS = (("tried", "Tried"), ("found", "Found"), ("next", "Decision"))


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
    return mini_table(table["title"], headings, rows, note=table.get("note", ""))


def example_markup(examples, filename, captured):
    suffix = Path(filename).suffix
    path = f"examples/{escape(filename, quote=True)}"
    if suffix in (".svg", ".png"):
        return f'<img src="{path}" alt="Output: {escape(filename, quote=True)}" loading="lazy">'
    if filename == "crop_benchmark.csv":
        with (examples / filename).open(encoding="utf-8", newline="") as stream:
            rows = [[row[key] for key, _ in CROP_COLUMNS] for row in csv.DictReader(stream)]
        return mini_table("Thesis Table 2.5", [label for _, label in CROP_COLUMNS], rows)
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


def narrative(goal, targets, examples, titles):
    def route(target):
        key, marker, name = target.partition("/")
        if key not in targets or (marker and name not in targets[key]):
            raise ValueError(f"Unknown goal or output: {target}")
        return "#" + key + ("/" + quote(name, safe="") if marker else "")

    def prose(value):
        return re.sub(r"#([a-z]+(?:-[a-z]+)*)", lambda match: (
            f'<a href="#{match[1]}">{escape(titles[match[1]])}</a>'
            if match[1] in targets else match[0]
        ), escape(value))

    blocks = []
    if goal.get("start"):
        starters = "".join(f'<a href="{route(target)}">{escape(label)} →</a>' for label, target in goal["start"])
        blocks.append(f'<div class="lab-start">{starters}</div>')
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
            f'<div><dt>{escape(goal.get("next_label", label) if key == "next" else label)}</dt>'
            f'<dd>{prose(story[key])}</dd></div>'
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
    return leaf_visuals(filename, examples, demo, captured)


def breadcrumb_markup(ancestors):
    if not ancestors:
        return ""
    links = ' <span class="lab-crumb-sep" aria-hidden="true">/</span> '.join(
        f'<a href="#{escape(target, quote=True)}">{escape(label)}</a>' for target, label in ancestors
    )
    return f'<nav class="lab-kicker" aria-label="Breadcrumb">{links}</nav>'


def render_project_home(goal, context, research):
    starter = escape((research / "entry-template.md").read_text(encoding="utf-8").strip())
    return f"""<article class="lab-experiment lab-goal-overview lab-project-home" data-goal-overview>
  <div class="lab-experiment-head" id="question/research_questions.md" data-home-part>
    <h2 tabindex="-1">{escape(goal["title"])}</h2>
    <p class="lab-lede">{escape(goal["description"])}</p>
  </div>
  {context}
  <details class="lab-detail lab-home-detail" id="question/README.md" data-home-part>
    <summary>Run the grading example</summary>
    <p>The example runs on generated data and saves the splits, predictions and chart. Run these commands from the examples folder with Python 3.9 or later.</p>
    <pre class="lab-command">python -m pip install numpy pillow
python run_grading_example.py --output grading-demo</pre>
    <p><a href="examples/README.md">Full setup notes</a> · <a href="#figures/run_grading_example.py">See the worked example</a></p>
  </details>
  <details class="lab-detail lab-home-detail">
    <summary>Start your own logbook</summary>
    <p>Open an entry when you have a question. Add what you did and what happened as the work progresses.</p>
    <pre class="lab-command">{starter}</pre>
    <p><a href="entry-template.md" download>Download the blank entry</a> · <a href="example/">See a filled-in example</a></p>
  </details>
</article>"""


def render_group_overview(root_crumb, group_id, group, titles):
    label = group["title"]
    kicker = breadcrumb_markup([root_crumb])
    summary = group.get(
        "summary",
        "Questions, experiments and outcomes.",
    )
    rows = []
    for index, goal in enumerate(group["goals"], start=1):
        key = goal["id"]
        parent = goal.get("parent")
        prefix = "↳ " if parent else f"{index}. "
        parent_note = f'<div class="lab-step-sub">Under {escape(titles[parent])}</div>' if parent else ""
        story = goal.get("story", {})
        finding = story.get("found", "")
        finding_html = f'<div class="lab-arc-finding">{escape(finding)}</div>' if finding else ""
        file_pills = "".join(
            f'<li><a href="{leaf_href(f"{key}/{filename}")}"><code>{escape(filename)}</code></a></li>'
            for filename, _, _ in goal["files"]
        )
        rows.append(
            f'<tr role="row">'
            f'<td role="cell"><a class="lab-step-link" href="#{escape(key, quote=True)}">{prefix}{escape(goal["title"])} →</a>{parent_note}</td>'
            + table_cell("Question", escape(goal["description"]))
            + table_cell("Outcome and scripts", f'{finding_html}<ul class="lab-inline-files">{file_pills}</ul>')
            + "</tr>"
        )
    tentpole = section_tentpole(group_id)
    markup = f"""<section id="{escape(group_id, quote=True)}" class="lab-goal" data-group-section>
<article class="lab-experiment lab-goal-overview" data-group-overview>
  <div class="lab-experiment-head">
    {kicker}
    <h2 tabindex="-1">{escape(label)}</h2>
    <p class="lab-lede">{escape(summary)}</p>
  </div>
  {tentpole}
  <div class="lab-walkthrough-section" role="region" aria-label="Goals in this section">
    <table class="lab-result-table lab-arc-table lab-stack-table" role="table">
      <caption class="lab-screen-reader">Goals and outcomes</caption>
      <thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Goal</th><th scope="col" role="columnheader">Question tested</th><th scope="col" role="columnheader">Outcome &amp; scripts</th></tr></thead>
      <tbody role="rowgroup">{"".join(rows)}</tbody>
    </table>
  </div>
</article>
</section>"""
    return "\n".join(line.rstrip() for line in markup.splitlines())


def render_goal_overview(ancestors, goal, titles, descriptions, children, details, snapshots, context, examples=None):
    key = goal["id"]
    kicker = breadcrumb_markup(ancestors)
    tentpole = goal_tentpole(key, examples) if key != "question" else ""
    rows = []
    for index, (filename, date, outcome) in enumerate(goal["files"], start=1):
        target = f"{key}/{filename}"
        detail = details.get(filename, {})
        leaf_title = detail.get("title", filename)
        role = detail.get("role", date_label(date))
        quantity = snapshots.get(filename, {}).get("quantity", "")
        badge_html = f'<div class="lab-arc-badge"><span class="lab-step-badge">{escape(quantity)}</span></div>' if quantity else ""
        rows.append(
            f'<tr role="row">'
            f'<td role="cell"><a class="lab-step-link" href="{leaf_href(target)}">{index}. {escape(leaf_title)} →</a>'
            f'<div class="lab-step-meta"><code>{escape(filename)}</code> · {escape(date_label(date))}</div></td>'
            + table_cell("Role", escape(role), class_name="lab-step-role")
            + table_cell("Result", escape(outcome) + badge_html)
            + "</tr>"
        )
    subgoals_html = ""
    if children.get(key):
        sub_rows = "".join(
            f'<tr role="row"><td role="cell"><a class="lab-step-link" href="#{escape(child, quote=True)}">↳ {escape(titles[child])} →</a></td>'
            + table_cell("Question", escape(descriptions[child])) + "</tr>"
            for child in children[key]
        )
        subgoals_html = (
            '<div class="lab-subgoals" role="region" aria-label="Next sub-goals in this branch">'
            '<table class="lab-result-table lab-arc-table lab-stack-table" role="table">'
            '<caption>Follow-on sub-goals in this branch</caption>'
            '<thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Sub-goal</th><th scope="col" role="columnheader">Question tested</th></tr></thead>'
            f'<tbody role="rowgroup">{sub_rows}</tbody></table></div>'
        )
    context_block = f'<div class="lab-goal-context">{context}</div>' if context else ""
    markup = f"""<article class="lab-experiment lab-goal-overview" data-goal-overview>
  <div class="lab-experiment-head">
    {kicker}
    <h2 tabindex="-1">{escape(goal["title"])}</h2>
    <p class="lab-lede">{escape(goal["description"])}</p>
  </div>
  {tentpole}
  {context_block}
  <div class="lab-walkthrough-section" role="region" aria-label="Narrative walkthrough of experiments">
    <table class="lab-result-table lab-arc-table lab-stack-table" role="table">
      <caption class="lab-screen-reader">Experiments and outcomes</caption>
      <thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Step</th><th scope="col" role="columnheader">Role in the story</th><th scope="col" role="columnheader">Result / output</th></tr></thead>
      <tbody role="rowgroup">{"".join(rows)}</tbody>
    </table>
  </div>
  {subgoals_html}
</article>"""
    return "\n".join(line.rstrip() for line in markup.splitlines())


def render_leaf(ancestors, goal, file, details, snapshots, examples, demo, context, downstream, labels):
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
            "Demo and thesis comparison" if filename == "compare_image_encodings.py" else
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
    source_action = "View script" if filename.endswith(".py") else "Open file"
    source_tag = "Script" if filename.endswith(".py") else "File"
    role = details.get("role", date_label(date))
    experiment = escape(target, quote=True)
    kicker = breadcrumb_markup([*ancestors, (key, goal["title"])])
    markup = f"""<article class="lab-experiment" id="{experiment}" data-experiment="{escape(filename, quote=True)}">
  <div class="lab-experiment-head">
    {kicker}
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
  <a class="lab-script-banner" data-preview href="{path}">
    <span class="lab-script-tag" aria-hidden="true">{source_tag}</span>
    <code>{escape(filename)}</code>
    <span class="lab-script-meta">{escape(role)} · {escape(date_label(date))}</span>
    <span class="lab-script-cta">{source_action} ↗</span>
  </a>
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
    {extra}{story}
  </section>
</article>"""
    return "\n".join(line.rstrip() for line in markup.splitlines())


def render_logbook(research, *, project=None):
    project = project or research
    settings_path = project / "project.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.is_file() else {
        "project title": "The PhD logbook",
        "root label": "PhD logbook",
        "back label": "PhD project",
        "back url": "../projects/phd.html",
        "source url": "https://github.com/samllan/samllan.github.io/tree/main/site/research/examples",
    }
    root_label = settings.setdefault("root label", re.sub(r"^The\s+", "", settings["project title"]))
    root_crumb = ("question", root_label)
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
    descriptions = {goal["id"]: goal["description"] for goal in goals}
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
        group_id = (
            "section-" + re.sub(r"[^a-z0-9]+", "-", group["title"].casefold()).strip("-")
            if group["title"] else ""
        )
        if group_id:
            panels.append(render_group_overview(root_crumb, group_id, group, titles))
        children, sidebar, parents = defaultdict(list), {}, {}
        for goal in group["goals"]:
            key, title = goal["id"], escape(goal["title"])
            if key in goal_ids:
                raise ValueError(f"Repeated research goal: {key}")
            goal_ids.add(key)
            parent = goal.get("parent")
            if parent is not None and parent not in sidebar:
                raise ValueError(f"Parent of {key} must be an earlier goal in the same group")
            children[parent].append(key)
            parents[key] = parent
            sidebar[key] = None

        def goal_ancestors(key):
            chain = []
            current = parents.get(key)
            while current is not None:
                chain.append((current, titles[current]))
                current = parents.get(current)
            chain.reverse()
            if group_id:
                chain.insert(0, (group_id, group["title"]))
            if key != "question":
                chain.insert(0, root_crumb)
            return chain

        for goal in group["goals"]:
            key, title = goal["id"], escape(goal["title"])
            if not goal["files"]:
                raise ValueError(f"Goal needs an entry: {key}")
            default_file = goal.get("default_file", goal["files"][0][0])
            if default_file not in targets[key]:
                raise ValueError(f"Unknown default entry for {key}: {default_file}")
            is_home = project == research and key == root_crumb[0]
            context = narrative(goal, targets, examples, titles)
            featured = {link[1].partition("/")[0] for field in ("links", "path") for link in goal.get(field, ())}
            links = "".join(f'<a href="#{target}">{escape(titles[target])} →</a>'
                            for target in goal.get("related", ()) if target not in featured)
            if links and not is_home:
                context += f'<nav class="lab-next" aria-label="Related goals">{links}</nav>'
            ancestors = goal_ancestors(key)
            overview = (
                render_project_home(goal, context, research) if is_home else render_goal_overview(
                    ancestors, goal, titles, descriptions, children, details, snapshots, context, examples
                )
            )
            script_links, leaves = [], []
            for file in goal["files"]:
                filename, date, _ = file
                if Path(filename).name != filename or not (examples / filename).is_file():
                    raise ValueError(f"Invalid logbook file: {filename}")
                if filename in file_names:
                    raise ValueError(f"File is already listed under another goal: {filename}")
                file_names.add(filename)
                if is_home:
                    continue
                target = f"{key}/{filename}"
                audit = f' data-open-goal="{key}"' if filename.endswith(".py") else ""
                script_links.append(
                    f'<li><a class="lab-file lab-script"{audit} href="{leaf_href(target)}">'
                    f'<code>{escape(filename)}</code> <small>({escape(date_label(date))})</small></a></li>'
                )
                leaf_context = context if filename == default_file else ""
                leaves.append(render_leaf(ancestors, goal, file, details.get(filename, {}), snapshots,
                                          examples, demo, leaf_context, downstream, labels))
            sidebar[key] = title, "".join(script_links)
            default = escape(default_file, quote=True)
            leaf_markup = f'\n<div data-default-file="{default}">{"".join(leaves)}</div>' if leaves else ""
            panels.append(f'<section id="{key}" class="lab-goal" data-goal>\n{overview}{leaf_markup}\n</section>')

        def branch(parent):
            items = []
            for key in children[parent]:
                title, scripts = sidebar[key]
                items.append(
                    f'<li class="lab-node"><div class="lab-row">'
                    f'<button type="button" class="lab-branch-toggle" aria-label="Entries under {title}" '
                    f'aria-expanded="true" aria-controls="branch-{key}" hidden></button>'
                    f'<a class="lab-node-link" href="#{key}">{title}</a></div>'
                    f'<div id="branch-{key}" class="lab-children"><ul class="lab-script-list">{scripts}</ul>'
                )
                if children[key]:
                    items.append(f'<ul class="lab-branch">{branch(key)}</ul>')
                items.append("</div></li>")
            return "".join(items)

        if label:
            tree = (
                f'<ul class="lab-tree lab-group">'
                f'<li class="lab-node lab-group-node"><div class="lab-row">'
                f'<button type="button" class="lab-branch-toggle" aria-label="Goals under {label}" '
                f'aria-expanded="true" aria-controls="branch-{group_id}" hidden></button>'
                f'<a class="lab-node-link lab-group-link" href="#{group_id}">{label}</a></div>'
                f'<div id="branch-{group_id}" class="lab-children">'
                f'<ul class="lab-group-tree">{branch(None)}</ul></div></li></ul>'
            )
        elif project != research:
            tree = f'<ul class="lab-tree">{branch(None)}</ul>'
        else:
            continue
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
