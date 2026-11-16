"""Compare fixed aggregation rules on one small group of image patches.

The example accepts attention logits directly. The research learned weights
inside its models.
"""
import numpy as np


def pool_patches(features, attention_logits):
    features = np.asarray(features, dtype=float)
    attention_logits = np.asarray(attention_logits, dtype=float)
    if features.ndim != 2 or not len(features) or attention_logits.shape != (len(features),):
        raise ValueError("Provide one logit per patch")
    if not np.isfinite(features).all() or not np.isfinite(attention_logits).all():
        raise ValueError("Features and logits must be finite")
    weights = np.exp(attention_logits - attention_logits.max())
    weights /= weights.sum()
    return {
        "mean": features.mean(axis=0),
        "maximum": features.max(axis=0),
        "attention": weights @ features,
    }


if __name__ == "__main__":
    variants = pool_patches([[0.1, 0.9], [0.3, 0.7], [0.9, 0.2]], [0, 0, 1])
    print({method: vector.round(3).tolist() for method, vector in variants.items()})
