# PhD research scripts

This collection follows the work from preparing lymphoma tissue images through
to comparing models, checking results and rebuilding thesis figures. Each
script demonstrates one task on a small set of generated inputs.

Run the examples from this folder with Python 3.9 or later. Install NumPy
and Pillow with `python -m pip install numpy pillow`. The encoding comparison
uses Pillow with WebP support.

Run `python record_crop_marks.py` to see the annotation CSV, or
`python run_grading_example.py --output grading-demo` to reproduce the grading
workflow. The grading example saves split assignments, out-of-fold predictions,
an assessor comparison and the SVG figure in that folder. Run
`python build_grading_table.py grading-demo/predictions.csv` to build the
summary from those predictions.

The examples use small implementations to show the steps in the research.
For instance, ridge regression illustrates the grading workflow and a linear
autoencoder illustrates reconstruction. The historical extraction figures in
[`crop_benchmark.csv`](crop_benchmark.csv) come from thesis Table 2.5.

The original archive includes [CLAM](https://github.com/mahmoodlab/CLAM)
split tooling. The fold example illustrates the grouping described in the
thesis with newly written code.

The [research logbook](https://samllan.github.io/research/) puts the scripts in the
context of the thesis and includes a browser demo of the crop workflow.
