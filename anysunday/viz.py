import matplotlib.pyplot as plt
import numpy as np


def plot_matrix(matrix, power_rank, cmap="PiYG", probs=False):

    if probs:
        params = {"vmin": 0, "vmax": 1}
    else:
        params = {"vmin": -8, "vmax": 8}

    f, ax = plt.subplots()
    f.set_size_inches((8, 10))
    imshow = ax.imshow(np.array(matrix).T, cmap=cmap, origin="lower", **params)
    ax.xaxis.set_ticks(list(range(17)))
    ax.xaxis.set_ticklabels(list(range(1, 18)))
    ax.xaxis.set_label_text("Week")
    ax.yaxis.set_ticks(list(range(32)))
    ax.yaxis.set_ticklabels(power_rank)
    ax.yaxis.set_label_text("Pick to Win")

    f.colorbar(imshow)

    return f, ax
