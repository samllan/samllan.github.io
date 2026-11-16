"""Fit simple grading baselines on the same examples at different scales.

Ridge regression on generated features illustrates the comparison structure.
The thesis trained deep models on image-derived inputs.
"""
import numpy as np


def train_graders(features_by_scale, grades, training_ids, ridge=0.1):
    ids = tuple(training_ids)
    if not ids or len(set(ids)) != len(ids) or ridge <= 0:
        raise ValueError("Provide distinct training IDs and a positive penalty")
    targets = np.array([grades[sample] for sample in ids])
    models = {}
    for scale, features in features_by_scale.items():
        matrix = np.array([features[sample] for sample in ids], dtype=float)
        if matrix.ndim != 2 or not np.isfinite(matrix).all():
            raise ValueError(f"Invalid feature matrix for {scale}")
        design = np.column_stack((np.ones(len(ids)), matrix))
        penalty = np.eye(design.shape[1]) * ridge
        penalty[0, 0] = 0
        models[scale] = np.linalg.solve(design.T @ design + penalty, design.T @ targets)
    return models


def predict_grades(model, features):
    return {sample: float(model[0] + np.asarray(vector) @ model[1:]) for sample, vector in features.items()}


if __name__ == "__main__":
    grades = {"a": 1.0, "b": 2.0, "c": 3.0}
    features = {"patch": {"a": [0.1], "b": [0.5], "c": [0.9]}, "cell": {"a": [0.3], "b": [0.6], "c": [0.7]}}
    for name, model in train_graders(features, grades, ("a", "b")).items():
        print(name, predict_grades(model, {"c": features[name]["c"]}))
