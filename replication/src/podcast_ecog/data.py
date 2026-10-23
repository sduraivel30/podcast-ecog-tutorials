"""Loaders for the Podcast ECoG dataset: electrophysiology (MNE), electrodes / channels, transcript, word embeddings and the word-aligned epochs of the tutorials."""
import json
import h5py, mne, numpy as np, pandas as pd
from mne_bids import BIDSPath, read_raw_bids
from .paths import bids_root, derivative_path, SUBJECTS

FEATURE_SETS = ("gpt2-xl", "en_core_web_lg", "phonetic", "spectral", "syntactic", "whisper-medium")

def participants(root=None) -> pd.DataFrame:
    return pd.read_csv(bids_root(root) / "participants.tsv", sep="\t")

def load_highgamma(subject, picks=None, preload=False, root=None, desc="highgamma"):
    """MNE Raw of the derivative (default the 70-200 Hz high-gamma envelope, 512 Hz, ~30 min). picks: list of channel names or an MNE regexp (e.g. 'LG[AB]*')."""
    raw = mne.io.read_raw_fif(derivative_path(subject, desc, root), preload=preload, verbose=False)
    if picks is not None:
        names = [picks] if isinstance(picks, str) and "*" not in picks else picks
        raw.pick(mne.pick_channels_regexp(raw.ch_names, picks) if isinstance(picks, str) else names)
    return raw

def load_raw_bids(subject, root=None, preload=False):
    """Raw (broadband) BIDS recording sub-XX/ieeg/sub-XX_task-podcast_ieeg.edf with channels.tsv / electrodes.tsv applied (mne-bids)."""
    bp = BIDSPath(root=bids_root(root), subject=subject, task="podcast", datatype="ieeg", suffix="ieeg", extension=".edf")
    return read_raw_bids(bp, verbose=False).load_data() if preload else read_raw_bids(bp, verbose=False)

def channels(subject, root=None) -> pd.DataFrame:
    return pd.read_csv(bids_root(root) / f"sub-{subject}" / "ieeg" / f"sub-{subject}_task-podcast_channels.tsv", sep="\t")

def electrodes(subject, space="MNI152NLin2009aSym", root=None) -> pd.DataFrame:
    """Electrode coordinates (BIDS electrodes.tsv); space 'MNI152NLin2009aSym' (template) or 'Other' (native)."""
    return pd.read_csv(bids_root(root) / f"sub-{subject}" / "ieeg" / f"sub-{subject}_space-{space}_electrodes.tsv", sep="\t")

def coords_mm(raw) -> np.ndarray:
    """Electrode xyz (mm) of the channels of an MNE Raw (channel locations are stored in metres)."""
    ch = {c["ch_name"]: c["loc"][:3] for c in raw.info["chs"]}
    return np.vstack([ch[n] for n in raw.ch_names]) * 1000

def transcript(model="gpt2-xl", root=None) -> pd.DataFrame:
    """Token-level transcript of a feature set (stimuli/<model>/transcript.tsv: word, start, end, word_idx, ...)."""
    return pd.read_csv(bids_root(root) / "stimuli" / model / "transcript.tsv", sep="\t", index_col=0)

def word_transcript(root=None) -> pd.DataFrame:
    """The plain word-aligned transcript (stimuli/podcast_transcript.csv)."""
    return pd.read_csv(bids_root(root) / "stimuli" / "podcast_transcript.csv")

def embeddings(model="gpt2-xl", layer=24, root=None):
    """(token x dim) feature matrix; for gpt2-xl `layer` selects `layer-<n>` (0-48), other feature sets are a single matrix."""
    with h5py.File(bids_root(root) / "stimuli" / model / "features.hdf5", "r") as f:
        key = f"layer-{layer}" if f"layer-{layer}" in f else list(f.keys())[0]
        return f[key][...]

def word_embeddings(model="gpt2-xl", layer=24, root=None):
    """Sub-token embeddings averaged within each word -> (words x dim) array and the word table (word, start, end) indexed by word_idx (tutorial 04)."""
    tr = transcript(model, root); X = embeddings(model, layer, root)
    emb = np.stack([X[g.index.to_numpy()].mean(0) for _, g in tr.groupby("word_idx")])
    words = tr.groupby("word_idx").agg(dict(word="first", start="first", end="last"))
    return emb, words

def word_epochs(raw, words, tmin=-2.0, tmax=2.0, sfreq=32, picks=None):
    """Word-onset epochs of an MNE Raw (tutorial 04): events at each word start, merged repeats, resampled to `sfreq`. Returns the Epochs; `epochs.selection` indexes the kept words."""
    if picks is not None: raw = raw.copy().pick(mne.pick_channels_regexp(raw.ch_names, picks) if isinstance(picks, str) else picks)
    ev = np.zeros((len(words), 3), dtype=int); ev[:, 0] = (words.start.values * raw.info["sfreq"]).astype(int)
    ep = mne.Epochs(raw, ev, tmin=tmin, tmax=tmax, baseline=None, proj=False, event_id=None, preload=True, event_repeated="merge", verbose=False)
    return ep.resample(sfreq=sfreq, npad="auto", method="fft", window="hamming", verbose=False) if sfreq else ep

def dataset_summary(root=None) -> pd.DataFrame:
    """One row per subject: channels (high-gamma derivative), duration, sampling rate, bad channels (BIDS channels.tsv)."""
    rows = []
    for s in SUBJECTS:
        try:
            raw = load_highgamma(s, root=root); ch = channels(s, root)
            rows.append(dict(subject=s, n_channels=len(raw.ch_names), sfreq=raw.info["sfreq"], duration_min=raw.times[-1] / 60, n_bad=int((ch.status == "bad").sum()) if "status" in ch else np.nan))
        except FileNotFoundError: rows.append(dict(subject=s))
    return pd.DataFrame(rows)
