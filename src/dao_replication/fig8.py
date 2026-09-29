"""Fig. 8: correlations between the AI-value survey (rows) and the governance survey
(columns). The article's printed cells were read from the PDF (data/paper_figures/
fig8_printed_cells.csv). Because the two survey files carry no shared participant
id, our matrix pairs respondents by row index, which is an assumption, not a link;
the diagnostics below show that it does not reproduce the article.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import vdem  # noqa: E402
from .compare import DIGITISED_DIR  # noqa: E402
from .config import SEED  # noqa: E402
from .figures import INK, INK2, SURFACE  # noqa: E402
from .paper_extract import FIG8_COLS, FIG8_VALUE_COLS  # noqa: E402

THRESH = 0.1  # the article prints a cell only when |r| >= 0.1
COL_LABELS = [
    "Process was indecisive", "Process not good at maintaining order", "Process better than other forms of government",
    "Voting method meaningful for my voice", "Voting method relevant to proposal", "Voting power meaningful for my voice",
    "I can contribute to shaping the model", "Voting power relevant to proposal", "Voting method fair",
    "I have power to affect future development", "Voting power distribution equitable", "Voting power can give unexpected outcome",
    "Electoral Democracy", "Liberal Democracy", "Participatory Democracy", "Deliberative Democracy", "Egalitarian Democracy",
    "Rule of Law", "Civil Liberties", "Political Equality", "Civil Society Participation", "Judicial Constraints on the Executive",
]


def paper_matrix() -> tuple[pd.DataFrame, list[str]]:
    d = pd.read_csv(DIGITISED_DIR / "fig8_printed_cells.csv", index_col=0)
    return d.drop(columns="row_label"), list(d["row_label"])


def paired_frames(gov: pd.DataFrame, value: pd.DataFrame, mode: str = "row_index", rng=None):
    g = pd.concat([gov[FIG8_COLS[:12]], vdem.subscales(gov)[list(vdem.VDEM_ITEMS)]], axis=1)
    g.columns = FIG8_COLS
    v = value[FIG8_VALUE_COLS]
    n = min(len(g), len(v))
    if mode == "row_index":
        return g.iloc[:n].reset_index(drop=True), v.iloc[:n].reset_index(drop=True)
    parts_g, parts_v = [], []  # random pairing within condition
    for c in gov["cond"].unique():
        gi = g[gov["cond"] == c].reset_index(drop=True)
        vi = v[value["cond"] == c].sample(frac=1, random_state=int(rng.integers(1 << 30))).reset_index(drop=True)
        m = min(len(gi), len(vi))
        parts_g.append(gi.iloc[:m]); parts_v.append(vi.iloc[:m])
    return pd.concat(parts_g, ignore_index=True), pd.concat(parts_v, ignore_index=True)


def corr_matrix(g: pd.DataFrame, v: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([[v[a].corr(g[b]) for b in g.columns] for a in v.columns], index=v.columns, columns=g.columns)


def diagnostics(gov, value, n_null: int = 500) -> tuple[pd.DataFrame, pd.DataFrame]:
    paper, _ = paper_matrix()
    ours = corr_matrix(*paired_frames(gov, value))
    pr = paper.notna().to_numpy()
    d = (ours.to_numpy() - paper.to_numpy())[pr]
    rng = np.random.default_rng(SEED)
    null_counts, null_corr = [], []
    for _ in range(n_null):
        c = corr_matrix(*paired_frames(gov, value, "random_within_condition", rng)).to_numpy()
        null_counts.append(int((np.abs(c) >= THRESH).sum()))
        null_corr.append(np.corrcoef(c[pr], paper.to_numpy()[pr])[0, 1])
    rows = [
        ("cells printed in the article (|r| >= 0.1), of 396", int(pr.sum())),
        ("cells with |r| >= 0.1, our row-index pairing", int((np.abs(ours.to_numpy()) >= THRESH).sum())),
        ("same, random pairings within condition: mean", float(np.mean(null_counts))),
        ("same, random pairings within condition: 2.5th-97.5th percentile", f"{np.percentile(null_counts, 2.5):.0f}-{np.percentile(null_counts, 97.5):.0f}"),
        ("printed cells reproduced within 0.005 (row-index pairing)", int((np.abs(d) <= 0.0051).sum())),
        ("mean |ours - article| over printed cells", float(np.abs(d).mean())),
        ("correlation of our and article's values over printed cells", float(np.corrcoef(ours.to_numpy()[pr], paper.to_numpy()[pr])[0, 1])),
        ("same correlation under random pairings: mean", float(np.mean(null_corr))),
        ("share of row-index-paired rows whose condition labels agree", float((gov["cond"].to_numpy()[: len(value)] == value["cond"].to_numpy()[: len(gov)]).mean())),
    ]
    return pd.DataFrame(rows, columns=["diagnostic", "value"]), ours


def _heat(ax, m: pd.DataFrame, title: str, show_cols: bool, row_labels):
    im = ax.imshow(m.to_numpy(), cmap="PiYG", vmin=-1, vmax=1, aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.iat[i, j]
            if pd.notna(v) and abs(v) >= THRESH:
                ax.text(j, i, f"{round(v, 2):g}",
                        ha="center", va="center", fontsize=5.6, color="#1a1a1a")
    ax.set_yticks(range(m.shape[0]), row_labels, fontsize=7)
    ax.set_xticks(range(m.shape[1]), [textwrap.fill(c, 34) for c in COL_LABELS] if show_cols else [], rotation=90, fontsize=6.6)
    ax.set_title(title, color=INK, fontsize=10.5, loc="left")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=2)
    return im


def fig8_pair(gov, value, path: Path):
    paper, rows = paper_matrix()
    ours = corr_matrix(*paired_frames(gov, value))
    shown = ours.where(ours.abs() >= THRESH)
    fig, axes = plt.subplots(2, 1, figsize=(12, 12.5), gridspec_kw={"height_ratios": [1, 1]})
    fig.patch.set_facecolor(SURFACE)
    _heat(axes[0], paper, "Article, Fig. 8 (printed cells; blank = |r| < 0.1)", False, rows)
    im = _heat(axes[1], shown, "Replication attempt: released data, respondents paired by row index (NOT a verified link)", True, rows)
    fig.subplots_adjust(right=0.9, hspace=0.06, left=0.32, bottom=0.2, top=0.96)
    cax = fig.add_axes([0.92, 0.25, 0.015, 0.7])
    fig.colorbar(im, cax=cax).ax.tick_params(labelsize=7)
    axes[1].set_xlabel("User perception of the voting process", fontsize=10, color=INK2, labelpad=8)
    fig.text(0.015, 0.6, "User AI value", rotation=90, fontsize=10, color=INK2, va="center")
    fig.savefig(path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
