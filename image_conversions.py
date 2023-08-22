"""
Methods for converting images to other formats.
"""
from glob import glob
from os import makedirs
from os.path import join, exists
from pathlib import Path

import nd2
import numpy as np
from scipy.io import savemat
import tifffile

def nd2_to_tif(file_nd2, file_tif = None, ext = '.tif', folder_dest = None):
    """
    Converts an nd2 file (Nikon) to a tif.

    Parameters
    ----------
    file_nd2 : str
        Absolute path to nd2 file.
    file_tif : str, optional
        Name of .tif to be created. If None, has same name as nd2 with .tif extension.
    ext : str, optional
        Extension. Appended to end of file name for saving. Default: '.tif'
    folder_dest : str, optional
        Destination folder. If None, tif saved in same folder as nd2

    Returns
    -------
    None
    """
    if folder_dest is None:
        folder_dest = Path(file_nd2).parent
    elif not exists(folder_dest):
        makedirs(folder_dest)

    if file_tif is None:
        file_tif = join(folder_dest, Path(file_nd2).stem + ext)

    image = nd2.imread(file_nd2)
    tifffile.imsave(file_tif, data=image)

def nd2_to_tif_batch(folder_nd2, pattern_nd2 = '*.nd2', ext = '.tif', folder_dest = None):
    """
    Convert .nd2 files to .tif files.

    Parameters
    ----------
    folder_nd2 : str
        Path to folder containing .nd2 files.
    pattern_nd2 : str, optional
        Pattern used to find .nd2 file. Default: '*.nd2'.
    ext : str, optional
        String append to file name when saving .tif.
    folder_dest : str, optional
        Folder where .tif files saved. If none is provided, .tif files are saved to same folder
        as .nd2 files.

    Returns
    -------
    None
    """
    files_nd2 = glob(join(folder_nd2, pattern_nd2))

    for file in files_nd2:
        nd2_to_tif(file, ext=ext, folder_dest=folder_dest)

def nd2_to_npy(file_nd2, file_npy = None, ext = '.npy', folder_dest = None):
    """
    Converts an nd2 file (Nikon) to a .npy (numpy array).
    
    Parameters
    ----------
    file_nd2 : str
        Absolute path to nd2 file.
    file_npy : str, optional
        Name of .tif to be created. If None, has same name as nd2 plus ext.
    ext : str, optional
        Extension. Appended to end of file name for saving. Default: '.npy'
    folder_dest : str, optional
        Destination folder. If None, .npy saved in same folder as nd2.

    Returns
    -------
    None
    """
    if folder_dest is None:
        folder_dest = Path(file_nd2).parent
    elif not exists(folder_dest):
        makedirs(folder_dest)

    if file_npy is None:
        file_npy = join(folder_dest, Path(file_nd2).stem + ext)

    image = nd2.imread(file_nd2)
    np.save(file_npy, arr=image)

def nd2_to_npy_batch(folder_nd2, pattern_nd2 = '*.nd2', ext = '.npy', folder_dest = None):
    """
    Converts .nd2 files to .npy files (numpy arrays).

    Parameters
    ----------
    folder_nd2 : str
        Folder containing .nd2 files.
    patter_nd2 : str, optional
        Pattern used to find .nd2 files. Default: '*.nd2'.
    ext : str, optional
        Extension. Appended to end of file name for saving. Default: '.npy'.
    folder_dest : str, optional
        Destination folder. If None, .npy saved in same folder as nd2.

    Returns
    -------
    None
    """
    files_nd2 = glob(join(folder_nd2, pattern_nd2))

    for file in files_nd2:
        nd2_to_npy(file, ext=ext, folder_dest=folder_dest)

def cellpose_to_mat(file_cp, file_mat = None, ext_cp = '_seg.npy', ext_mat = '_PhaseMask.mat', folder_dest = None):
    """
    Converts .npy file in cellpose format to .mat file that is readable by SMALL-LABS.

    Parameters
    ----------
    file_cp : str
        .npy file created by cellpose
    file_mat : str, optional
        Name of .mat to be created. If None, has same name as cellpose file with '_PhaseMask.mat' appended.
    ext_cp : str, optional
        Cellpose extension. Gets chopped off before saving .mat.
    ext_mat : str, optional
        Extension. Appended to end of file name for saving. Default: '_PhaseMask.mat'
    folder_dest : str, optional
        Destination folder. If None, .mat saved in same folder as cellpose file.

    Returns
    -------
    None
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

def cellpose_to_mat_batch(folder_cp, pattern_cp = '*_seg.npy', ext_cp = '_seg.npy', ext_mat = '_PhaseMask.mat'):
    """
    Converts cellpose style .npy files to .mat files readable by SMALL-LABS.

    Parameters
    ----------
    folder_cp : str
        Folder containing cellpose .npy files.
    patter_cp : str, optional
        Pattern used to find cellpose output files.
    ext_cp : str, optional
        Part of cellpose file names to be removed.
    ext_mat : str, optional
        Added to end of filename (after ext_cp removed).

    Returns
    -------
    None
    """
    files_cp = glob(join(folder_cp, pattern_cp))

    [cellpose_to_mat(file, ext_cp=ext_cp, ext_mat=ext_mat) for file in files_cp]