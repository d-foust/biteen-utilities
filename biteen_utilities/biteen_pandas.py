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

def locs_to_steps(locs_df, frame_col='frame', coord_cols=('x', 'y'), track_col='track_id'):
    """
    From locs_df calculate data for individual steps.

    Parameters
    ----------
    locs_df : pd.DataFrame
    frame_col : str, default 'frame'
    coord_cols : tuple, default ('x', 'y')
    track_col : str, default 'track_id'

    Returns
    -------
    steps_df : pd.DataFrame
        DataFrame with columns: frame0, frame1, x0, x1, y0, y1, xmid, ymid, d, gap
        frame0, x0, y0 are start coordinates for step each step.
        frame1, x1, y2 are end coordinates.
        xmid, ymid are the midpoint.
        d is the length.
        gap is the number of frames between the start and end.
    """
    xcol, ycol = coord_cols

    locs_sorted = locs_df.sort_values([track_col, frame_col], axis=0, ascending=True)

    frames = locs_sorted[frame_col].values
    x, y = locs_sorted[xcol].values, locs_sorted[ycol].values
    track_id = locs_sorted[track_col].values

    track_filt = track_id[:-1] == track_id[1:] # to verify 

    steps_df = pd.DataFrame(data={'frame0': frames[:-1][track_filt], 'frame1': frames[1:][track_filt],
                                  'x0': x[:-1][track_filt], 'x1': x[1:][track_filt],
                                  'y0': y[:-1][track_filt], 'y1': y[1:][track_filt]})

    steps_df['xmid'] = (steps_df['x0'] + steps_df['x1']) / 2
    steps_df['ymid'] = (steps_df['y0'] + steps_df['y1']) / 2
    steps_df['d'] = np.sqrt((steps_df['x0'] - steps_df['x1'])**2 + (steps_df['y0'] - steps_df['y1'])**2)
    steps_df['gap'] = steps_df['frame1'] - steps_df['frame0']

    return steps_df

def median_step_size(locs_df, frame_col='frame', coord_cols=['x', 'y'], track_col='track_id'):
    """
    Finds median step size for each unique track in locs_df.

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