"""Compare frozen representations at bag level on fixed synthetic splits.

The workflow mirrors the separate PCam benchmark branch. Small numerical
features stand in for pretrained encoder outputs.
"""
import numpy as np

from build_benchmark_bags import make_bags


def evaluate_encoders(encoders, training, testing):
    train_ids = {key for bag in training for key in bag["patches"]}
    test_ids = {key for bag in testing for key in bag["patches"]}
    if train_ids & test_ids:
        raise ValueError("Training and test bags must use distinct patch IDs")
    train_labels = np.array([bag["label"] for bag in training])
    test_labels = np.array([bag["label"] for bag in testing])
    if set(train_labels) != {0, 1} or set(test_labels) != {0, 1}:
        raise ValueError("Both splits must contain each class")

    def features(bags, cache):
        result = []
        for bag in bags:
            patches = np.asarray([cache[key] for key in bag["patches"]], dtype=float)
            if patches.ndim != 2 or not patches.size or not np.isfinite(patches).all():
                raise ValueError("Each patch needs a finite feature vector")
            result.append(patches.max(axis=0))
        return np.stack(result)

    scores = {}
    for name, cache in encoders.items():
        training_features = features(training, cache)
        testing_features = features(testing, cache)
        centroids = np.stack([training_features[train_labels == label].mean(axis=0) for label in (0, 1)])
        distance = np.square(testing_features[:, None, :] - centroids[None, :, :]).sum(axis=-1)
        predictions = distance.argmin(axis=1)
        recalls = [(predictions[test_labels == label] == label).mean() for label in (0, 1)]
        scores[name] = float(np.mean(recalls))
    return scores


if __name__ == "__main__":
    training_labels = {f"train-{index}": int(index >= 6) for index in range(10)}
    testing_labels = {f"test-{index}": int(index >= 6) for index in range(10)}
    train = make_bags(training_labels, count_per_class=4, bag_size=4, positive_patches=1, seed=11)
    test = make_bags(testing_labels, count_per_class=4, bag_size=4, positive_patches=1, seed=23)
    labels = {**training_labels, **testing_labels}
    rng = np.random.default_rng(17)
    encoders = {
        "signal": {patch: [label + rng.normal(0, 0.1)] for patch, label in labels.items()},
        "noise": {patch: [rng.normal()] for patch in labels},
    }
    for encoder, score in evaluate_encoders(encoders, train, test).items():
        print(f"{encoder}: balanced accuracy {score:.3f}")
