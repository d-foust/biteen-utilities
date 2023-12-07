"""

"""

import napari as na
from napari_animation import Animation


def animate_1axis(viewer: na.Viewer, start_frame: int = 0, end_frame: int = None, axis: int = 0):
    """
    Whatever is currently displayed in viewer gets turned into a napari animation frame-by-frame.
    Use axis to specify temporal dimension.

    Parameters
    ----------
    viewer : na.Viewer
    start_frame : int
    end_frame : int
        Not included.
    axis : int

    Returns
    -------
    animation : Animation
    """
    current_step = viewer.dims.ndim * [0,]

    if end_frame is None:
        end_frame = int(viewer.dims.range[axis][1])

    animation = Animation(viewer)
    for frame in range(start_frame, end_frame): # end_frame is included
        current_step[axis] = frame
        viewer.dims.current_step = tuple(current_step)
        animation.capture_keyframe(steps=1)

    return animation

def save_animation(animation: Animation,
                   save_path: str,
                   canvas_only: bool = True,
                   fps: float = 24,
                   quality: float = 5):
    """
    Render and save napari_animation.Animation

    Parameters
    ----------
    animation : Animation
    save_path : str
        Where animation gets saved. Recommended: include .avi extension.
    canvas_only : bool
    fps : float
    quality : float
    """
    animation.animate(
        save_path,
        canvas_only = canvas_only,
        fps = fps,
        quality = quality
    )