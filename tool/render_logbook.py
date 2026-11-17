"""Render the goal navigation and file tables from the same records."""
from html import escape
import json
from pathlib import Path


def render_logbook(research):
    groups = json.loads((research / "goals.json").read_text(encoding="utf-8"))
    examples = research / "examples"
    template = (research / "logbook.html").read_text(encoding="utf-8")
    crop_demo = (research / "crop_demo.html").read_text(encoding="utf-8")
    navigation, tables = [], []
    goal_ids, script_names = set(), set()
    titles = {goal["id"]: goal["title"] for group in groups for goal in group["goals"]}

    for group in groups:
        label = escape(group["title"])
        navigation.append(f'<h3 class="lab-group">{label}</h3>\n<ul>')
        for goal in group["goals"]:
            key, title = goal["id"], escape(goal["title"])
            if key in goal_ids:
                raise ValueError(f"Repeated research goal: {key}")
            goal_ids.add(key)
            navigation.append(f'<li><a href="#{key}">{title}</a>')
            script_links, rows = [], []
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
                rows.append(
                    f'<tr><td><a class="lab-file" href="{path}">{name}</a> '
                    f'<small>({escape(date)})</small></td><td>{escape(outcome)}</td></tr>'
                )
            if script_links:
                navigation.append('<ul class="lab-script-list">' + "\n".join(script_links) + "</ul>")
            navigation.append("</li>")

            rows_html = "\n      ".join(rows)
            demo_html = crop_demo if key == "crop" else ""
            related = goal.get("related", ())
            links = "".join(
                f'<a href="#{target}">{escape(titles[target])} →</a>' for target in related
            )
            onward = f'<nav class="lab-next" aria-label="Related goals">{links}</nav>\n' if links else ""
            tables.append(f'''<section id="{key}" class="lab-goal" data-goal>
  <p class="eyebrow">{label}</p>
  <h2>{title}</h2>
  <p class="lab-lede">{escape(goal["description"])}</p>
  <table class="lab-files" aria-label="{title}">
    <thead><tr><th scope="col">File and date</th><th scope="col">Outcome</th></tr></thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
{demo_html}{onward}</section>''')
        navigation.append("</ul>")

    missing = {path.name for path in examples.glob("*.py")} - script_names
    if missing:
        raise ValueError(f"Scripts without a goal: {', '.join(sorted(missing))}")
    return template.replace("<!-- goal navigation -->", "\n".join(navigation)).replace(
        "<!-- goal tables -->", "\n".join(tables)
    )
