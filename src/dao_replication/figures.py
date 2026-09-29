"""Figures. Style follows a fixed-slot categorical palette (blue, orange, aqua,
yellow) validated for colour-vision deficiency; aqua and yellow fall below 3:1
contrast on a light surface, so every series also has its own marker and line
style, every figure has a legend, and the underlying numbers are written to CSV.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .config import CONDITION_LABELS, CONDITIONS, RATIOS  # noqa: E402
from .data import REVERSE_ITEMS  # noqa: E402
from .survey import FIG5_ITEMS, FIG6_ITEMS, condition_means  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e6e5e0"

STYLE = {  # fixed by condition (colour follows the entity)
    "quadratic-equal": {"color": "#2a78d6", "marker": "o", "ls": "-"},
    "quadratic-early": {"color": "#eb6834", "marker": "s", "ls": "-"},
    "ranked-equal": {"color": "#1baf7a", "marker": "^", "ls": "--"},
    "ranked-early": {"color": "#eda100", "marker": "D", "ls": "--"},
}


def _base(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _fig(*args, **kw):
    fig, axes = plt.subplots(*args, **kw)
    fig.patch.set_facecolor(SURFACE)
    return fig, axes


def _legend(ax, **kw):
    leg = ax.legend(frameon=False, fontsize=9, labelcolor=INK2, **kw)
    return leg


CHOICE_TICKS = ["1\nCurrent\nmodel", "2\nExtra user\ninfo", "3\nTrack\npreferences", "4\nFlags /\ntags"]


def fig4_interaction(votes: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Mean token ratio per choice, by condition, for each round (paper Fig. 4)."""
    fig, axes = _fig(1, 2, figsize=(11, 4.4), sharey=True)
    rows = []
    for ax, rnd in zip(axes, (1, 2)):
        _base(ax)
        d = votes[votes["round"] == rnd]
        for cond in CONDITIONS:
            m = d[d["cond"] == cond][RATIOS].mean().to_numpy()
            st = STYLE[cond]
            ax.plot(range(4), m, color=st["color"], marker=st["marker"], ls=st["ls"], lw=2, ms=7,
                    markeredgecolor=SURFACE, markeredgewidth=1.2, label=CONDITION_LABELS[cond])
            for i, v in enumerate(m):
                rows.append({"round": rnd, "cond": cond, "choice": i + 1, "mean_ratio": v})
        ax.set_xticks(range(4), CHOICE_TICKS)
        ax.set_xlim(-0.3, 3.3)
        ax.set_title(f"Round {rnd} (n = {len(d)})", color=INK, fontsize=11, loc="left")
    axes[0].set_ylabel("Mean share of budget allocated", color=INK2, fontsize=9)
    _legend(axes[0], loc="upper left", title="Voting method, power", title_fontsize=9)
    fig.suptitle("Token allocation by choice and voting design (ratios as defined in the paper)",
                 color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    return pd.DataFrame(rows)


def _dotplot(means: pd.DataFrame, items: list[str], texts: dict[str, str], title: str, path: Path):
    n = len(items)
    fig, ax = _fig(figsize=(10.5, 0.62 * n + 1.9))
    _base(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    offs = np.linspace(-0.24, 0.24, len(CONDITIONS))
    labels = []
    for i, item in enumerate(items):
        t = texts.get(item, item)
        t = textwrap.fill(t, 58) + (" (reversed)" if item in REVERSE_ITEMS else "")
        labels.append(t)
    for j, cond in enumerate(CONDITIONS):
        st = STYLE[cond]
        m = means[means["cond"] == cond].set_index("item").loc[items, "mean"].to_numpy()
        ax.scatter(m, np.arange(n) + offs[j], color=st["color"], marker=st["marker"], s=46,
                   edgecolor=SURFACE, linewidth=1.0, label=CONDITION_LABELS[cond], zorder=3)
    ax.set_yticks(range(n), labels)
    ax.invert_yaxis()
    ax.set_xlim(1.5, 5)
    ax.set_xlabel("Mean rating (1 = strongly disagree, 5 = strongly agree)", color=INK2, fontsize=9)
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    handles, lab = ax.get_legend_handles_labels()
    fig.legend(handles, lab, loc="lower center", ncol=4, frameon=False, fontsize=9, labelcolor=INK2)
    fig.tight_layout(rect=(0, 0.07 if n > 4 else 0.14, 1, 1))
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def fig5_fig6(gov: pd.DataFrame, texts: dict[str, str], out_dir: Path) -> pd.DataFrame:
    means = condition_means(gov, FIG5_ITEMS + FIG6_ITEMS, reverse=True)
    _dotplot(means, FIG5_ITEMS, texts, "Perception of the decision process, by condition (paper Fig. 5)", out_dir / "fig5_process_perception.png")
    _dotplot(means, FIG6_ITEMS, texts, "Perception of the voting mechanism, by condition (paper Fig. 6)", out_dir / "fig6_mechanism_perception.png")
    return means


def fig_sensitivity(variants: pd.DataFrame, path: Path):
    """p-value of each factor under alternative data treatments (not in the paper)."""
    labels = list(dict.fromkeys(variants["variant"]))
    fig, axes = _fig(1, 2, figsize=(11.5, 4.2), sharey=True)
    for ax, term in zip(axes, ("quadratic", "same")):
        _base(ax)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        for rnd, color, marker in ((1, "#2a78d6", "o"), (2, "#eb6834", "s")):
            d = variants[(variants["term"] == term) & (variants["round"] == rnd)].set_index("variant")
            y = [labels.index(v) for v in d.index]
            ax.scatter(d["p"], y, color=color, marker=marker, s=50, edgecolor=SURFACE, linewidth=1.0,
                       label=f"Round {rnd}", zorder=3)
        ax.axvline(0.05, color=INK2, lw=1, ls=":")
        ax.set_ylim(len(labels) - 0.5, -1.0)
        ax.text(0.052, -0.72, "p = 0.05", color=INK2, fontsize=8, va="center")
        ax.set_xscale("log")
        ax.set_xlim(0.005, 1.0)
        ax.set_xlabel("p-value (Pillai's trace, log scale)", color=INK2, fontsize=9)
        ax.set_title(f"Effect of {'voting method' if term == 'quadratic' else 'voting power'}", color=INK, fontsize=11, loc="left")
    axes[0].set_yticks(range(len(labels)), [textwrap.fill(v, 34) for v in labels])
    axes[0].invert_yaxis()
    handles, lab = axes[0].get_legend_handles_labels()
    fig.legend(handles, lab, loc="upper right", ncol=2, frameon=False, fontsize=9, labelcolor=INK2,
               bbox_to_anchor=(0.99, 0.995))
    fig.suptitle("How the MANOVA p-values change with the data treatment", color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
