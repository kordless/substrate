import matplotlib.pyplot as plt
import numpy as np

def mandelbrot(h, w, max_iter):
    y, x = np.ogrid[-1.4:1.4:h*1j, -2:0.8:w*1j]
    c = x + y*1j
    z = c
    divtime = max_iter + np.zeros(z.shape, dtype=int)

    for i in range(max_iter):
        z = z**2 + c
        diverge = z*np.conj(z) > 2**2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        z[diverge] = 2

    return divtime

h, w = 1000, 1500
max_iter = 100

d = mandelbrot(h, w, max_iter)

plt.figure(figsize=(12, 8))
plt.imshow(d, cmap='hot', extent=[-2, 0.8, -1.4, 1.4])
plt.gca().set_facecolor('blue')  # Set the interior (undefined region) to blue
plt.colorbar(label='Iteration count')
plt.title('Mandelbrot Set with Pink Exterior and Blue Interior')
plt.xlabel('Re(c)')
plt.ylabel('Im(c)')
plt.tight_layout()
plt.show()
