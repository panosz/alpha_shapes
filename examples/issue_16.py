import numpy as np
import matplotlib.pyplot as plt

points = np.genfromtxt('data/issue_16_points.txt', delimiter=',')

from alpha_shapes import Alpha_Shaper, plot_alpha_shape

shaper = Alpha_Shaper(points, normalize=True)
alpha_opt, shape = shaper.optimize()
print(f"Alpha shape optimize value:{alpha_opt}")

#  Compare the alpha shapes calculated with and without scaling.
fig, (ax0, ax1, ax2) = plt.subplots(
    1, 3, sharey=True, sharex=True, constrained_layout=True
)
ax0.scatter(*zip(*points))
ax0.set_title("data")
ax1.scatter(*zip(*points))
ax2.scatter(*zip(*points))

plot_alpha_shape(ax1, shape)


plt.show()

