import matplotlib.pyplot as plt
import numpy as np

from alpha_shapes import Alpha_Shaper

np.random.seed(42)  # for reproducibility

#  Define a set of points
points = np.random.random((1000, 2))

x = points[:, 0]
y = points[:, 1]

z = x**2 * np.cos(x * y)

# If the characteristic scale along each axis varies significantly,
# it may make sense to turn on the `normalize` option.
shaper = Alpha_Shaper(points, normalize=True)
alpha_opt, alpha_shape_scaled = shaper.optimize()

#  mask = shaper.set_mask_at_alpha(alpha_opt)

fig, ax = plt.subplots()

ax.tricontourf(shaper, z)
ax.triplot(shaper)
ax.plot(x, y, ".k", markersize=2)

plt.show()
