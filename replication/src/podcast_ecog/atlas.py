"""Atlas-based electrode regions (tutorial 05): nearest Destrieux (2009) label of every electrode."""
import numpy as np
from nilearn import datasets, image
from scipy.spatial import KDTree

def destrieux_labels(coords_mm):
    """Label of the nearest non-zero atlas voxel for each (x, y, z) in mm (MNI); returns a list of strings like 'G_temp_sup-Lateral' with the hemisphere tag stripped where present."""
    atlas = datasets.fetch_atlas_destrieux_2009(); img = image.load_img(atlas["maps"]); vol = img.get_fdata().astype(int)
    names = dict(zip(atlas["lut"]["index"], atlas["lut"]["name"]))   # nilearn >= 0.12: labels is a plain list, the look-up table is `lut`
    nz = np.nonzero(vol); xyz = np.vstack(image.coord_transform(*nz, img.affine)).T
    _, nn = KDTree(xyz).query(coords_mm, k=1); ids = vol[nz[0][nn], nz[1][nn], nz[2][nn]]
    return [names[i] for i in ids]
