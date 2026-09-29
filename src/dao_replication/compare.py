"""Paper-versus-replication comparison of Figs 4-7.

Paper values for Figs 5-7 were measured from the article's raster images
(data/paper_figures/*.csv, accuracy about +-0.015 rating points); Fig. 4 is
compared through Table 1, which prints the plotted means exactly.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from . import vdem  # noqa: E402
from .config import CONDITION_LABELS, CONDITIONS, RATIOS, REPO_ROOT  # noqa: E402
from .data import REVERSE_ITEMS  # noqa: E402
from .figures import GRID, INK, INK2, STYLE, SURFACE, _base  # noqa: E402
from .paper_values import TABLE1  # noqa: E402
from .survey import FIG5_ITEMS, FIG6_ITEMS, condition_means  # noqa: E402

DIGITISED_DIR = REPO_ROOT / "data" / "paper_figures"
TOL = 0.015  # digitisation accuracy in rating points

# Paper's fill order (matplotlib tab colours + hatches), read off Figs 5 and 7.
PAPER_FILLS = [
    ("#999999", None), ("#1f77b4", "/"), ("#f781bf", None), ("#ff7f00", "*"), ("#a65628", None),
    ("#2ca02c", "x"), ("#ffff33", None), ("#e41a1c", "+"), ("#ff7f00", None), ("#984ea3", "o"),
]
SHORT = {  # short panel titles for the survey items
    "Q1_1": "Decisive (reversed)", "Q1_2": "Maintains order (reversed)", "Q1_3": "Better than other governments",
}


def _digitised(name: str) -> pd.DataFrame:
    return pd.read_csv(DIGITISED_DIR / f"{name}_digitized.csv")


def figure_tables(gov: pd.DataFrame) -> pd.DataFrame:
    """Long table: figure, item, cond, paper (digitised), ours, diff, n, ci95."""
    ours = {
        "fig5": condition_means(gov, FIG5_ITEMS, reverse=True),
        "fig6": condition_means(gov, FIG6_ITEMS, reverse=True),
        "fig7": vdem.condition_means(vdem.subscales(gov)),
    }
    out = []
    for fig, o in ours.items():
        p = _digitised(fig).rename(columns={"paper_value": "paper"})
        j = p.merge(o.rename(columns={"mean": "ours"}), on=["item", "cond"])
        j["figure"] = fig
        out.append(j)
    t = pd.concat(out, ignore_index=True)
    t["diff"] = t["ours"] - t["paper"]
    t["ci95"] = 1.96 * t["sd"] / np.sqrt(t["n"])
    t["within_tol"] = t["diff"].abs() <= TOL + 0.005
    return t[["figure", "item", "cond", "n", "paper", "ours", "diff", "ci95", "within_tol"]]


def table1_comparison(t1: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (rnd, cond), (n, means, sds, dec) in TABLE1.items():
        r = t1[(t1["round"] == rnd) & (t1["cond"] == cond)].iloc[0]
        for i, k in enumerate(RATIOS):
            rows.append({"round": rnd, "cond": cond, "choice": i + 1, "stat": "mean", "paper": means[i],
                         "ours": r[f"mean_{k}"], "decimals": dec})
            rows.append({"round": rnd, "cond": cond, "choice": i + 1, "stat": "sd", "paper": sds[i],
                         "ours": r[f"sd_{k}"], "decimals": dec})
    t = pd.DataFrame(rows)
    t["diff"] = t["ours"] - t["paper"]
    t["matches_printed"] = t["diff"].abs() <= 10.0 ** (-t["decimals"]) + 1e-12  # one unit in the last printed digit, as in verify.py
    return t


# ---------------------------------------------------------------- figures
def _titles(items, texts):
    out = []
    for it in items:
        t = SHORT.get(it) or texts.get(it, it)
        t = t.replace("Voting mechanism ", "").strip()
        if it in REVERSE_ITEMS and "(reversed)" not in t:
            t += " (reversed)"
        out.append(textwrap.fill(t, 30))
    return out


def fig_paper_layout_pair(tab: pd.DataFrame, figure: str, items: list[str], titles: list[str], path: Path, name: str):
    """Top: the article's bar layout with the digitised article values. Bottom: the same
    layout from the replication data. Same axis (1-5), same fills, so differences are
    visible at a glance. Note that bars start at 1, the scale minimum, not at zero."""
    d = tab[tab["figure"] == figure]
    n = len(items)
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.2), sharey=True)
    fig.patch.set_facecolor(SURFACE)
    width = 0.8 / n
    for ax, col, lab in zip(axes, ("paper", "ours"), ("Article, Fig. %s (values read from the image)" % name[-1], "Replication (released data)")):
        _base(ax)
        for k, it in enumerate(items):
            color, hatch = PAPER_FILLS[k % len(PAPER_FILLS)]
            v = d[d["item"] == it].set_index("cond").loc[CONDITIONS, col].to_numpy()
            x = np.arange(4) + (k - (n - 1) / 2) * width
            ax.bar(x, v - 1, width=width * 0.94, bottom=1, color=color, hatch=hatch, edgecolor="#222222", linewidth=0.6)
        ax.set_xticks(range(4), [CONDITION_LABELS[c] for c in CONDITIONS])
        ax.set_ylim(1, 5)
        ax.set_ylabel("Mean rating (1-5)", color=INK2, fontsize=9)
        ax.set_title(lab, color=INK, fontsize=11, loc="left")
    handles = [Patch(facecolor=PAPER_FILLS[k % len(PAPER_FILLS)][0], hatch=PAPER_FILLS[k % len(PAPER_FILLS)][1],
                     edgecolor="#222222", label=t.replace("\n", " ")) for k, t in enumerate(titles)]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.985, 0.5), frameon=False, fontsize=8.5,
               labelcolor=INK2, handleheight=1.4, handlelength=2.2)
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def fig_small_multiples(tab: pd.DataFrame, figure: str, items: list[str], titles: list[str], path: Path,
                        suptitle: str, ncols: int):
    d = tab[tab["figure"] == figure]
    nrows = int(np.ceil(len(items) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.3 * ncols, 2.7 * nrows + 0.9), sharex=True)
    fig.patch.set_facecolor(SURFACE)
    axes = np.atleast_1d(axes).ravel()
    for ax, it, title in zip(axes, items, titles):
        _base(ax)
        s = d[d["item"] == it].set_index("cond").loc[CONDITIONS]
        x = np.arange(4)
        for i, c in enumerate(CONDITIONS):
            st = STYLE[c]
            ax.errorbar(x[i] - 0.09, s["ours"].iloc[i], yerr=s["ci95"].iloc[i], color=st["color"], marker=st["marker"],
                        ms=6.5, lw=1.2, capsize=2.5, markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=3)
            ax.scatter(x[i] + 0.12, s["paper"].iloc[i], marker="D", s=26, facecolor="none", edgecolor=INK, linewidth=1.2, zorder=4)
        lo = float(min((s["ours"] - s["ci95"]).min(), s["paper"].min())) - 0.1
        hi = float(max((s["ours"] + s["ci95"]).max(), s["paper"].max())) + 0.1
        ax.set_ylim(lo, hi)
        ax.set_xlim(-0.55, 3.55)
        ax.set_title(title, color=INK, fontsize=8.5, loc="left")
        ax.tick_params(labelsize=8)
    for ax in axes[len(items):]:
        ax.set_visible(False)
    for ax in axes[max(0, len(items) - ncols): len(items)]:
        ax.set_xticks(range(4), ["Q-eq", "Q-20/80", "R-eq", "R-20/80"], fontsize=8)
    handles = [Line2D([], [], marker="o", color=INK2, lw=1.2, ms=6, label="Replication mean, 95% CI (colour/shape = condition)"),
               Line2D([], [], marker="D", color=INK, lw=0, mfc="none", ms=5.5, label="Article (read from the image, +-0.015)")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=9, labelcolor=INK2)
    fig.suptitle(suptitle, color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def fig_agreement(tab: pd.DataFrame, path: Path):
    """All digitised bars: article value against replication value, and the residuals."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
    fig.patch.set_facecolor(SURFACE)
    spec = {"fig5": ("#2a78d6", "o", "Fig. 5 (3 items)"), "fig6": ("#eb6834", "s", "Fig. 6 (9 items)"),
            "fig7": ("#1baf7a", "^", "Fig. 7 (10 sub-scales, inferred mapping)")}
    _base(a)
    a.plot([1.9, 4.7], [1.9, 4.7], color=INK2, lw=1, ls=":")
    _base(b)
    b.grid(axis="y", visible=False)
    b.grid(axis="x", color=GRID)
    b.axvspan(-TOL, TOL, color=GRID, alpha=0.7, lw=0)
    for k, (fig_, (c, m, lab)) in enumerate(spec.items()):
        d = tab[tab["figure"] == fig_]
        a.scatter(d["paper"], d["ours"], color=c, marker=m, s=34, edgecolor=SURFACE, linewidth=0.7, label=lab, zorder=3)
        jit = np.linspace(-0.25, 0.25, len(d)) if len(d) > 1 else [0]
        b.scatter(d["diff"], np.full(len(d), k) + jit, color=c, marker=m, s=34, edgecolor=SURFACE, linewidth=0.7, zorder=3)
    a.set_xlabel("Article value (read from image)", color=INK2, fontsize=9)
    a.set_ylabel("Replication value", color=INK2, fontsize=9)
    a.set_xlim(1.9, 4.7); a.set_ylim(1.9, 4.7)
    a.set_title("Bar heights", color=INK, fontsize=11, loc="left")
    b.axvline(0, color=INK2, lw=0.8)
    b.set_yticks(range(3), [v[2].split(" (")[0] for v in spec.values()])
    b.invert_yaxis()
    b.set_xlabel("Replication minus article (rating points); grey band = reading error", color=INK2, fontsize=9)
    b.set_title("Differences", color=INK, fontsize=11, loc="left")
    fig.legend(*a.get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False, fontsize=9, labelcolor=INK2)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def fig4_overlay(votes: pd.DataFrame, t1c: pd.DataFrame, path: Path):
    """Replication lines with the article's Table 1 means drawn on top as hollow rings."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    fig.patch.set_facecolor(SURFACE)
    for ax, rnd in zip(axes, (1, 2)):
        _base(ax)
        for c in CONDITIONS:
            st = STYLE[c]
            m = votes[(votes["round"] == rnd) & (votes["cond"] == c)][RATIOS].mean().to_numpy()
            ax.plot(range(4), m, color=st["color"], marker=st["marker"], ls=st["ls"], lw=2, ms=7,
                    markeredgecolor=SURFACE, markeredgewidth=1.2, label=CONDITION_LABELS[c])
            p = t1c[(t1c["round"] == rnd) & (t1c["cond"] == c) & (t1c["stat"] == "mean")].sort_values("choice")["paper"]
            ax.scatter(range(4), p, s=170, facecolor="none", edgecolor=INK, linewidth=1.0, zorder=4)
        ax.set_xticks(range(4), ["1\nCurrent\nmodel", "2\nExtra user\ninfo", "3\nTrack\npreferences", "4\nFlags /\ntags"])
        ax.set_xlim(-0.3, 3.3)
        dm = t1c[(t1c["round"] == rnd) & (t1c["stat"] == "mean")]["diff"].abs().max()
        ax.set_title(f"Round {rnd}: largest |replication - Table 1| = {dm:.4f}", color=INK, fontsize=10, loc="left")
    axes[0].set_ylabel("Mean share of budget allocated", color=INK2, fontsize=9)
    h, l = axes[0].get_legend_handles_labels()
    h.append(Line2D([], [], marker="o", ls="", ms=11, mfc="none", mec=INK, label="Article, Table 1 mean"))
    fig.legend(h, l + ["Article, Table 1 mean"], loc="lower center", ncol=5, frameon=False, fontsize=9, labelcolor=INK2)
    fig.suptitle("Fig. 4: replication against the article's Table 1", color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def build_all(votes, gov, texts, t1, out_dir: Path, tables_dir: Path) -> dict:
    tab = figure_tables(gov)
    tab.to_csv(tables_dir / "compare_figs5_7.csv", index=False)
    t1c = table1_comparison(t1)
    t1c.to_csv(tables_dir / "compare_table1.csv", index=False)
    sub = vdem.subscales(gov)
    vdem.regressions(sub).to_csv(tables_dir / "vdem_regressions_inferred.csv", index=False)

    v7 = list(vdem.VDEM_ITEMS)
    cfg = [
        ("fig5", FIG5_ITEMS, _titles(FIG5_ITEMS, texts), 3, "Fig. 5: perception of the decision process"),
        ("fig6", FIG6_ITEMS, _titles(FIG6_ITEMS, texts), 3, "Fig. 6: perception of the voting mechanism"),
        ("fig7", v7, v7, 5, "Fig. 7: V-Dem sub-scales (item mapping inferred, see docs)"),
    ]
    for f, items, titles, ncols, st in cfg:
        fig_paper_layout_pair(tab, f, items, titles, out_dir / f"{f}_paper_layout_pair.png", f)
        fig_small_multiples(tab, f, items, titles, out_dir / f"{f}_compare_panels.png", st + ": replication against the article", ncols)
    fig_agreement(tab, out_dir / "agreement_figs5_7.png")
    fig4_overlay(votes, t1c, out_dir / "fig4_compare.png")
    return {"tab": tab, "t1c": t1c}


def vdem_text_check(tables_dir: Path) -> pd.DataFrame:
    """Regressions quoted in the text for the V-Dem sub-scales against the inferred mapping."""
    from .paper_values import VDEM_TEXT

    reg = pd.read_csv(tables_dir / "vdem_regressions_inferred.csv")
    rows = []
    for (s, m, t), (coef, p) in VDEM_TEXT.items():
        r = reg[(reg["subscale"] == s) & (reg["model"] == m) & (reg["term"] == t)].iloc[0]
        rows.append({"subscale": s, "model": m, "term": t, "paper_coef": coef, "ours_coef": r["coef"],
                     "paper_p": p, "ours_p": r["p"], "n": r["n"],
                     "coef_match": abs(r["coef"] - coef) < 6e-5, "p_match": abs(r["p"] - p) < 6e-4})
    return pd.DataFrame(rows)
