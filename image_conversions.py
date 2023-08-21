"""
Methods for converting images to other formats
"""
from glob import glob
from os.path import join
from pathlib import Path

import numpy as np
from scipy.io import savemat

import nd2
import tifffile

def nd2_to_tif(file_nd2: str, file_tif: str = None, ext: str = '.tif', folder_dest: str = None):
    """
    Converts an nd2 file (Nikon) to a tif
    ---
    Inputs
    file_nd2 : Absolute path to nd2 file.
    file_tif : Name of .tif to be created.
                   If None, has same name as nd2 with .tif extension
    folder_dest : Destination folder.
                  If None, tif saved to same folder as nd2
    """
    if folder_dest is None:
        folder_dest == Path(file_nd2).parent
    if file_tif is None:
        file_tif == join(folder_dest, Path(file_nd2).stem + ext)

    image = nd2.imread(file_nd2)
    tifffile.imsave(file_tif, data=image)

def nd2_to_tif_batch(folder_nd2: str, pattern_nd2: str = '*.nd2', ext: str = '.tif', folder_dest: str = None):
    """

    """
    files_nd2 = glob(join(folder_nd2, pattern_nd2))

    for file in files_nd2:
        nd2_to_tif(file, ext=ext, folder_dest=folder_dest)

def nd2_to_npy(file_nd2: str, file_npy: str = None, ext: str = '.npy', folder_dest: str = None):
    """
    """
    if folder_dest is None:
        folder_dest == Path(file_nd2).parent
    if file_npy is None:
        file_npy == join(folder_dest, Path(file_nd2).stem + ext)

    image = nd2.imread(file_nd2)
    np.save(file_npy, arr=image)

def nd2_to_npy_batch(folder_nd2: str, pattern_nd2: str = '*.nd2', ext: str = '.npy', folder_dest: str = None):
    """
    """
    files_nd2 = glob(join(folder_nd2, pattern_nd2))

    for file in files_nd2:
        nd2_to_npy(file, ext=ext, folder_dest=folder_dest)

def cellpose_to_mat(file_cp: str,
                    file_mat: str = None,
                    ext_cp: str = '_seg.npy',
                    ext_mat: str = '_PhaseMask.mat',
                    folder_dest: str = None):
    """
    """
    if folder_dest is None:
        folder_dest = Path(file_cp).parent
    if file_mat is None:
        stem_mat = Path(file_cp).split(ext_cp)[0]
        file_mat = join(folder_dest, stem_mat + ext_mat)

    masks = np.load(file_cp, allow_pickle=True).item()['masks']
    savemat(file_mat, {'PhaseMask': masks})

def cellpose_to_mat_batch(folder_cp: str,
                          pattern_cp: str = '*_seg.npy',
                          ext_cp: str = '_seg.npy',
                          ext_mat: str = '_PhaseMask.mat'):
    """
    """
    files_cp = glob(join(folder_cp, pattern_cp))

    for file in files_cp:
        cellpose_to_mat(file, ext_cp=ext_cp, ext_mat=ext_mat)