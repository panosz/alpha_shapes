from time import time
import numpy as np
import matplotlib.pyplot as plt
from alpha_shapes import Alpha_Shaper
from plotting import plot_alpha_shape

#  Define a set of random points
points = np.random.random((1000, 2))
# Prepare the shaper
alpha_shaper = Alpha_Shaper(points)

# Estimate the optimal alpha value and calculate the corresponding shape
ts = time()
alpha_opt, alpha_shape = alpha_shaper.optimize()
te = time()
print(f'optimization took: {te-ts:.2} sec')

fig, axs = plt.subplots(1,
                        2,
                        sharey=True,
                        sharex=True,
                        constrained_layout=True)

for ax in axs:
    ax.plot(*zip(*points),
            linestyle='',
            color='k',
            marker='.',
            markersize=1)

    ax.set_aspect('equal')

axs[0].set_title('data')

plot_alpha_shape(axs[1], alpha_shape)
axs[1].set_title(r'$\alpha_{\mathrm{opt}}$')

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

plot_alpha_shape(axs[1], alpha_shape)
axs[1].set_title(r'$\alpha_{\mathrm{opt}}$')
plot_alpha_shape(axs[2], alpha_sub_opt)
axs[2].set_title(r'$1.5\ \alpha_{\mathrm{opt}}$')


plt.show()
