# Podcast ECoG tutorials: replication branch

This branch (`replication`) of the fork adds, on top of the unmodified tutorials:

* **Fixes** in `notebooks/` for current library versions: `05-atlases` (nilearn >= 0.12 returns the atlas table as `atlas['lut']`; the old `atlas['labels'].index/.name` fails) and `04-encoding` (`np.product` was removed in numpy 2).
* **`replication/`**: a small package `podcast_ecog` (loaders for the dataset, word-onset encoding, Destrieux labels), real-data tests, a tutorial runner and the scripts used to run everything on a cluster (SLURM, ORCD).

## Use
```
cd replication
python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pip install -e .
export PODCAST_BIDS_ROOT=/path/to/ds005574          # or run scripts/download_data.sh (aws CLI, 14.4 GiB -> replication/data/ds005574)
.venv/bin/python scripts/verify_download.py          # file names/sizes vs the OpenNeuro bucket
.venv/bin/python -m pytest -q tests                  # real-data smoke tests (subject 02)
.venv/bin/python scripts/run_tutorials.py            # executes notebooks/*.ipynb on the local copy (patched copies in notebooks_patched/, executed notebooks in executed/); failing cells are listed
```
`run_tutorials.py` comments out the `!pip` / `!wget` cells, sets `bids_root` to the local dataset and accepts `--subject-map 03=02` when only some subjects are present, `--only 04-encoding`.
Dataset: OpenNeuro ds005574 (CC BY), Zada, Nastase et al. 2025 (Sci Data). Upstream: <https://github.com/hassonlab/podcast-ecog-tutorials>.
