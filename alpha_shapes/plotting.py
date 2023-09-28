import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from alpha_shapes.boundary import Boundary, get_boundaries


def plot_alpha_shape(ax, alpha_shape):
    for boundary in get_boundaries(alpha_shape):
        _plot_boundary(ax, boundary)


def _plot_boundary(ax, boundary: Boundary):
    """
    Plot a boundary using matplotlib's PathPatch.
    see https://stackoverflow.com/a/70533052/6060982
    """
    exterior = Path(boundary.exterior)
    holes = [Path(hole) for hole in boundary.holes]
    path = Path.make_compound_path(exterior, *holes)
    patch = PathPatch(path, facecolor="r", lw=0.8, alpha=0.5, ec="b")
    ax.add_patch(patch)
