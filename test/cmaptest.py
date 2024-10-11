import numpy as np
import matplotlib.pyplot as plt
import rmpyutils.plt

x = np.arange(0, np.pi, 0.1)
y = np.arange(0, 2 * np.pi, 0.1)
X, Y = np.meshgrid(x, y)
Z = np.cos(X) * np.sin(Y) * 10

plt.imshow(Z, cmap="RMPY")
plt.show()
