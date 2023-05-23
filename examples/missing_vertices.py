"""
In this example, some input data is missing from the triangulation.
This is standard behavior for standard triangulation algorithms,
see for example qhull and the related "QJ" option.

In this particular case, all missing points are very close to other points 
that are included in the triangulation.

Related to issue #3.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.tri import Triangulation
from scipy.spatial import Delaunay

from alpha_shapes import Alpha_Shaper
from alpha_shapes.plotting import plot_alpha_shape

current_dir = Path(__file__).parent.absolute()

datafile = current_dir.parent / "tests" / "data" / "decade_points_2020.csv"

df = pd.read_csv(datafile)

shaper = Alpha_Shaper(df.drop_duplicates())  # type: ignore

tri = Triangulation(df.decimalLongitude, df.decimalLatitude)

delaunay = Delaunay(df)

plt.triplot(df.decimalLongitude, df.decimalLatitude, delaunay.simplices)

missing_vertices = set(range(shaper.x.size)) - set(
    np.ravel(shaper._sorted_simplices())
)

missing_x = [shaper.x[i] for i in missing_vertices]
missing_y = [shaper.y[i] for i in missing_vertices]

plt.scatter(missing_x, missing_y, color="red")


alpha_opt, alpha_shape = shaper.optimize()

plot_alpha_shape(plt.gca(), alpha_shape)

plt.show()
