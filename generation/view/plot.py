import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def plot(mat):
    array = np.array(mat)

    cmap = ListedColormap(["#222222", "#00cc66"])  # 0 → gris, 1 → vert

    plt.imshow(array, cmap=cmap)
    plt.title("Tunnel")
    plt.axis("off")
    plt.show()


maze = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


# plot(maze)
