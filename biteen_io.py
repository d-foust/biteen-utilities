"""
Methods for converting images to other formats.
"""
from glob import glob
from os import makedirs
from os.path import join, exists
from pathlib import Path

import h5py
import hdf5storage
import nd2
import numpy as np
import pandas as pd
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

def get_cellpose_labels(filename):
    """
    Get labels generated from _seg.npy file generated by Cellpose.
    
    Parameters
    ----------
    filename : str

    Returns
    -------
    2d array type int
    """
    return np.load(filename, allow_pickle=True).item()['masks']

def sl_to_df(sl_object):
    """
    Convert SMALL-LABS object read from .mat to pandas DataFrame.
    
    Parameters
    ----------
    sl_object : SMALL-LABS data object, a .mat file read using h5py

    Returns
    -------
    pd.DataFrame
    """
    if 'fits' in sl_object.keys():
        df = pd.DataFrame(data={key: sl_object['fits'][key][0,:] for key in sl_object['fits'].keys()})
    elif 'guesses' in sl_object.keys():
        df = pd.DataFrame(data={'frame': sl_object['guesses'][0,:],
                                'row': sl_object['guesses'][1,:],
                                'col': sl_object['guesses'][2,:]})
        if 'roinum' in sl_object.keys():
            df['roinum'] = sl_object['roinum'][0,:]

    if 'trk_filt' in sl_object.keys():
        df['trk_filt'] = sl_object['trk_filt'][0,:]

    if 'tracks' in sl_object.keys():
        df['tracked'] = np.isin(df['molid'], sl_object['tracks'][5,:])
        df['track_id'] = np.nan
        df.loc[df['tracked']==True, 'track_id'] = sl_object['tracks'][3,:]
        track_id_max = sl_object['tracks'][3,:].max()
        n_nottracked = (df['tracked']==False).sum()
        df.loc[df['tracked']==False, 'track_id'] = np.arange(track_id_max+1, track_id_max+n_nottracked+1)

    return df

def sl_to_df_batch(objs_sl: list):
    """

    Parameters
    ----------
    objs_sl : list (or other iterable)
        SMALL-LABS objects to be converted to pandas DataFrames.

    Returns
    -------
    list
        Each element is pd.DataFrame
    """
    dfs = []
    for obj in objs_sl:
        dfs.append(sl_to_df(obj))
    
    return dfs

def slfile_to_csv(file_sl, file_csv = None, ext = '.csv', folder_dest = None):
    """
    Reads SMALL-LABS .mat file and saves as .csv file.

    Parameters
    ----------
    file_sl : str
        .mat filename. Full path.
    file_csv : str, optional
        Name of new file where data is to be stored as .csv. Full path.
    ext : str, optional
        Bit of text added to end of new .csv name. Default is '.csv'.
    folder_dest : str, optional
        Destination folder. If none provided, .csv saved in origin folder.

    Returns
    -------
    None
    """
    if folder_dest is None:
        folder_dest = Path(file_sl).parent
    elif not exists(folder_dest):
        makedirs(folder_dest)

    if file_csv is None:
        file_csv = join(folder_dest, Path(file_sl).stem + ext)

    obj_sl = h5py.File(file_sl)
    df = sl_to_df(obj_sl)

    df.to_csv(file_csv)

def slfile_to_csv_batch(folder_sl, pattern_sl = '*_fits.mat', ext = '.csv', folder_dest = None):
    """
    Converts SMALL-LABS files to csv.
    
    Parameters
    ----------
    folder_sl : str
        Folder containing .mat files to be converted to .csv.
    pattern_sl : str, optional
        Pattern used to identify files to be converted.
    ext : str, optional
        Bit of text added to end of new .csv names. Default is '.csv'.
    folder_dest : str, optional
        Destination folder. If none provided, .csv saved in origin folder.

    Returns
    -------
    None
    """
    files_sl = glob(join(folder_sl, pattern_sl))

    [slfile_to_csv(file, ext=ext, folder_dest=folder_dest) for file in files_sl]

def df_to_sl(df, col_mapper = None):
    """
    Convert pandas DataFrame to SMALL-LABS .mat format.

    Parameters
    ----------
    df : pd.DataFrame
    col_mapper : dict
        Keys are columns in df, values are new names in SMALL-LABS format. Used if, for example,
        columns in df, 'x' and 'y', need to be re-labeled 'col' and 'row', respectively, 
        for use in NOBIAS.
        Example:
            col_mapper = {'x': 'col', 'y': 'row', 'n': 'track_id', 'rois': 'roinum'}
        
        Columns 'frame', 'row', 'col', 'track_id', and 'roinum' are required to generate tracks.

    Returns
    -------
    data_sl : dict
        Orgainized like SMALL-LABS data structure. 
        First level keys: 'fits', 'tracks'.
        Second level: 'fits' additional keys matching columns in df after renaming.
    """
    if col_mapper is not None:
        data = df.rename(columns=col_mapper) # makes a copy of df
    else:
        data = df

    data_sl = {}

    fits_dict = {c: data[c].values for c in data.columns} # may need to play with axes ordering
    data_sl['fits'] = fits_dict

    if set(('frame', 'row', 'col', 'track_id', 'roinum')).issubset(data.columns):
        tracks = np.zeros([len(data), 6])
        tracks[:,0] = data['frame'].values
        tracks[:,1] = data['row'].values
        tracks[:,2] = data['col'].values
        tracks[:,3] = data['track_id'].values
        tracks[:,4] = data['roinum'].values
        if 'molid' in data.columns:
            tracks[:,5] = data['molid'].values
        else:
            tracks[:,5] = data.index.values
        data_sl['tracks'] = tracks

    return data_sl

def save_sl_fits(data_sl, file_sl):
    """
    Save dict structured SMALL-LABS-like as .mat. Wrapper around hdf5storage.savemat(...).

    Parameters
    ----------
    data_sl : dict
    file_sl : name of file where data_sl is to be save. Should end with '.mat'.

    Returns
    -------
    None
    """
    hdf5storage.savemat(file_name = file_sl, mdict = data_sl, format = '7.3')

def sl_to_so(data_sl, pixel_size=0.049, t_frame=0.04):
    """
    Convert tracks in SMALL-LABS-style dict to numpy array format expected by Spot-On.

    Parameters
    ----------
    data_sl : dict
    pixel_size : float
        Spot-On expects coordinates in be in micron, so um/pixel required to convert.
    t_frame : float
        Time between frames in seconds.

    Returns
    -------
    so_tracks : np.array, dtype=[('xy', 'O'), ('TimeStamp', 'O'), ('Frame', 'O')]
        Spot-On formatted tracks
    """
    if 'tracks' in data_sl.keys():
        data_np = data_sl['tracks'][:].T # numpy array
        if data_np.ndim == 2: # False if SMALL-LABS didn't find any tracks
            xy = data_np[:,1:3] * pixel_size
            frames = (data_np[:,:1].T).astype('int')
            times = frames * t_frame
            track_ids = data_np[:,3]
            unique_track_ids = np.unique(track_ids)
            so_tracks = [(xy[track_ids==ti], times[track_ids==ti], frames[track_ids==ti]) for ti in unique_track_ids]
            so_tracks = np.array(so_tracks, dtype=[('xy', 'O'), ('TimeStamp', 'O'), ('Frame', 'O')])
        else:
            so_tracks = np.array([])
    else:
        so_tracks = np.array([])

    return so_tracks

def df_to_so(data_df, frame_col='frame', coord_cols=['x', 'y'], track_col='track_id', pixel_size=1, t_frame=0.04):
    """
    Convert tracks in pandas DataFrame to numpy array format expected by Spot-On.

    Parameters
    ----------
    data_df : pd.DataFrame
        Tracking data.
    frame_col : str
        Column containing frame number.
    coord_cols : List[str]
        Column names for 'x' and 'y' coordinates, respectively.
    track_col : str
    pixel_size : float
        For converting to um.
    t_frame : float
        Time between frames in seconds.

    Returns
    -------
    so_tracks : np.array, dtype=[('xy', 'O'), ('TimeStamp', 'O'), ('Frame', 'O')]
        Spot-On formatted tracks
    """
    frames = data_df[frame_col].values
    xy = data_df[coord_cols].values * pixel_size
    frames = (data_df[frame_col].values).astype('int')
    times = frames * t_frame
    track_ids = data_df[track_col].values
    unique_track_ids = np.unique(track_ids)
    so_tracks = [(xy[track_ids==ti], times[track_ids==ti], frames[track_ids==ti]) for ti in unique_track_ids]
    so_tracks = np.array(so_tracks, dtype=[('xy', 'O'), ('TimeStamp', 'O'), ('Frame', 'O')])

    return so_tracks