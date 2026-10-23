"""Where the dataset lives. Resolution order: the `root` argument, $PODCAST_BIDS_ROOT, ~/Documents/podcast_ecog, <repo>/data/ds005574."""
import os
from pathlib import Path

SUBJECTS = [f"{i:02d}" for i in range(1, 10)]
_CANDIDATES = [Path.home() / "Documents" / "podcast_ecog", Path(__file__).resolve().parents[2] / "data" / "ds005574"]

def bids_root(root=None) -> Path:
    cands = [Path(root)] if root else ([Path(os.environ["PODCAST_BIDS_ROOT"])] if os.environ.get("PODCAST_BIDS_ROOT") else []) + _CANDIDATES
    for c in cands:
        if (c / "dataset_description.json").exists(): return c
    raise FileNotFoundError("ds005574 not found; set PODCAST_BIDS_ROOT or pass root=. Tried: " + ", ".join(map(str, cands)))

def derivative_path(subject, desc="highgamma", root=None) -> Path:
    """derivatives/ecogprep/sub-XX/ieeg/sub-XX_task-podcast[_desc-<desc>]_ieeg.fif ('highgamma' = 70-200 Hz envelope at 512 Hz; None = minimally preprocessed broadband)."""
    d = f"_desc-{desc}" if desc else ""
    return bids_root(root) / "derivatives" / "ecogprep" / f"sub-{subject}" / "ieeg" / f"sub-{subject}_task-podcast{d}_ieeg.fif"
