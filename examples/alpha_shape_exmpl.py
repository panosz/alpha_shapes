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
          (0.5,    2.5),
          (-0.5,    1.5), (-0.25,    1.5),
          (-0.25,    1.25), (0,    1.25),
          (1.5,    1.5), (1.25,    1.5),
          (1.25,    1.25), (1,    1.25),
          (0.5,    2.25),
          (1.,    2.),    (0.25,  2.15),  (0.65,  2.45),
          (0.75,  2.75),  (0.5,   2.5),   (0.5,   2.25),
          (0.5,   2.75),  (0.25,  2.5),   (0.75,  2.25)]


# Scale the points along the x-dimension
x_scale = 1e-3
points = np.array(points)
points[:, 0] *= x_scale

#  Create the alpha shape without accounting for the x and y scale separation
unnormalized_shaper = Alpha_Shaper(points, normalize=False)
_, alpha_shape_unscaled = unnormalized_shaper.optimize()


# If the characteristic scale along each axis varies significantly,
# it may make sense to turn on the `normalize` option.
shaper = Alpha_Shaper(points, normalize=True)
_, alpha_shape_scaled = shaper.optimize()

#  Compare the alpha shapes calculated with and without scaling.
fig, (ax0, ax1, ax2) = plt.subplots(1, 3,
                                    sharey=True,
                                    sharex=True,
                                    constrained_layout=True)
ax0.scatter(*zip(*points))
ax0.set_title('data')
ax1.scatter(*zip(*points))
ax2.scatter(*zip(*points))
ax1.add_patch(PolygonPatch(alpha_shape_scaled, alpha=0.2, color='r'))
ax1.set_title("with normalization")
ax2.add_patch(PolygonPatch(alpha_shape_unscaled, alpha=0.2))
ax2.set_title("without normalization")

for ax in (ax1, ax2):
    ax.set_axis_off()
for ax in (ax0, ax1, ax2):
    ax.set_aspect(x_scale)

plt.show()
