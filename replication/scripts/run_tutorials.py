"""Run the authors' tutorial notebooks (external/podcast-ecog-tutorials) against a local copy of ds005574 and report which cells fail.
Patches applied to copies in notebooks_patched/: `bids_root = ""` -> the local root (so no download), shell magics (`!pip`, `!wget`, `!python -m spacy download`) are commented out, the nilearn >= 0.12 atlas API,
tutorial 00's relative derivative path, and an optional subject remap (use when only some subjects are present locally).
  .venv/bin/python scripts/run_tutorials.py [--root ROOT] [--only 00-intro 04-encoding] [--subject-map 03=02 01=08] [--timeout 3600]"""
import argparse, json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from podcast_ecog import bids_root
_R = Path(__file__).resolve().parents[1]; EXT = _R.parent / "notebooks" if (_R.parent / "notebooks" / "00-intro.ipynb").exists() else _R / "external" / "podcast-ecog-tutorials" / "notebooks"   # inside the tutorials fork (replication/ folder) or the podcast_ecog layout
ap = argparse.ArgumentParser(); ap.add_argument("--root"); ap.add_argument("--only", nargs="*"); ap.add_argument("--subject-map", nargs="*", default=[]); ap.add_argument("--timeout", type=int, default=3600); a = ap.parse_args()
root = str(bids_root(a.root)) + "/"; smap = dict(m.split("=") for m in a.subject_map); out = EXT.parent / "notebooks_patched"; out.mkdir(exist_ok=True); (EXT.parent / "executed").mkdir(exist_ok=True)
def fix(src):
    src = re.sub(r'^!.*$', lambda m: "# " + m.group(0), src, flags=re.M)                       # shell magics
    src = src.replace('bids_root = ""', f'bids_root = "{root}"')
    src = src.replace('root="derivatives/ecogprep"', f'root="{root}derivatives/ecogprep"').replace("read_raw_fif(file_path.basename", "read_raw_fif(file_path.fpath")
    src = src.replace("indices = atlas['labels'].index", "indices = atlas['lut']['index']").replace("names = atlas['labels'].name", "names = atlas['lut']['name']")
    src = src.replace("np.product(", "np.prod(")   # numpy >= 2 removed np.product
    for k, v in smap.items(): src = src.replace(f'subject="{k}"', f'subject="{v}"')
    return src
summary = {}
for nb in sorted(EXT.glob("*.ipynb")):
    if a.only and nb.stem not in a.only: continue
    d = json.loads(nb.read_text())
    for c in d["cells"]:
        if c["cell_type"] == "code": c["source"] = fix("".join(c["source"])).splitlines(keepends=True); c["outputs"] = []; c["execution_count"] = None
    (out / nb.name).write_text(json.dumps(d, indent=1))
    r = subprocess.run([str(Path(sys.executable).parent / "jupyter"), "nbconvert", "--to", "notebook", "--execute", nb.name, "--output-dir", "../executed", "--allow-errors", f"--ExecutePreprocessor.timeout={a.timeout}"], cwd=out, capture_output=True, text=True)
    ex = json.loads((EXT.parent / "executed" / nb.name).read_text()) if (EXT.parent / "executed" / nb.name).exists() else {"cells": []}
    errs = [(i, o["ename"], o["evalue"][:100]) for i, c in enumerate(ex["cells"]) for o in c.get("outputs", []) if o.get("output_type") == "error"]
    summary[nb.stem] = errs; print(f"{nb.stem:20s} {'OK' if not errs else str(len(errs)) + ' failing cell(s)'}  (rc={r.returncode})")
    for e in errs[:4]: print("    cell", *e)
