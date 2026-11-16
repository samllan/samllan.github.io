"""Train a fresh grading baseline per fold and write held-out predictions."""
import csv
import sys

from train_scale_graders import predict_grades, train_graders


def write_predictions(output, features, grades, assignments):
    if grades.keys() != assignments.keys() or any(values.keys() != grades.keys() for values in features.values()):
        raise ValueError("Grades, assignments and features must cover the same IDs")
    folds = sorted(set(assignments.values()))
    if len(folds) < 2:
        raise ValueError("At least two held-out folds are required")
    writer = csv.writer(output)
    writer.writerow(("sample", "scale", "fold", "reference", "prediction"))
    for fold in folds:
        training = sorted(sample for sample, held_out in assignments.items() if held_out != fold)
        testing = sorted(sample for sample, held_out in assignments.items() if held_out == fold)
        for scale, model in train_graders(features, grades, training).items():
            test_features = {sample: features[scale][sample] for sample in testing}
            predicted = predict_grades(model, test_features)
            writer.writerows((sample, scale, fold, grades[sample], predicted[sample]) for sample in testing)


if __name__ == "__main__":
    features = {"patch": {"a": [0.1], "b": [0.35], "c": [0.7], "d": [0.9]}}
    grades = {"a": 0.0, "b": 1.0, "c": 2.0, "d": 3.0}
    write_predictions(sys.stdout, features, grades, {"a": 0, "b": 1, "c": 1, "d": 0})
