"""
Methods for converting images to other formats
"""
from glob import glob
from os import makedirs
from os.path import join, exists
from pathlib import Path

import numpy as np
from scipy.io import savemat

import nd2
import tifffile

def nd2_to_tif(file_nd2: str, file_tif: str = None, ext: str = '.tif', folder_dest: str = None):
    """
    Converts an nd2 file (Nikon) to a tif.
    ---
    Inputs
    file_nd2 : Absolute path to nd2 file.
    file_tif : Name of .tif to be created.
               If None, has same name as nd2 with .tif extension
    ext : extension.
          Appended to end of file name for saving. Default: '.tif'
    folder_dest : Destination folder.
                  If None, tif saved in same folder as nd2
    """
    if folder_dest is None:
        folder_dest = Path(file_nd2).parent
    elif not exists(folder_dest):
        makedirs(folder_dest)

    if file_tif is None:
        file_tif = join(folder_dest, Path(file_nd2).stem + ext)

    image = nd2.imread(file_nd2)
    tifffile.imsave(file_tif, data=image)

def nd2_to_tif_batch(folder_nd2: str, pattern_nd2: str = '*.nd2', ext: str = '.tif', folder_dest: str = None):
    """
    Convert .nd2 files to .tif files.
    ---
    Inputs
    folder_nd2 : Folder containing .nd2 files.
    pattern_nd2 : Pattern used to find .nd2 file. Default: '*.nd2'.
    ext : String append to file name when saving .tif.
    folder_dest : Folder where .tif files saved. If none is provided, .tif files are saved to same folder
                  as .nd2 files.
    """
    files_nd2 = glob(join(folder_nd2, pattern_nd2))

    for file in files_nd2:
        nd2_to_tif(file, ext=ext, folder_dest=folder_dest)

def nd2_to_npy(file_nd2: str, file_npy: str = None, ext: str = '.npy', folder_dest: str = None):
    """
    Converts an nd2 file (Nikon) to a .npy (numpy array).
    ---
    Inputs
    file_nd2 : Absolute path to nd2 file.
    file_npy : Name of .tif to be created.
               If None, has same name as nd2 plus ext.
    ext : extension.
          Appended to end of file name for saving. Default: '.npy'
    folder_dest : Destination folder.
                  If None, .npy saved in same folder as nd2
    """
    if folder_dest is None:
        folder_dest = Path(file_nd2).parent
    elif not exists(folder_dest):
        makedirs(folder_dest)

    if file_npy is None:
        file_npy = join(folder_dest, Path(file_nd2).stem + ext)

    image = nd2.imread(file_nd2)
    np.save(file_npy, arr=image)

def nd2_to_npy_batch(folder_nd2: str, pattern_nd2: str = '*.nd2', ext: str = '.npy', folder_dest: str = None):
    """
    Converts .nd2 files to .npy files (numpy arrays).
    ---
    Inputs
    folder_nd2 : Folder containing .nd2 files.
    patter_nd2 : Pattern used to find .nd2 files. Default: '*.nd2'.
    ext : 
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
    Converts .npy file in cellpose format to .mat file that is readable by SMALL-LABS.
    ---
    Inputs
    file_cp     : .npy file created by cellpose
    file_mat    : Name of .mat to be created.
                  If None, has same name as cellpose file with '_PhaseMask.mat' appended.
    ext_cp      : Cellpose extension. Gets chopped off before saving .mat.
    ext_mat     : Extension.
                  Appended to end of file name for saving. Default: '_PhaseMask.mat'
    folder_dest : Destination folder.
                  If None, .mat saved in same folder as cellpose file.
    """
    if folder_dest is None:
        folder_dest = Path(file_cp).parent
    elif not exists(folder_dest):
        makedirs(folder_dest)

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
    Converts cellpose style .npy files to .mat files readable by SMALL-LABS.
    ---
    Inputs
    folder_cp   :   Folder containing cellpose .npy files.
    patter_cp   :   Pattern used to find cellpose output files.
    ext_cp      :   Part of cellpose file names to be removed.
    ext_mat     :   Added to end of filename (after ext_cp removed).
    """
    files_cp = glob(join(folder_cp, pattern_cp))

    for file in files_cp:
        cellpose_to_mat(file, ext_cp=ext_cp, ext_mat=ext_mat)