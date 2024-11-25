"""

"""
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib_scalebar.scalebar as sb
import numpy as np
import pandas as pd
from skimage.measure import find_contours, regionprops


default_scalebar_props = {
    'dx': 0.049,
    'units': 'um',
    'fixed_value': 4,
    'scale_loc': 'none',
    'location': 'lower left',
    'frameon': False
}

transparent_rgba = mpl.colors.to_rgba('xkcd:white', alpha=0)
black = mpl.colors.to_rgba('xkcd:black', alpha=1)
hotmagenta_tr = mpl.colors.to_rgba('xkcd:hot magenta', alpha=0)
hotmagenta_op = mpl.colors.to_rgba('xkcd:hot magenta', alpha=1)

transparent2hotmagenta = mpl.colors.LinearSegmentedColormap.from_list('transparent2hotmagenta',
                                                                   [hotmagenta_tr, hotmagenta_op],
                                                                   512)

black2hotmagenta = mpl.colors.LinearSegmentedColormap.from_list('black2hotmagenta',
                                                                   [black, hotmagenta_op],
                                                                   512)

  
def crop_to_labels(ax, labels, crop_buffer=5, scale=1):
    """
    Set limits of ax so that only bounding box of labels is shown with crop_buffer number of
    pixels added to border.

    Parameters
    ----------
    ax : matplotlib axis handle
    labels : np.array, dtype=int
    crop_buffer : int
        Extra pixels to leave around bounding box. Always in pixels even if scale is set.
    scale : float
        For converting pixel coordinates to other units.

    Returns
    -------
    None
    """
    nrows_init, ncols_init = labels.shape

    labels_bool = (labels > 0).astype('int')
    rowmin, colmin, rowmax, colmax = regionprops(labels_bool)[0]['bbox']

    xmin = np.max([-0.5, colmin-crop_buffer-0.5]) * scale
    xmax = np.min([colmax+crop_buffer+0.5, ncols_init-0.5]) * scale
    ymin = np.max([-0.5, rowmin-crop_buffer-0.5]) * scale
    ymax = np.min([rowmax+crop_buffer+0.5, nrows_init-0.5]) * scale
    
    ax.set_xlim(left=xmin, right=xmax)
    ax.set_ylim(bottom=ymax, top=ymin)


def figs_to_pdf(figures, save_name):
    """
    Save series of figures to pdf where each figure is on a single page.

    Parameters
    ----------
    figures : List[matplotlib figure objects]
        List of figure handles.
    savename : str, Path

    Returns
    -------
    None
    """
    image_pdf = PdfPages(save_name)
    for fig in figures:
        image_pdf.savefig(fig)
    image_pdf.close()


def gauss_kernel(x, sigma):
    """
    Helper for smoothening polygons.
    """
    gk = np.exp(-x**2 / (2 * sigma**2))
    gk[x==0] = 0
    gk /= gk.sum()
    return gk


def labels_to_contours(labels, level=0.5, smooth=False, lam=0.39, mu=-0.4, N=500, sigma=1.5):
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
        contours.append(*contour)

    if smooth == True:
        contours = [smooth_polygon(contour, 
                                   lam=lam, 
                                   mu=mu, 
                                   N=N, 
                                   sigma=sigma) for contour in contours]
        
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


def plot_locs_scatter(
        locs_df,
        coord_cols=('x', 'y'),
        scale = 1,
        labels = None,
        image = None,
        crop = False,
        figure_props = {},
        marker_props = {},
        scalebar_props = None,
        smooth = True,
        smooth_parameters = {}
        ):
    """
    Plot single-molecule localization data as a scatter plot.
    
    Parameters
    ----------
    locs_df : pd.DataFrame
    coord_cols : 2-tuple of strings, default ('x', 'y')
        Specify columns of locs_df containing coordinates.
        Set to ('col', 'row') for data originating from SMALL-LABS.
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
        https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html
    scalebar_props : dict
        Inputs to add_scalebar. If None provided (default), no scalebar is drawn.
        
    Returns
    -------
    fig, ax
    """
    xcol, ycol = coord_cols

    if labels is not None:
        contours = labels_to_contours(labels, smooth=smooth, **smooth_parameters)
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
        ax.plot(contour[:,1], contour[:,0], lw=1, alpha=0.5, color='xkcd:gray')

    ax.scatter(locs_df[xcol]*scale, locs_df[ycol]*scale, **marker_props)
            
    if crop == True and labels is not None:
        crop_to_labels(ax, labels)
    else:
        ax.set_xlim(left=-0.5, right=image.shape[1] - 0.5)
        ax.set_ylim(bottom=image.shape[0] - 0.5, top=-0.5)

    if scalebar_props is not None:
        scalebar = sb.ScaleBar(**scalebar_props)
        ax.add_artist(scalebar)

    ax.axis('off')

    return fig, ax


def plot_overlay(
        image_bgd: np.ndarray,
        image_fgd: np.ndarray,
        vmin_bgd: float = None,
        vmax_bgd: float = None,
        vmin_fgd: float = None,
        vmax_fgd: float = None,
        cmap_bgd: str = "binary_r",
        cmap_fgd_solo: mpl.colors.LinearSegmentedColormap = black2hotmagenta,
        cmap_fgd_overlay: mpl.colors.LinearSegmentedColormap = transparent2hotmagenta,
        scalebar_props: dict = default_scalebar_props
        ):
    """
    Creates figure with three axes for displaying two images and an overlay:
    1) Background image, e.g. phase contrast.
    2) Foreground image, e.g. bulk fluorescence.
    3) Overlay of foreground image on background image.

    Parameters
    ----------
    image_bgd : np.ndarray
        2D array for background image.
    image_fgd : np.ndarray
        2D array for foreground image.
    vmin_bgd : float
        Lower limit on background image - for setting contrast. Default is image_bgd.min().
    vmax_bgd : float
        Upper limit on background image - for setting contrast. Default is image_bgd.max().
    vmin_fgd : float
        Lower limit on foreground image - for setting contrast. Default is image_fgd.min().
    vmax_fgd : float
        Upper limit on foreground image - for setting contrast. Default is image_fgd.max().
    cmap_bgd : str, default "binary_r"
        Colormap for background image.
    cmap_fgd_solo : mpl.colors.LinearSegmentedColormap
        Colormap for foreground image in middle axes. Default is hot magenta against black.
    cmap_fgd_overlay : mpl.colors.LinearSegmentedColormap
        Colormap for foreground image in overlay. Default is hot magenta against transparent.
    scalebar_props : dict

    Returns
    -------
    fig : mpl.figure.Figure
    ax : mpl.axes.Axes
    """
    scalebar = sb.ScaleBar(**scalebar_props)

    fig, ax = plt.subplots(1, 3, figsize=(12,6))

    ax[0].imshow(image_bgd,
                 cmap=cmap_bgd,
                 vmin=vmin_bgd,
                 vmax=vmax_bgd)
    ax[0].add_artist(scalebar)
    ax[0].axis('off')

    ax[1].imshow(image_fgd,
                cmap=cmap_fgd_solo,
                vmin=vmin_fgd,
                vmax=vmax_fgd)
    ax[1].axis('off')

    ax[2].imshow(image_bgd,
                 cmap=cmap_bgd,
                 vmin=vmin_bgd,
                 vmax=vmax_bgd)
    ax[2].imshow(image_fgd,
                cmap=cmap_fgd_overlay,
                vmin=vmin_fgd,
                vmax=vmax_fgd)
    ax[2].axis('off')

    plt.tight_layout()

    return fig, ax


def plot_tracks(
        locs_df,
        track_data = None,
        coord_cols=('x', 'y'),
        track_col = 'track_id',
        color_col = None,
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
        scalebar_props = None
        ):
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
        track_ids = np.unique(locs_df[track_col])
        track_data = pd.DataFrame(data={track_col: np.unique(track_ids)})

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
        track_data_colors = ['xkcd:hot pink'] * n_bins
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
            for ti in track_data[track_col][filt]:
                loc_filt = locs_df[track_col] == ti
                x = locs_df[xcol][loc_filt]
                y = locs_df[ycol][loc_filt]
                ax[i_ax].plot(x*scale, y*scale, color=track_data_colors[i_ax%n_colors], **line_props)

            if crop == True:
                crop_to_labels(ax[i_ax], labels)

                if scalebar_props is not None:
                    # add_scalebar(ax, scalebar_props)
                    scalebar = sb.ScaleBar(**scalebar_props)
                    ax.add_artist(scalebar)

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
            filt = (track_data[color_col] > l) & (track_data[color_col] <= h)
            for ti in track_data[track_col][filt]:
                loc_filt = locs_df[track_col] == ti
                x = locs_df[xcol][loc_filt]
                y = locs_df[ycol][loc_filt]
                ax.plot(x*scale, y*scale, color=track_data_colors[i%n_colors], **line_props)
                
        if crop == True:
            crop_to_labels(ax, labels)

        if scalebar_props is not None:
            scalebar = sb.ScaleBar(**scalebar_props)
            ax.add_artist(scalebar)

    return fig, ax


def smooth_polygon(polygon, lam=0.39, mu=-0.4, N=500, sigma=1.5):
    """

    """
    nv = len(polygon) - 1
    I = np.identity(nv)
    W = np.zeros(I.shape)
    
    x = np.arange(-nv//2, nv//2)
    gk = gauss_kernel(x, sigma)
    gk = np.roll(gk, -nv//2)
    
    for v in range(nv):
        W[v,:] = gk
        gk = np.roll(gk, 1)

    K = I - W
    smooth_operator = np.linalg.matrix_power(np.matmul((I - mu*K), (I - lam*K)), N)
    polygon_smooth = np.matmul(smooth_operator, polygon[:-1]) # ignore second end
    polygon_smooth = np.concatenate([polygon_smooth,
                                    [polygon_smooth[0]]]) # make ends match
    
    return polygon_smooth