from descartes import PolygonPatch
import numpy as np
import matplotlib.pyplot as plt
from alpha_shapes.alpha_shapes import Alpha_Shape

#  Define a set of points

points = np.random.random((1000, 2))
alpha_shaper = Alpha_Shape(points, normalize=True)
alpha_opt, alpha_shape = alpha_shaper.optimize()
alpha_sub_opt = alpha_shaper.get_shape(alpha_opt*1.5)
print(alpha_opt)

#  Compare the alpha shapes calculated with and without scaling.
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, sharey=True, sharex=True)
ax0.plot(*zip(*points), linestyle='', color='k', marker='.', markersize=1)
ax0.set_title('data')
ax1.plot(*zip(*points), linestyle='', color='k', marker='.', markersize=1)
ax1.add_patch(PolygonPatch(alpha_shape, alpha=0.2, color='r'))
ax2.plot(*zip(*points), linestyle='', color='k', marker='.', markersize=1)
ax2.add_patch(PolygonPatch(alpha_sub_opt, alpha=0.2, color='r'))

for ax in (ax0, ax1, ax2):
    ax.set_aspect('equal')

plt.show()
