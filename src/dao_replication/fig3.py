"""Fig. 3 (overall satisfaction): re-plot and consistency check.

The three satisfaction statements are NOT in the released survey files, so this
figure cannot be recomputed from data. What can be done: (a) redraw it in the
article's layout from the values embedded in the article's own graphic, (b)
compare those with the percentages quoted in the caption, and (c) infer the
number of respondents from the percentages.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from .compare import DIGITISED_DIR  # noqa: E402
from .figures import INK, INK2, SURFACE, _base  # noqa: E402
from .paper_values import FIG3_TEXT  # noqa: E402

CATS = ["Strongly Agree", "Agree", "Somewhat Agree", "Neutral", "Somewhat Disagree", "Disagree", "Strongly Disagree"]
COLOURS = ["#7ac2bc", "#bde0dd", "#d4d4d4", "#f0e0c2", "#ddc282", "#d9a638", "#ffffff"]  # as in the article
ORDER = ["experience", "trust", "contributions"]  # bottom to top, as in the article
LABELS = {
    "experience": "The experience was enjoyable or meaningful",
    "trust": "I would trust this process to determine the stereotypical bias in AI design that reflects public consensus.",
    "contributions": "I believe my contributions will be used appropriately to achieve the final output to design "
                     "Generative AI model which reflects informed public consensus",
}


def load_figure_values() -> pd.DataFrame:
    d = pd.read_csv(DIGITISED_DIR / "fig3_segments.csv")
    return d.pivot(index="statement", columns="category", values="pct_figure").reindex(index=ORDER, columns=CATS).fillna(0.0)


def consistency_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(long table figure-vs-caption, per-statement summary with implied N)."""
    fig = load_figure_values()
    rows = []
    for s in ORDER:
        for c in CATS:
            txt = FIG3_TEXT[s].get(c, np.nan)
            rows.append({"statement": s, "category": c, "figure_pct": fig.loc[s, c], "caption_pct": txt,
                         "diff": txt - fig.loc[s, c] if pd.notna(txt) else np.nan})
    long = pd.DataFrame(rows)
    summ = []
    for s in ORDER:
        cap = pd.Series(FIG3_TEXT[s])
        # respondent counts N for which every figure percentage is (almost) a whole count
        ok = [n for n in range(50, 400) if np.abs(fig.loc[s] * n / 100 - np.round(fig.loc[s] * n / 100)).max() < 0.02]
        summ.append({"statement": s, "sum_of_caption_pcts": cap.sum(), "sum_of_figure_pcts": fig.loc[s].sum(),
                     "smallest_N_consistent_with_figure": ok[0] if ok else np.nan,
                     "max_abs_caption_minus_figure": long[long.statement == s]["diff"].abs().max()})
    return long, pd.DataFrame(summ)


def _bars(ax, table: pd.DataFrame):
    _base(ax)
    ax.grid(axis="y", visible=False)
    left = np.zeros(len(ORDER))
    for c, col in zip(CATS, COLOURS):
        v = table.loc[ORDER, c].to_numpy()
        ax.barh(range(len(ORDER)), v, left=left, color=col, edgecolor="#9a9a96" if c == "Strongly Disagree" else "none", height=0.62, linewidth=0.6)
        left += v
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10), [f"{t}%" for t in range(0, 101, 10)])
    ax.set_yticks(range(len(ORDER)), [textwrap.fill(LABELS[s], 44) for s in ORDER], fontsize=8)


def fig3_pair(path: Path):
    fig_v = load_figure_values()
    cap = pd.DataFrame(FIG3_TEXT).T.reindex(index=ORDER, columns=CATS).fillna(0.0)
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 6.8), sharex=True)
    fig.patch.set_facecolor(SURFACE)
    for ax, t, title in zip(axes, (fig_v, cap), ("Article, Fig. 3 (shares taken from the bar geometry in the PDF)",
                                                 "Same layout drawn from the percentages quoted in the article's caption")):
        _bars(ax, t)
        ax.set_title(title, color=INK, fontsize=10.5, loc="left")
    axes[1].set_xlabel("Percentage of responses", color=INK2, fontsize=9)
    trust_sum = cap.loc["trust"].sum()
    axes[1].text(100, 1.42, f"caption values for the middle statement add up to {trust_sum:.1f} %", ha="right", va="center",
                 fontsize=8.5, color=INK2)
    handles = [Patch(facecolor=c, edgecolor="#9a9a96" if c == "#ffffff" else "none", label=k) for k, c in zip(CATS, COLOURS)]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.985, 0.5), frameon=False, fontsize=8.5, labelcolor=INK2)
    fig.suptitle("Fig. 3: not recomputable from the released data; re-plotted from the article's own numbers",
                 color=INK, fontsize=11.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
