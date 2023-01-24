
from descartes import PolygonPatch
import numpy as np
import matplotlib.pyplot as plt

from alpha_shapes.alpha_shapes import Alpha_Shaper

#  Define a set of points


points = [(0.,    0.),    (0.,    1.),    (1.,    1.1),
          (1.,    0.),    (0.25,  0.15),  (0.65,  0.45),
          (0.75,  0.75),  (0.5,   0.5),   (0.5,   0.25),
          (0.5,   0.75),  (0.25,  0.5),   (0.75,  0.25),
          (0.,    2.),    (0.,    2.1),    (1.,    2.1),
          (-0.5,    1.5), (-0.25,    1.5),
          (-0.25,    1.25), (0,    1.25),
          (1.5,    1.5), (1.25,    1.5),
          (1.25,    1.25), (1,    1.25),
          (1.,    2.),    (0.25,  2.15),  (0.65,  2.45),
          (0.75,  2.75),  (0.5,   2.5),   (0.5,   2.25),
          (0.5,   2.75),  (0.25,  2.5),   (0.75,  2.25)]


points = np.array(points)

x = points[:, 0]
y = points[:, 1]

z = x**2 * np.cos(x * y)

# If the characteristic scale along each axis varies significantly,
# it may make sense to turn on the `normalize` option.
shaper = Alpha_Shaper(points, normalize=True)
alpha_opt, alpha_shape_scaled = shaper.optimize()

mask = shaper.get_mask(alpha_opt)
shaper.set_mask(mask)



fig, ax = plt.subplots()

ax.tricontourf(shaper, z)
ax.triplot(shaper)
ax.plot(x, y, '.k', markersize=2)

plt.show()
