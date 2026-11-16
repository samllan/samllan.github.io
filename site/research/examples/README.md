# PhD research logbook examples

This public edition consolidates selected workflows from Samuel Llanwarne's doctoral research at the University of Leeds. The examples run on small generated inputs. The thesis benchmark in `crop_benchmark.csv` is recorded separately from the synthetic runs.

From this folder, use Python 3.9 or newer. Install Pillow for the image examples and NumPy for the Barlow Twins example.

```sh
python -m pip install Pillow numpy
python crop_from_points.py example_grid.png clicks.csv crops
python tile_image.py example_grid.png tiles
python compare_image_formats.py example_grid.png --quality 75
python barlow_twins_loss.py
python compare_runs.py example_runs.csv --experiments baseline compact
python footprint.py --items 500 --height 224 --width 224 --features 256
python classwise_dimming.py
```

- `crop_from_points.py` combines the stored-click and crop-extraction steps into a portable example. See `crops/crop_manifest.csv` for the coordinates and output filenames.
- `tile_image.py` extracts fixed-size regions on a grid and saves their coordinates alongside the outputs in `tiles/tile_manifest.csv`.
- `compare_image_formats.py` measures storage and image differences on the same pixels. The original thesis measurement used a collection of research images.
- `barlow_twins_loss.py` demonstrates how [the Barlow Twins objective](https://proceedings.mlr.press/v139/zbontar21a.html) rewards agreement between two views while penalising redundant features. This example evaluates the objective on generated vectors.
- `compare_runs.py` demonstrates checking a complete fold-and-seed design and computing paired changes. This simplified example reports absolute differences from baseline.
- `footprint.py` compares raw 8-bit RGB image storage with fixed-length feature storage. Encoded images, container overhead and model execution have separate costs.
- `classwise_dimming.py` demonstrates one brightness mask per class with a toy linear model. The thesis experiments used trained models and visual overlays.

Research reference — Samuel Llanwarne, *Multi-Scale and Multi-Stage Deep Learning for the Classification of Diffuse Large B-cell Lymphoma Histology*, University of Leeds, 2026. See Table 2.5 for the extraction benchmark, Chapter 3 for the model comparisons, and Chapter 4 for representation costs and model explanations.
