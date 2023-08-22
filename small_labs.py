"""
Methods for converting to and from SMALL-LABS formats
"""

from glob import glob
from os import makedirs
from os.path import join, exists

import h5py
import hdf5storage
import numpy as np
import pandas as pd
from pathlib import Path

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
        .mat filename.
    file_csv : str, optional
        Name of new file where data is to be stored as .csv
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
