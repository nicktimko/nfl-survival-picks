import matplotlib.offsetbox as obox
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


def plot_matrix(matrix, power_rank, cmap="PiYG", probs=False, week=None):

    if probs:
        params = {"vmin": 0, "vmax": 1}
    else:
        params = {"vmin": -8, "vmax": 8}

    n_weeks = len(matrix)
    n_teams = len(matrix[0])

    f, ax = plt.subplots()
    f.set_size_inches((8, 10))
    imshow = ax.imshow(np.array(matrix).T, cmap=cmap, origin="lower", **params)
    ax.xaxis.set_ticks(list(range(n_weeks)), list(range(1, n_weeks + 1)))
    ax.xaxis.set_label_text("Week")
    ax.yaxis.set_ticks(list(range(n_teams)), power_rank)
    ax.yaxis.set_label_text("Pick to Win")

    cbar = f.colorbar(imshow)
    cbar.set_label("Power Advantage")

    if week is not None:
        thepast = patches.Rectangle(
            xy=(week - 1.5 - n_weeks, -.5),
            width=n_weeks,
            height=n_teams,
            facecolor='xkcd:grey',
            alpha=0.5,
        )
        ax.add_patch(thepast)

        linewidth = 4
        xy, w, h = (week - 1.5, -.5), 1, 32
        r = patches.Rectangle(xy, w, h, facecolor='none')
        offsetbox = obox.AuxTransformBox(ax.transData)
        offsetbox.add_artist(r)
        ab = obox.AnnotationBbox(offsetbox, (xy[0] + w/2., xy[1] + h/2.),
                            boxcoords="data", pad=0.52,fontsize=linewidth,
                            bboxprops=dict(facecolor="none", edgecolor='xkcd:black',
                                    lw=linewidth))
        ax.add_artist(ab)

    return f, ax
