import matplotlib.pyplot as plt
import numpy as np

def mandelbrot(h, w, max_iter=200):
    # Define constants for the complex plane bounds
    xmin, xmax, ymin, ymax = -2, 0.8, -1.4, 1.4

    # Create a grid of complex numbers
    y, x = np.ogrid[ymin:ymax:h*1j, xmin:xmax:w*1j]
    complex_plane = x + y*1j
    z = complex_plane
    divtime = max_iter + np.zeros(z.shape, dtype=int)

    for i in range(max_iter):
        z = z**2 + complex_plane
        diverge = np.abs(z) > 2
        div_now = np.logical_and(diverge, divtime == max_iter)
        divtime[div_now] = i
        z[diverge] = 2

    return divtime

h, w = 1000, 1500  # Decrease resolution
max_iter = 200

d = mandelbrot(h, w, max_iter)

plt.figure(figsize=(16, 10))
plt.imshow(d, cmap='hot', extent=[-2, 0.8, -1.4, 1.4])
plt.gca().set_facecolor('blue')  # Set the interior (undefined region) to blue
plt.colorbar(label='Iteration count')
plt.title('Mandelbrot Set with Pink Exterior and Blue Interior')
plt.xlabel('Re(c)')
plt.ylabel('Im(c)')
plt.tight_layout()
plt.show()