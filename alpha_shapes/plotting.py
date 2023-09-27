import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path


def plot_alpha_shape(ax, alpha_shape):
    try:
        geoms = alpha_shape.geoms
    except AttributeError:
        geoms = [alpha_shape]

    for geom in geoms:
        _plot_polygon(ax, geom)


def _plot_polygon(ax, polygon):
    """
    Plot a polygon using matplotlib's PathPatch.
    see https://stackoverflow.com/a/70533052/6060982
    """
    exterior = Path(np.asarray(polygon.exterior.coords))
    holes = [Path(np.asarray(hole.coords)) for hole in polygon.interiors]
    path = Path.make_compound_path(exterior, *holes)
    patch = PathPatch(path, facecolor="r", lw=0.8, alpha=0.5, ec="b")
    ax.add_patch(patch)
