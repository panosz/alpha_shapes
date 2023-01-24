def plot_alpha_shape(ax, alpha_shape):
    try:
        geoms = alpha_shape.geoms
    except AttributeError:
        geoms = [alpha_shape]

    for geom in geoms:
        _plot_polygon(ax, geom)


def _plot_polygon(ax, polygon):
    xe, ye = polygon.exterior.xy
    ax.fill(xe, ye, alpha=0.2, fc="r", ec="b")
