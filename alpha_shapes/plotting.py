"""This module contains mechanisms essential to printing figures.
Functions receive sets of points from alpha_shapes and then plot appropriate shapes.
This pattern is used in examples directory.
"""
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def plot_alpha_shape(ax, alpha_shape):
    """Main-line function, which plots all sets of figure's points.

    Args:
        ax: Axes object received from matplotlib.subplots function
        alpha_shape: set of points given by Alpha_Shaper._get_shape method
    """
    try:
        geoms = alpha_shape.geoms
    except AttributeError:
        geoms = [alpha_shape]

    for geom in geoms:
        _plot_polygon(ax, geom)


def _plot_polygon(ax, polygon):
    """Plots a polygon using matplotlib's PathPatch.
    This thread on stackoverflow may be helpful https://stackoverflow.com/a/70533052/6060982.

    Args:
        ax: Axes object received from matplotlib.subplots function.
        polygon: Polygon object (from shapely.geometry) nested in object returned by Alpha_Shaper._get_shape method.
    """
    xe, ye = polygon.exterior.xy
    exterior = Path(np.column_stack([xe, ye]))
    holes = [Path(np.asarray(hole.coords)) for hole in polygon.interiors]
    path = Path.make_compound_path(exterior, *holes)
    patch = PathPatch(path, facecolor="r", lw=0.8, alpha=0.5, ec="b")
    ax.add_patch(patch)
