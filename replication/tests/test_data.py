"""Smoke tests on the real dataset (skipped when it is not found). Uses subject 02, the smallest complete derivative."""
import numpy as np, pytest
from podcast_ecog import bids_root
from podcast_ecog import data as D

try: bids_root()
except FileNotFoundError: pytest.skip("ds005574 not available", allow_module_level=True)

SUB = "02"
CH = D.load_highgamma(SUB).ch_names[:20]   # first 20 channels keep the tests fast

def test_transcript_and_embeddings():
    tr = D.transcript(); X = D.embeddings(layer=24)
    assert len(tr) == X.shape[0] and X.shape[1] == 1600          # gpt2-xl hidden size
    emb, words = D.word_embeddings(layer=24)
    assert emb.shape[0] == len(words) > 4000 and {"word", "start", "end"} <= set(words.columns)
    assert (words.start.diff().dropna() < 0).mean() < 0.01       # onsets are ordered apart from a few (19) out-of-order words in the transcript

def test_highgamma_and_electrodes():
    raw = D.load_highgamma(SUB)
    assert raw.info["sfreq"] == 512 and raw.times[-1] / 60 > 25   # ~30 min at 512 Hz
    xyz = D.coords_mm(raw); assert xyz.shape == (len(raw.ch_names), 3) and np.isfinite(xyz).any()
    el = D.electrodes(SUB); ch = D.channels(SUB); assert len(el) > 0 and len(ch) >= len(raw.ch_names)

def test_word_epochs():
    emb, words = D.word_embeddings(); raw = D.load_highgamma(SUB, picks=CH, preload=True)
    ep = D.word_epochs(raw, words, tmin=-0.5, tmax=0.5, sfreq=32)
    assert ep.get_data().shape[0] == len(ep.selection) <= len(words) and ep.get_data().shape[1] == len(raw.ch_names)

def test_encoding_runs():
    from podcast_ecog.encoding import encode_subject
    r, chs, t = encode_subject(SUB, picks=CH, tmin=-0.5, tmax=0.5, sfreq=32)
    assert r.shape[1] == len(chs) and r.shape[2] == len(t) and np.isfinite(r).all()
    assert r.mean(0).max() > 0.05                                    # some electrode/lag is predicted above chance
