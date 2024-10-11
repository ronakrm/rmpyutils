from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  # type: ignore
from matplotlib import animation

myBlue = "#005baa"
myRed = "#ff2a2a"
myPurple = "#25a000"
myGreen = "#ed00d4"
myYellow = "#f0e442"
myColors = [myBlue, myRed, myPurple, myGreen, myYellow]

rmpy_cmap = mpl.colors.LinearSegmentedColormap.from_list(
    "RMPY", myColors, N=len(myColors)
)
mpl.colormaps.register(rmpy_cmap)


def SingleHist(A: np.ndarray, S: np.ndarray, outName: Optional[str] = None):
    d = A.shape[0]
    bin_boundaries = range(d + 1)

    plt.rcParams["axes.grid"] = False
    plt.rcParams["axes.linewidth"] = 0.0

    fig = plt.figure(figsize=(9, 3), dpi=300, frameon=False)
    plt.tight_layout(pad=0.0)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))

    # clear everything except plot area
    ax.axis("off")
    ax.patch.set_visible(False)
    ax.patch.set_linewidth(0.0)
    ax.set_axis_off()
    ax.set_frame_on(False)
    ax.minorticks_off()
    plt.tick_params(
        which="both",  # both major and minor ticks are affected
        right=False,
        left=False,  # ticks along the bottom edge are off
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    sns.histplot(
        x=range(d),
        weights=A,
        stat="count",
        bins=bin_boundaries,
        color=myBlue,
        alpha=1,
        ax=ax,
        legend=False,
    )

    sns.histplot(
        x=range(d),
        weights=S,
        stat="count",
        bins=bin_boundaries,
        color=myYellow,
        alpha=1,
        ax=ax,
        legend=False,
    )
    ax.set_xlim(0, d)

    if outName is not None:
        plt.savefig(outName, bbox_inches="tight", pad_inches=0.0)
    plt.show()


def univariateGiffer(
    logs, outName, plim=None, show_vals=False, alpha=False, total_time=5000
):

    plt.rcParams["axes.grid"] = False
    plt.rcParams["axes.linewidth"] = 0.0

    fig = plt.figure(figsize=(9, 3), dpi=300, frameon=False)
    plt.tight_layout(pad=0.0)
    ax = fig.add_axes([0, 0, 1, 1])

    # clear everything except plot area
    ax.axis("off")
    for item in [fig, ax]:
        item.patch.set_visible(False)
        item.patch.set_linewidth(0.0)
    # plt.subplots_adjust(wspace=0, hspace=0)
    ax.set_axis_off()
    ax.set_frame_on(False)
    ax.minorticks_off()
    plt.tick_params(
        which="both",  # both major and minor ticks are affected
        right=False,
        left=False,  # ticks along the bottom edge are off
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    def jointSingleAxisPlot(A: np.ndarray, show_vals=False):

        n, d = A.shape
        bin_boundaries = range(d + 1)

        # colors = sns.set_palette("tab10", n=n)

        for i in range(n):
            if alpha:
                alph = 0.5 + 0.5 * ((n - i) / n)
            else:
                alph = 1

            sns.histplot(
                x=range(d),
                weights=A[i, :],
                stat="count",
                bins=bin_boundaries,
                color=myColors[i],
                alpha=alph,
                ax=ax,
                legend=False,
            )
        ax.set_xlim(0, d)

    def animate(i=0):
        ax.clear()
        ax.patch.set_visible(False)
        if plim is not None:
            ax.set_ylim([0, plim])
        # plt.subplots_adjust(wspace=0, hspace=0)
        Ai = logs[i]["A"]

        jointSingleAxisPlot(Ai, show_vals=show_vals)
        # import pdb; pdb.set_trace()
        # fig.savefig(f'test_single.png')

    anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=animate,
        interval=total_time / len(logs),
        frames=len(logs),
        repeat=False,
    )
    anim.save(
        outName,
        codec="png",
        bitrate=-1,
        savefig_kwargs={
            "transparent": True,
            # "bbox_inches": 'tight',
        },
    )
