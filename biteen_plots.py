"""

"""
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.measure import find_contours, regionprops

def add_scalebar(ax, scalebar_props):
    """
    Add a scalebar to image displayed on ax.

    Parameters
    ----------
    ax : matplotlib.Axes
    scalebar_props : dict
        Contains instructions for drawing scalebar. 
        Required keys: 'loc', 'buffer', 'height', 'length'
            'loc' : must be 'upper_left', 'lower_left', 'upper_rigth', 'lower_right'
            'buffer' : distance in pixels from nearest corner of scalebar to edge of image
            'height' : in pixels
            'width' : in pixels
            'edgecolor' : 
            'facecolor' : 

    """
    
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
    
def crop_to_labels(ax, labels, crop_buffer=5):
    """
    Set limits of ax so that only bounding box of labels is shown with crop_buffer number of
    pixels added to border.

    Parameters
    ----------
    ax : matplotlib axis handle
    labels : np.array, dtype=int
    crop_buffer : int
        Extra pixels to leave around bounding box.

    Returns
    -------
    None
    """
    nrows_init, ncols_init = labels.shape

    labels_bool = (labels > 0).astype('int')
    rowmin, colmin, rowmax, colmax = regionprops(labels_bool)[0]['bbox']

    xmin = np.max([-0.5, colmin-crop_buffer-0.5])
    xmax = np.min([colmax+crop_buffer+0.5, ncols_init-0.5])
    ymin = np.max([-0.5, rowmin-crop_buffer-0.5])
    ymax = np.min([rowmax+crop_buffer+0.5, nrows_init-0.5])
    
    ax.set_xlim(left=xmin, right=xmax)
    ax.set_ylim(bottom=ymax, top=ymin)

def figs_to_pdf(figures, save_name):
    """
    Save series of figures to pdf where each figure is on a single page.

    Parameters
    ----------
    figures : List[matplotlib figure objects]
    savename : str, Path

    Returns
    -------
    None
    """
    image_pdf = PdfPages(save_name)
    for fig in figures:
        image_pdf.savefig(fig)
    image_pdf.close()

def labels_to_contours(labels, level=0.5):
    """

    Parameters
    ----------
    labels : np.array(dtype=int)
    level : float, (0, 1)

    Returns
    -------
    contours : list[np.array(shape=(N,2))]
        Length of contours matches number of rois
        Columns of each array contain rows and columns, respectively.
    """
    n_labels = labels.max()
    contours = []
    for l in range(1, n_labels+1):
        label = labels == l
        contour = find_contours(label, level=level)
        contours.append(contour)
        
    return contours

def plot_locs_gaussian():
    """
    Plots localizations with each represented by a Gaussian distribtuion.

    Parameters
    ----------
    

    Returns
    -------
    fig
    ax
    """
    pass

def plot_locs_scatter(locs_df,
                        coord_cols=('x', 'y'),
                        color_col = None,
                        scale = 1,
                        labels = None,
                        image = None,
                        crop = False,
                        figure_props = {},
                        marker_props = {},
                        scalebar_props = None):
    """
    Plot single-molecule localization data as a scatter plot.
    
    Parameters
    ----------
    locs_df : pd.DataFrame
    coord_cols : 2-tuple of strings, default ('x', 'y')
        Specify columns of locs_df containing coordinates.
        Set to ('col', 'row') for data originating from SMALL-LABS.
    color_col : string
        Specify column of locs_df to determine marker color.
    scale : float
        Factor to convert units of coord_cols to pixels
    labels : np.ndarray
        2d integer array labeling regions of interest.
        Typically the output of segmentation, e.g. cellpose.
    image : np.ndarray
        2d array to overlay localization scatter on.
        Typically, some kind reference image, e.g. phase contrast.
        If None provided, plot on black background by default.
    crop : bool, default False
        If True, will crop to only display area where labels > 0.
    figure_props : dict
        Inputs to plt.subplots.
    marker_props : dict
        kwargs to matplotlib.pyplot.scatter
    scalebar_props : dict
        Inputs to add_scalebar. If None provided (default), no scalebar is drawn.

    Returns
    -------
    fig, ax
    """
    xcol, ycol = coord_cols

    if color_col is None: colors = None
    else: colors = locs_df[color_col]

    if 'c' not in marker_props:
        marker_props['c'] = colors

    if labels is not None:
        contours = labels_to_contours(labels)
    else:
        contours = []

    if image is None and labels is None:
        colmax = int(np.max(locs_df[xcol]*scale)) + 1
        rowmax = int(np.max(locs_df[ycol]*scale)) + 1
        image = np.zeros([rowmax, colmax])
    elif image is None:
        image = np.zeros(labels.shape)

    fig, ax = plt.subplots(1, 1, **figure_props)
        
    ax.imshow(image, cmap='binary_r')
    
    for contour in contours:
        ax.plot(contour[0][:,1], contour[0][:,0], lw=1, alpha=0.5, color='xkcd:gray')

    ax.scatter(locs_df[xcol]*scale, locs_df[ycol]*scale, **marker_props)
            
    if crop == True:
        crop_to_labels(ax, labels)

    if scalebar_props is not None:
        add_scalebar(ax, scalebar_props)

    ax.axis('off')

    return fig, ax

def plot_tracks(locs_df,
                track_data = None,
                coord_cols=('x', 'y'),
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
    Plot single-molecule tracks.

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
    xcol = coord_cols[0]
    ycol = coord_cols[1]

    if track_data is None:
        track_ids = np.unique(locs_df['track_id'])
        track_data = pd.DataFrame(data={'track_id': np.unique(track_ids)})

    if subsample is not None:
        idx_sub = np.random.choice(track_data.index, size=subsample, replace=False)
        track_data = track_data.loc[idx_sub].reset_index()

    if labels is not None:
        contours = labels_to_contours(labels)
    else:
        contours = []

    if image is None and labels is None:
        colmax = int(np.max(locs_df[xcol]*scale)) + 1
        rowmax = int(np.max(locs_df[ycol]*scale)) + 1
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
                crop_to_labels(ax[i_ax], labels)

            if scalebar_props is not None:
                add_scalebar(ax[i_ax], scalebar_props)

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
            crop_to_labels(ax, labels)

        if scalebar_props is not None:
            add_scalebar(ax, scalebar_props)

    return fig, ax