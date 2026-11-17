"""Replay the small grading workflow from split assignment to figure."""
import argparse
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from assign_validation_folds import assign_folds
from build_grading_table import build_table
from compare_assessor_errors import compare_errors
from prepare_reference_grades import reference_grades
from render_grading_figure import render_figure
from save_held_out_grades import write_predictions


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    ids = [f"S{i:02}" for i in range(12)]
    signal = {sample: (i % 4) + (i % 3 - 1) * 0.2 for i, sample in enumerate(ids)}
    first = {sample: round(value) for sample, value in signal.items()}
    # Give one teaching case a controlled disagreement between the two ratings.
    case = "S02"
    second = {**first, case: 3}
    ratings = [(sample, assessor, table[sample]) for assessor, table in (("A", first), ("B", second)) for sample in ids]
    grades = {sample: result[0] for sample, result in reference_grades(ratings).items()}
    assignments = assign_folds([(sample, f"G{i // 2}") for i, sample in enumerate(ids)], 3)
    features = {
        scale: {sample: [signal[sample] + spread * ((i % 5) - 2)] for i, sample in enumerate(ids)}
        for scale, spread in (("core", 0.30), ("patch", 0.08), ("cell", 0.23))
    }
    with (output / "splits.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("sample", "held_out_fold"))
        writer.writerows(sorted(assignments.items()))
    with (output / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        write_predictions(stream, features, grades, assignments)
    with (output / "predictions.csv").open(encoding="utf-8", newline="") as stream:
        rows = build_table(stream)
        stream.seek(0)
        predictions = {
            row["sample"]: float(row["prediction"])
            for row in csv.DictReader(stream) if row["scale"] == "patch"
        }
    agreement = compare_errors(first, second, predictions)
    case_rows = [
        ("Case", case), ("Validation fold", assignments[case]),
        ("Assessor A", first[case]), ("Assessor B", second[case]),
        ("Reference grade (mean)", f"{grades[case]:.3f}"),
        ("Patch model prediction", f"{predictions[case]:.3f}"),
        ("Absolute error (grade points)", f"{abs(predictions[case] - grades[case]):.3f}"),
    ]
    with (output / "case_trace.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Field", "Value"))
        writer.writerows(case_rows)
    with (output / "agreement.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(agreement))
        writer.writeheader()
        writer.writerow(agreement)
    (output / "grading_figure.svg").write_text(render_figure(rows), encoding="utf-8")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        print(run(args.output))
    else:
        with TemporaryDirectory() as directory:
            print(run(Path(directory)))
