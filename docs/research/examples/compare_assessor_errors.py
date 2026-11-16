"""Compare errors on the same samples with two available assessor grades."""
from math import isfinite
from statistics import mean


def compare_errors(first, second, predictions):
    sample_ids = sorted(first.keys() & second.keys() & predictions.keys())
    if not sample_ids:
        raise ValueError("No samples with both ratings and a prediction")
    assessor_gaps = []
    prediction_gaps = []
    for sample in sample_ids:
        a, b, prediction = first[sample], second[sample], predictions[sample]
        if not all(map(isfinite, (a, b, prediction))):
            raise ValueError(f"Nonfinite grade for {sample}")
        assessor_gaps.append(abs(a - b))
        prediction_gaps.append(abs(prediction - (a + b) / 2))
    return {
        "matched_samples": len(sample_ids),
        "assessor_gap": mean(assessor_gaps),
        "model_to_consensus_mae": mean(prediction_gaps),
    }


if __name__ == "__main__":
    print(compare_errors({"a": 1, "b": 2}, {"a": 2, "b": 2}, {"a": 1.4, "b": 1.8}))
