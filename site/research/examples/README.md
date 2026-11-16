# PhD research scripts

Four short adaptations from my doctoral research at the University of Leeds.
Each file includes a small example that shows its inputs and outputs.

| Script | What it shows |
| --- | --- |
| [Prepare image regions](prepare_image_regions.py) | Turn clicks and grids into labelled image regions with source coordinates. |
| [Learn image features](learn_image_features.py) | Measure agreement and redundancy between two views encoded by the same model. |
| [Compare experiments](compare_experiments.py) | Verify run coverage and compare error, time and memory against matching baseline runs. |
| [Explain a prediction](explain_prediction.py) | Fit separate brightness masks for competing classes while keeping the scoring model fixed. |

Run any of the files with Python 3.9 or later. The feature example uses NumPy.
The numeric examples are illustrative. The extraction figures in
[`crop_benchmark.csv`](crop_benchmark.csv) come from thesis Table 2.5.

The [research logbook](https://samllan.github.io/research/) puts the scripts in the
context of the thesis and includes a browser demo of the crop workflow.
