import matplotlib.pyplot as plt
from alpha_shapes import Alpha_Shaper, plot_alpha_shape

#  Define a set of points

points = [(0.,     0.),    (0.,    1.),    (1.,     1.1),
          (1.,     0.),    (0.25,  0.15),  (0.65,   0.45),
          (0.75,   0.75),  (0.5,   0.5),   (0.5,    0.25),
          (0.5,    0.75),  (0.25,  0.5),   (0.75,   0.25),
          (0.,     2.),    (0.,    2.1),   (1.,     2.1),
          (0.5,    2.5),   (-0.5,  1.5),   (-0.25,  1.5),
          (-0.25,  1.25),  (0,     1.25),  (1.5,    1.5),
          (1.25,   1.5),   (1.25,  1.25),  (1,      1.25),
          (1.,    2.),    (0.25,   2.15),
          (0.65,   2.45),  (0.75,  2.75),  (0.5,    2.25),
          (0.5,    2.75),  (0.25,  2.5),   (0.75,   2.25)]


#  Create the alpha shaper
shaper = Alpha_Shaper(points)

# Calculate the shape
alpha = 3.0
alpha_shape = shaper.get_shape(alpha=alpha)

fig, (ax0, ax1) = plt.subplots(1, 2)
ax0.scatter(*zip(*points))
ax0.set_title('data')
ax1.scatter(*zip(*points))
plot_alpha_shape(ax1, alpha_shape)
ax1.set_title(f"$\\alpha={alpha:.3}$")

for ax in (ax0, ax1):
    ax.set_aspect('equal')

# Calculate the shape with increased alpha value
alpha = 4.5
alpha_shape = shaper.get_shape(alpha=alpha)

fig, (ax0, ax1) = plt.subplots(1, 2)
ax0.scatter(*zip(*points))
ax0.set_title('data')
ax1.scatter(*zip(*points))
plot_alpha_shape(ax1, alpha_shape)
ax1.set_title(f"$\\alpha={alpha:.3}$")

for ax in (ax0, ax1):
    ax.set_aspect('equal')

# Calculate the optimal alpha shape
alpha_opt, alpha_shape = shaper.optimize()
print(alpha_opt)

fig, (ax0, ax1) = plt.subplots(1, 2)
ax0.scatter(*zip(*points))
ax0.set_title('data')
ax1.scatter(*zip(*points))
plot_alpha_shape(ax1, alpha_shape)
ax1.set_title(f"$\\alpha_{{\\mathrm{{opt}}}}={alpha_opt:.3}$")

for ax in (ax0, ax1):
    ax.set_aspect('equal')

plt.show()
