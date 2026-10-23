"""Podcast ECoG electrodes (MNI152NLin2009aSym, all subjects) on the 2009aSym T1w template together with the LanA probability map warped into that space (lana_figs/matlab/atlas_to_2009asym.m).
Figure 1: orthogonal slices of LanA over the template with the electrodes in each slab; Figure 2: glass brain of all electrodes coloured by the LanA probability at the electrode (6 mm sphere mean).
  .venv/bin/python scripts/plot_electrodes_on_template.py [--maps DIR] [--out figures]"""
import argparse, os
from pathlib import Path
import numpy as np, pandas as pd, nibabel as nib, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from nilearn import plotting
from templateflow import api as tf
from podcast_ecog import bids_root, data as D, SUBJECTS
ap = argparse.ArgumentParser(); ap.add_argument("--maps", default=str(Path.home() / "repos/ieeg_lanA_correspondence/lana_figs/data/atlas_2009asym/maps")); ap.add_argument("--out", default="figures"); a = ap.parse_args()
out = Path(a.out); out.mkdir(exist_ok=True); root = bids_root()
t1 = nib.load(str(tf.get("MNI152NLin2009aSym", resolution=1, suffix="T1w", desc=None, extension="nii.gz"))); lana = nib.load(f"{a.maps}/w2009a_nlin6_lana_prob.nii")
el = pd.concat([D.electrodes(s, root=root).assign(subject=s) for s in SUBJECTS if (root / f"sub-{s}/ieeg/sub-{s}_space-MNI152NLin2009aSym_electrodes.tsv").exists()], ignore_index=True).dropna(subset=["x", "y", "z"]); xyz = el[["x", "y", "z"]].to_numpy(float)
vol = lana.get_fdata(); inv = np.linalg.inv(lana.affine); r = 3; g = np.arange(-r, r + 1); off = np.array([[i, j, k] for i in g for j in g for k in g if i * i + j * j + k * k <= r * r])
ijk = np.rint((inv @ np.c_[xyz, np.ones(len(xyz))].T).T[:, :3]).astype(int)
def sph(c):
    p = c + off; ok = (p >= 0).all(1) & (p < vol.shape).all(1); return vol[tuple(p[ok].T)].mean() if ok.any() else np.nan
el["lana"] = [sph(c) for c in ijk]; el.to_csv(out / "podcast_electrodes_lana_2009aSym.csv", index=False)
print(f"{len(el)} electrodes, {el.subject.nunique()} subjects; LanA at electrodes: mean {el.lana.mean():.3f}, {100 * (el.lana > 0.3).mean():.1f}% > 0.3")
# 1) slices: LanA over the template + electrodes within 4 mm of each slice
fig = plt.figure(figsize=(11, 3.6)); 
for k, (mode, cut, lab) in enumerate((("x", -54, "x = -54"), ("y", -20, "y = -20"), ("z", 6, "z = 6"))):
    ax = fig.add_subplot(1, 3, k + 1); d = plotting.plot_anat(t1, display_mode=mode, cut_coords=[cut], axes=ax, annotate=False, draw_cross=False, colorbar=False, title=lab)
    d.add_overlay(lana, cmap="YlOrRd", threshold=0.05, vmin=0.05, vmax=0.5, alpha=0.85)
    ax_i = "xyz".index(mode); near = np.abs(xyz[:, ax_i] - cut) <= 4
    if near.any(): d.add_markers(xyz[near], marker_color="#1f77b4", marker_size=8)
fig.suptitle("Podcast ECoG electrodes (blue; within 4 mm of each slice) and LanA probability (warped to MNI152NLin2009aSym)", fontsize=9); fig.savefig(out / "electrodes_lana_slices_2009aSym.png", dpi=200, bbox_inches="tight")
# 2) glass brain coloured by LanA
o = np.argsort(el.lana.fillna(0).to_numpy()); fig2 = plt.figure(figsize=(9, 3)); plotting.plot_markers(el.lana.fillna(0).to_numpy()[o], xyz[o], node_size=8, display_mode="lzr", node_cmap="YlOrRd", node_vmin=0, node_vmax=0.3, colorbar=True, figure=fig2, title="Podcast electrodes coloured by LanA probability at the electrode")
fig2.savefig(out / "electrodes_glassbrain_lana_2009aSym.png", dpi=200, bbox_inches="tight"); print("saved to", out)
