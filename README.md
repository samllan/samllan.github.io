# Samuel Llanwarne's portfolio

[Public website](https://samllan.github.io/)

Eleven project stories covering products, research, community and creative technology.
Static HTML, with browser demonstrations for Fourier modelling and Music Note Rain.
Experimental work is labelled as such.

## Edit and build

- `tool/build_site.py`: content and shared HTML layout.
- `tool/style.css`: responsive presentation.
- `tool/experiments.js`: browser demonstrations.
- `tool/music-demo.json`: 36 notes from Music Note Rain's composed sample.
- `tool/lane_demo.py`: optional regeneration of the educational lane overlay (NumPy/Pillow).
- `site/assets/`: selected images; no private recordings or model checkpoints.
- `site/flutter_service_worker.js`: retires caches from the former Flutter site.
- `docs/`: generated, committed public website.

Requires Python 3.9+; no third-party Python packages:

```sh
python tool/build_site.py
python -m http.server 8937 --bind 127.0.0.1 --directory docs
```

Check changed pages and demonstrations before committing source and `docs/`
together. GitHub Pages automatically publishes `main` → `/docs`. No Flutter build
or separate hosting service is needed. Historical Flutter source remains in Git.

## Publication and rollback

The former live version is preserved at branch
`rollback/pre-static-portfolio-2026-10-24` (commit
`92e9e2fbb4190012ada714958831e69f0cc764af`).

The migration and follow-up fixes are ordinary release commits. To roll back,
restore the saved branch's source and `docs/` as a new commit on `main`, then
push. GitHub Pages republishes the previous site while preserving the history.
Avoid resetting or force-pushing main.

## Attribution

Word Map: equal collaboration with Nina Sushko (interface/design), with Samuel
responsible for data and application logic. Incidental AI: four-person hackathon
team. Field II experiments build on examples by Jørgen Arendt Jensen. Recent
independent products use AI-assisted implementation under Samuel's product and
design direction. Individual pages explain their context and evidence limits.
