"""
Operations for manipulating pandas DataFrames containing single-molecule localization data.
"""

import numpy as np
import pandas as pd

def filter_by_nlocs(locs_df, min_locs=2, max_locs=np.inf, track_col='track_id'):
    """
    Remove data for tracks with fewer localizations than min_locs and greater than max_locs.

    Parameters
    ----------
    locs_df : pd.DataFrame
    min_locs : int, default 2
    max_locs : int, default np.inf
    track_col : str, default 'track_id'
        Name of column that identifies which track a localization belongs to.

    Returns
    -------
    locs_filtered : pd.DataFrame
    """
    locs_ngroups = locs_df.groupby(track_col)
    locs_filtered = locs_ngroups.filter(lambda x: (x[track_col].count() >= min_locs) & (x[track_col].count() <= max_locs))

    return locs_filtered.reset_index()

def median_step_size(locs_df, frame_col='frame', coord_cols=['x', 'y'], track_col='track_id'):
    """
    Finds median step size for each unique track in locs_df

    Parameters
    ----------
    locs_df : pd.DataFrame
    frame_col : str
    coord_cols : iterabale[str]
    track_col : str, default 'track_id'
        Name of column that identifies which track a localization belongs to.

    Returns
    -------
    d_med : np.ndarray
    track_ids : np.ndarray
    """
    track_ids = np.unique(locs_df['track_id'].values)
    frames = locs_df[frame_col].values
    x = locs_df[coord_cols[0]].values
    y = locs_df[coord_cols[1]].values

    d_med = np.zeros(len(track_ids))
    for i, track_id in enumerate(track_ids):
        track_filt = locs_df[track_col].values == track_id
        if track_filt.sum() > 1:
            frames_track = frames[track_filt]
            x_track = x[track_filt]
            y_track = y[track_filt]
            d = np.sqrt((x_track[1:] - x_track[:-1])**2 + (y_track[1:] - y_track[:-1])**2)
            d = d[frames_track[1:] - frames_track[:-1] == 1]
            d_med[i] = np.median(d)
        else:
            d_med[i] = np.nan

    return pd.DataFrame(data={track_col: track_ids, 'd_med': d_med})