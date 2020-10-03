from time import time
from descartes import PolygonPatch
import numpy as np
import matplotlib.pyplot as plt
from alpha_shapes.alpha_shapes import Alpha_Shaper

#  Define a set of random points
points = np.random.random((1000, 2))
# Prepare the shaper
alpha_shaper = Alpha_Shaper(points, normalize=True)

# Estimate the optimal alpha value and calculate the corresponding shape
ts = time()
alpha_opt, alpha_shape = alpha_shaper.optimize()
te = time()
print(f'optimization took: {te-ts:.2} sec')

# Calculate the shape for greater than optimal alpha
alpha_sub_opt = alpha_shaper.get_shape(alpha_opt*1.5)
print(alpha_opt)

#  Compare the alpha shapes
fig, axs = plt.subplots(1, 3, sharey=True, sharex=True)

for ax in axs:
    ax.plot(*zip(*points),
            linestyle='',
            color='k',
            marker='.',
            markersize=1)

    ax.set_aspect('equal')

axs[0].set_title('data')

axs[1].add_patch(PolygonPatch(alpha_shape, alpha=0.2, color='r'))
axs[1].set_title(r'$\alpha_{\mathrm{opt}}$')
axs[2].add_patch(PolygonPatch(alpha_sub_opt, alpha=0.2, color='r'))
axs[2].set_title(r'$1.5\ \alpha_{\mathrm{opt}}$')


plt.show()
