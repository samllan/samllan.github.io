"""Export the same PhD logbook content as one Markdown document."""
import argparse
import csv
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import quote, urljoin

from render_logbook import CROP_COLUMNS, STORY_LABELS, date_label, evidence_data, load_leaf_details


ROOT = Path(__file__).resolve().parents[1] / "site" / "research"
BASE = "https://samllan.github.io/research/"


def route(target):
    goal, slash, filename = target.partition("/")
    return BASE + "#" + goal + ("/" + quote(filename) if slash else "")


def asset(filename):
    return urljoin(BASE, "examples/" + quote(filename))


def figure(visual):
    filename, alt, caption, *_ = visual
    return f"![{alt}]({asset(filename)})\n\n{caption}"


def evidence(table, examples):
    headings, rows = evidence_data(table, examples)
    lines = ["| " + " | ".join(headings) + " |", "| " + " | ".join("---" for _ in headings) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    note = "\n\n" + table["note"] if table.get("note") else ""
    return f'**{table["title"]}**\n\n' + "\n".join(lines) + note


def notes(examples, filename):
    body = (examples / filename).read_text(encoding="utf-8").strip()
    body = re.sub(r"^(#{1,3})(?= )", lambda match: "#" * (len(match[1]) + 3), body, flags=re.M)
    return re.sub(r"\]\(([^()\s]+)\)", lambda match: "](" + urljoin(asset(filename), match[1]) + ")", body)


def benchmark(examples):
    headings = [label for _, label in CROP_COLUMNS]
    lines = ["| " + " | ".join(headings) + " |",
             "| " + " | ".join("---" for _ in headings) + " |"]
    with (examples / "crop_benchmark.csv").open(encoding="utf-8", newline="") as stream:
        lines.extend("| " + " | ".join(row[key] for key, _ in CROP_COLUMNS) + " |"
                     for row in csv.DictReader(stream))
    return "**Thesis Table 2.5**\n\n" + "\n".join(lines)


def crop_demo(research):
    template = (research / "crop_demo.html").read_text(encoding="utf-8")
    def read(name):
        return unescape(re.search(r'id="' + name + r'"[^>]*>([^<]+)', template)[1])

    return [
        "**Interactive crop demo · synthetic image**",
        read("demo-help"), f"![Synthetic image used in the crop demo]({asset('example_grid.png')})",
        read("crop-undo") + " · " + read("crop-download"),
        f"[Open the interactive crop demo]({route('crop/prepare_image_regions.py')})",
    ]


def export(research):
    groups = json.loads((research / "goals.json").read_text(encoding="utf-8"))
    snapshots = json.loads((research / "row_examples.json").read_text(encoding="utf-8"))
    examples = research / "examples"
    leaf_details = load_leaf_details(research)
    titles = {goal["id"]: goal["title"] for group in groups for goal in group["goals"]}
    parts = ["# Text Review Map", f"[The PhD logbook]({BASE}) · Snapshot of the published logbook", "## The PhD logbook"]
    parts.append("Dates refer to saved research versions or the thesis. The scripts are runnable adaptations using generated data.")
    appendix = []
    names = {f"{goal['id']}/{file[0]}": leaf_details.get(file[0], {}).get("title", file[0])
             for group in groups for goal in group["goals"] for file in goal["files"]}
    later = {}
    for target in names:
        for earlier in leaf_details.get(target.partition("/")[2], {}).get("from", ()):
            later.setdefault(earlier, []).append(target)
    for group in groups:
        if group["title"]:
            parts.append("## " + group["title"])
        for goal in group["goals"]:
            key = goal["id"]
            parts += ["### " + goal["title"], goal["description"]]
            if goal.get("start"):
                parts.append(" · ".join(f"[{label}]({route(target)})" for label, target in goal["start"]))
            if "figure" in goal:
                parts.append(figure(goal["figure"]))
            if goal.get("path"):
                parts.append("\n".join(f"{index}. [{label}]({route(target)})  \n   {detail}"
                    for index, (label, target, detail) in enumerate(goal["path"], 1)))
            if "story" in goal:
                story = goal["story"]
                parts.extend(
                    f"**{goal.get('next_label', label) if field == 'next' else label}**  \n{story[field]}"
                    for field, label in STORY_LABELS
                )
                if "source" in story:
                    parts.append(story["source"])
            if "table" in goal:
                parts.append(evidence(goal["table"], examples))
            if "revision" in goal:
                date, previous, reason = goal["revision"]
                parts += [f"**Decision revised** · {date}", f"**Previous decision** · {previous}", f"**Why it changed** · {reason}"]
            links = [f"[{label}]({route(target)})" for label, target in goal.get("links", ())]
            links.extend(f"[{label}]({urljoin(BASE, target)})" for label, target in goal.get("more", ()))
            if links:
                parts.append(" · ".join(links))
            parts.append("**Experiments and records**")
            for filename, date, outcome in goal["files"]:
                target = key + "/" + filename
                link = route(target)
                detail = leaf_details.get(filename, {})
                parts.extend((f"#### {names[target]}", f"[{filename}]({link}) ({date_label(date)})",
                              "**Question and notes**  \n" + detail.get("framing", goal["description"])))
                if "input" in detail:
                    parts.append("**Input**  \n" + detail["input"])
                parts.append("**What this step did**  \n" + " ".join(filter(None, (detail.get("method"), outcome))))
                for heading, connections in (("Earlier in the workflow", detail.get("from", ())),
                                             ("Later in the workflow", later.get(target, ()))):
                    if connections:
                        parts.append(heading + "  \n" + " · ".join(
                            f"[{names[connection]}]({route(connection)})" for connection in connections))
                if filename == "render_score_overlay.py":
                    parts.extend(figure(visual) for visual in (
                        ("score_overlay_input.png", "Generated input with two outlined patches",
                         "The patch scores are 0.30 and 0.80. The rectangles overlap."),
                        ("score_overlay_output.png", "Heatmap of the same patches, with unscored pixels hatched",
                         "The overlap is 0.55. Hatching marks pixels with no score."),
                    ))
                snapshot = snapshots.get(filename, {})
                if "quantity" in snapshot:
                    prefix = "Example · " if filename.endswith(".py") else ""
                    parts.append(prefix + snapshot["quantity"])
                if filename.endswith(".md"):
                    parts.append(notes(examples, filename))
                elif filename == "crop_benchmark.csv":
                    parts.append(benchmark(examples))
                elif filename.endswith((".svg", ".png")):
                    parts.append(f"![Output: {filename}]({asset(filename)})")
                if filename == "prepare_image_regions.py":
                    parts.extend(crop_demo(research))
                if "figure" in snapshot:
                    parts.append(figure(snapshot["figure"]))
                if "note" in snapshot:
                    parts.append(snapshot["note"])
                if "table" in snapshot:
                    parts.append(evidence(snapshot["table"], examples))
                if "assets" in snapshot:
                    parts.append(" · ".join(f"[{label}]({asset(file)})" for label, file in snapshot["assets"]))
                if "stdout" in snapshot:
                    appendix.append(f"#### [{filename}]({link})")
                    if filename == "render_grading_figure.py":
                        appendix.append(f"[Open the rendered figure]({link})")
                    else:
                        fence = chr(96) * 3
                        appendix.append(f"{fence}text\n{snapshot['stdout']}\n{fence}")
            featured = {item[1].partition("/")[0] for field in ("links", "path") for item in goal.get(field, ())}
            related = [f"[{titles[target]}]({route(target)})"
                       for target in goal.get("related", ()) if target not in featured]
            if related:
                parts.append(" · ".join(related))
    parts += ["## Example output appendix",
              "Captured output from the script entries. The examples use generated data.", *appendix]
    return "\n\n".join(parts) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    arguments.output.write_text(export(ROOT), encoding="utf-8")
