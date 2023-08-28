"""

"""
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.measure import find_contours, regionprops

def plot_trajectories(locs_df,
                      track_data = None,
                      track_col = 'track_id',
                      track_data_bins = np.array([[-np.inf, np.inf]]),
                      track_data_colors = None,
                      order = 'forward',
                      scale = 1,
                      labels = None,
                      image = None,
                      subsample = None,
                      line_props = {},
                      separate = False,
                      crop = False,
                      figure_props = {},
                      scalebar_props = None):
    """
    Plot single-molecule trajectories.

    Parameters
    ----------
    locs : pd.DataFrame
        Localization data. Required columns: 'x', 'y', 'track_id'.
    track_data : pd.DataFrame, optional
        Columns: 'track_id' + other values calculated for each track. Used to filter, choose color.
    track_data_bins : array_like
        Nx2 array where each row defines a half open interval for categorizing 
    track_data_colors : iterable
    order : str
        'forward' or 'reverse'.
        Determines which order to plot binned track data.
    scale : float, default 1
        Used to convert localizations to units of pixels if not already.
    labels : 2d int array
        Segmentation data for cell, nuclei, etc.
    subsample : int, default None
        Number of tracks to plot. If None, all tracks are plotted.
    line_props : dict, optional
    separate : bool, default False
    crop : bool, default False
    figure_props : dict, optional
    scalebar_props : dict, optional

    Returns
    -------
    fig
        Matplotlib figure handle.
    ax
        Matplotlib axis handle(s).
    """
    if track_data is None:
        track_ids = np.unique(locs_df['track_id'])
        track_data = pd.DataFrame(data={'track_id': np.unique(track_ids)})

    if subsample is not None:
        idx_sub = np.random.choice(track_data.index, size=subsample, replace=False)
        track_data = track_data.loc[idx_sub].reset_index()

    if labels is not None:
        contours = get_contours(labels)
    else:
        contours = []

    if image is None and labels is None:
        colmax = int(np.max(locs_df['x']*scale)) + 1
        rowmax = int(np.max(locs_df['y']*scale)) + 1
        image = np.zeros([rowmax, colmax])
    elif image is None:
        image = np.zeros(labels.shape)

    n_bins = track_data_bins.shape[0]

    if track_data_colors is None:
        track_data_colors = ['xkcd:hot pink']*n_bins
    n_colors = len(track_data_colors)

    if separate == True:
        fig, ax = plt.subplots(n_bins, 1, **figure_props)
        if n_bins == 1: ax = [ax]
        for i_ax, (l, h) in enumerate(track_data_bins):
            
            ax[i_ax].imshow(image, cmap='binary_r')
            ax[i_ax].axis('off')

            for contour in contours:
                ax[i_ax].plot(contour[0][:,1], contour[0][:,0],
                            lw=1,
                            alpha=0.5,
                            color='xkcd:gray') # future: contour props
            
            filt = (track_data[track_col] > l) & (track_data[track_col] <= h)
            for ti in track_data['track_id'][filt]:
                loc_filt = locs_df['track_id'] == ti
                x = locs_df['x'][loc_filt]
                y = locs_df['y'][loc_filt]
                ax[i_ax].plot(x*scale, y*scale, color=track_data_colors[i_ax%n_colors], **line_props)

            if crop == True:
                crop_to_cells(ax[i_ax], labels)

            if scalebar_props is not None:
                plot_scalebar(ax[i_ax], scalebar_props)

    elif separate == False:
        fig, ax = plt.subplots(1, 1, **figure_props)
        
        ax.imshow(image, cmap='binary_r')
        ax.axis('off')

        for contour in contours:
            ax.plot(contour[0][:,1], contour[0][:,0], lw=1, alpha=0.5, color='xkcd:gray')

        if order == 'forward':
            i_bin = np.arange(n_bins, dtype=int)
        elif order == 'reverse':
            i_bin = np.arange(n_bins-1, -1, -1, dtype=int)

        for i in i_bin:
            l, h = track_data_bins[i]
            filt = (track_data[track_col] > l) & (track_data[track_col] <= h)
            for ti in track_data['track_id'][filt]:
                loc_filt = locs_df['track_id'] == ti
                x = locs_df['x'][loc_filt]
                y = locs_df['y'][loc_filt]
                ax.plot(x*scale, y*scale, color=track_data_colors[i%n_colors], **line_props)
                
        if crop == True:
            crop_to_cells(ax, labels)

        if scalebar_props is not None:
            plot_scalebar(ax, scalebar_props)

    return fig, ax

def get_contours(rois):
    """
    rois : 2d integer array. 0 for background pixels.
    """
    num_rois = rois.max()
    contours = []
    for r in range(1, num_rois+1):
        roi = rois == r
        contour = find_contours(roi, level=0.01)
        contours.append(contour)
        
    return contours

def plot_scalebar(ax, scalebar_props):
    
    xmin, xmax = ax.get_xlim()
    ymax, ymin = ax.get_ylim()
    
    if scalebar_props['loc'] == 'upper_left':
        x = xmin + scalebar_props['buffer']
        y = ymin + scalebar_props['buffer']
    elif scalebar_props['loc'] == 'lower_left':
        x = xmin + scalebar_props['buffer']
        y = ymax - scalebar_props['buffer'] - scalebar_props['height']
    elif scalebar_props['loc'] == 'upper_right':
        x = xmax - scalebar_props['buffer'] - scalebar_props['length']
        y = ymin + scalebar_props['buffer']
    elif scalebar_props['loc'] == 'lower_right':
        x = xmax - scalebar_props['buffer'] - scalebar_props['length']
        y = ymax - scalebar_props['buffer'] - scalebar_props['height']
    
    ax.add_patch(Rectangle((x, y), scalebar_props['length'], scalebar_props['height'],
                 edgecolor=scalebar_props['edgecolor'],
                 facecolor=scalebar_props['facecolor']))
    
def crop_to_cells(ax, cell_labels, crop_buffer=5):
    """
    """
    cell_bool = (cell_labels > 0).astype('int')
    rowmin, colmin, rowmax, colmax = regionprops(cell_bool)[0]['bbox']
    
    xmin, xmax = colmin-crop_buffer-0.5, colmax+crop_buffer+0.5
    ymin, ymax = rowmin-crop_buffer-0.5, rowmax+crop_buffer+0.5
    
    ax.set_xlim(left=xmin, right=xmax)
    ax.set_ylim(bottom=ymax, top=ymin)