"""This module contains mechanisms essential to printing figures.
Functions receive sets of points and then plot appropriate shapes.
"""

import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def plot_alpha_shape(ax, alpha_shape):
    """Mainline function, which plots all sets of figure's points.

    Args:
        ax(Axes.matplotlib.subplots): axes of image.
        alpha_shape(numpy.ArrayLike): set of points to print.

    """

    try:
        geoms = alpha_shape.geoms
    except AttributeError:
        geoms = [alpha_shape]

    for geom in geoms:
        _plot_polygon(ax, geom)


def _plot_polygon(ax, polygon):
    """Plot a polygon using matplotlib's PathPatch.
    This thread on stackoverflow may be helpful https://stackoverflow.com/a/70533052/6060982.

    Args:
        ax(Axes.matplotlib.subplots): axes of image.
        polygon(shapely.geometry.Polygon): set of points to print.

    """

    xe, ye = polygon.exterior.xy
    exterior = Path(np.column_stack([xe, ye]))
    holes = [Path(np.asarray(hole.coords)) for hole in polygon.interiors]
    path = Path.make_compound_path(exterior, *holes)
    patch = PathPatch(path, facecolor="r", lw=0.8, alpha=0.5, ec="b")
    ax.add_patch(patch)
