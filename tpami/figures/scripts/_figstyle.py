"""One restrained IEEE-style visual system for all four V6 figures.

Vector PDF, Type-1/TrueType text (no Type-3), one font family, fixed sizes, no
gradients, no background fill, grayscale-safe encodings: every distinction is
carried by marker shape or line dash as well as by tone.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl

PT = 1 / 72.27                      # TeX point in inches
COL = 252.0 * PT                    # IEEEtran compsoc single column
TWOCOL = 516.0 * PT                 # text block width

mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    # V7.3: typography raised so that text lands at roughly 9 pt once the
    # figure is placed at \textwidth. Figures grow rather than text shrinking.
    "font.size": 9.0,
    "axes.labelsize": 9.0, "axes.titlesize": 9.0,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5, "legend.frameon": False,
    "axes.linewidth": 0.6, "grid.linewidth": 0.4,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.2, "ytick.major.size": 2.2,
    "lines.linewidth": 1.0, "lines.markersize": 3.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "savefig.pad_inches": 0.01,
})

# grayscale-safe: tone plus a distinct marker or dash for every role
INK      = "#000000"
MID      = "#4d4d4d"
LIGHT    = "#8c8c8c"
PALE     = "#bfbfbf"

ROLE = {
    "reference":        dict(color=INK,   ls="-",  marker="None", lw=1.0),
    "reference_other":  dict(color=MID,   ls="--", marker="None", lw=1.0),
    "anchor":           dict(color=INK,   ls="None", marker="o", mfc="white",
                             mew=0.9, ms=4.0),
    "added":            dict(color=INK,   ls="None", marker="^", mfc=INK, ms=3.4),
    "gap":              dict(color=LIGHT, ls=":",  marker="None", lw=0.9),
}

def panel_label(ax, s, dx=-0.085, dy=1.055):
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=7.5,
            fontweight="bold", va="top", ha="left")

def finish(fig, path):
    fig.savefig(path, format="pdf", bbox_inches="tight", metadata={"CreationDate": None, "Producer": None, "Creator": None})
    return path
