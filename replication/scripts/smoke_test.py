"""End-to-end check of the data and loaders: print a dataset summary, then run the tutorial-04 word-onset encoding for one subject and report the best electrodes.
   .venv/bin/python scripts/smoke_test.py [--subject 03] [--n-channels 20]"""
import argparse, numpy as np
from podcast_ecog import bids_root, data as D
from podcast_ecog.encoding import encode_subject
ap = argparse.ArgumentParser(); ap.add_argument("--subject", default="03"); ap.add_argument("--n-channels", type=int, default=20); a = ap.parse_args()
print("dataset root:", bids_root()); print(D.dataset_summary().to_string(index=False))
picks = D.load_highgamma(a.subject).ch_names[:a.n_channels]; r, chs, t = encode_subject(a.subject, picks=picks); m = r.mean(0); best = m.max(1).argsort()[::-1][:5]
print(f"sub-{a.subject}: {len(chs)} electrodes, lags {t[0]:.2f}..{t[-1]:.2f} s")
for i in best: print(f"  {chs[i]:8s} peak r = {m[i].max():.3f} at {t[m[i].argmax()]:+.2f} s")
