from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
import numpy as np

from alpha_shapes import Alpha_Shaper

np.random.seed(42)  # for reproducibility

#  Define a set of points
points = np.random.random((1000, 2))

x = points[:, 0]
y = points[:, 1]


z = x**2 * np.cos(5 * x * y - 8 * x + 9 * y) + y**2 * np.sin(
    5 * x * y - 8 * x + 9 * y
)

# If the characteristic scale along each axis varies significantly,
# it may make sense to turn on the `normalize` option.
shaper = Alpha_Shaper(points, normalize=True)
alpha_opt, alpha_shape_scaled = shaper.optimize()

#  mask = shaper.set_mask_at_alpha(alpha_opt)

fig, ax = plt.subplots()
ax = cast(Axes, ax)

ax.tricontourf(shaper, z)
ax.triplot(shaper)
ax.plot(x, y, ".k", markersize=2)
ax.set_aspect("equal")

plt.show()
