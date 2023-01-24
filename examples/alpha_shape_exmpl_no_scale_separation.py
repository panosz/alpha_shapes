import matplotlib.pyplot as plt
import numpy as np
from plotting import plot_alpha_shape

from alpha_shapes.alpha_shapes import Alpha_Shaper

#  Define a set of points

points = [
    (0.0, 0.0),
    (0.0, 1.0),
    (1.0, 1.1),
    (1.0, 0.0),
    (0.25, 0.15),
    (0.65, 0.45),
    (0.75, 0.75),
    (0.5, 0.5),
    (0.5, 0.25),
    (0.5, 0.75),
    (0.25, 0.5),
    (0.75, 0.25),
    (0.0, 2.0),
    (0.0, 2.1),
    (1.0, 2.1),
    (0.5, 2.5),
    (-0.5, 1.5),
    (-0.25, 1.5),
    (-0.25, 1.25),
    (0, 1.25),
    (1.5, 1.5),
    (1.25, 1.5),
    (1.25, 1.25),
    (1, 1.25),
    (0.5, 2.25),
    (1.0, 2.0),
    (0.25, 2.15),
    (0.65, 2.45),
    (0.75, 2.75),
    (0.5, 2.5),
    (0.5, 2.25),
    (0.5, 2.75),
    (0.25, 2.5),
    (0.75, 2.25),
]


points = list(set(points))

#  Calculate the optimal alpha shape
shaper = Alpha_Shaper(points, normalize=False)
alpha_opt, shape = shaper.optimize()
print(alpha_opt)


#  Visualize
fig, (ax0, ax1) = plt.subplots(1, 2)
ax0.scatter(*zip(*points))
ax0.set_title("data")
ax1.scatter(*zip(*points))


plot_alpha_shape(ax1, shape)
ax1.set_title("alpha shape")
for ax in (ax0, ax1):
    ax.set_axis_off()

plt.show()
