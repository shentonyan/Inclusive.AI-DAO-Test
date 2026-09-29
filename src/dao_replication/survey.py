"""Item-level regressions on the governance survey (paper Section "Quality of
democratic governance decision-making process").

The paper's reported coefficients for Q1_1, Q1_2 and Q2_10 come from
single-predictor OLS fits on the raw 1-5 scores (n = 182), and the
interaction coefficient quoted for Q2_1 from the two-factor model with
interaction; both are reproduced here.

The ten V-Dem sub-scales in the paper's Fig. 7 are rebuilt in vdem.py from an INFERRED mapping: the
mapping from the 24 Q3_/Q4_ statements to sub-scales is not in the released files.
"""

from __future__ import annotations

import warnings

import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from .config import CONDITIONS
from .data import REVERSE_ITEMS

FIG5_ITEMS = ["Q1_1", "Q1_2", "Q1_3"]
FIG6_ITEMS = ["Q2_1", "Q2_3", "Q2_4", "Q2_5", "Q2_6", "Q2_7", "Q2_8", "Q2_9", "Q2_10"]
ANALYSED_ITEMS = FIG5_ITEMS + FIG6_ITEMS

MODELS = {
    "oneway_quadratic": "{y} ~ quadratic",
    "oneway_same": "{y} ~ same",
    "additive": "{y} ~ quadratic + same",
    "interaction": "{y} ~ quadratic * same",
}


def item_regressions(gov: pd.DataFrame, items: list[str] | None = None) -> pd.DataFrame:
    """Tidy table: one row per item x model x term (intercept excluded)."""
    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for y in items or ANALYSED_ITEMS:
            d = gov.dropna(subset=[y])
            for name, tmpl in MODELS.items():
                fit = smf.ols(tmpl.format(y=y), data=d).fit()
                for term in fit.params.index:
                    if term == "Intercept":
                        continue
                    rows.append(
                        {
                            "item": y,
                            "model": name,
                            "term": term,
                            "coef": fit.params[term],
                            "se": fit.bse[term],
                            "p": fit.pvalues[term],
                            "n": int(fit.nobs),
                        }
                    )
    return pd.DataFrame(rows)


def add_multiplicity(reg: pd.DataFrame) -> pd.DataFrame:
    """Holm and Benjamini-Hochberg adjustment within each (model, term) family
    of item-level tests. The paper reports none."""
    out = reg.copy()
    out["p_holm"] = float("nan")
    out["p_bh"] = float("nan")
    for _, idx in out.groupby(["model", "term"]).groups.items():
        p = out.loc[idx, "p"].to_numpy()
        out.loc[idx, "p_holm"] = multipletests(p, method="holm")[1]
        out.loc[idx, "p_bh"] = multipletests(p, method="fdr_bh")[1]
    return out


def condition_means(gov: pd.DataFrame, items: list[str] | None = None, reverse: bool = True) -> pd.DataFrame:
    """Mean and SD per item and condition. With reverse=True the reverse-worded
    items are flipped (6 - x) as in the paper's Figs 5-6."""
    rows = []
    for y in items or ANALYSED_ITEMS:
        x = gov[y]
        if reverse and y in REVERSE_ITEMS:
            x = 6 - x
        for cond in CONDITIONS:
            s = x[gov["cond"] == cond].dropna()
            rows.append({"item": y, "cond": cond, "n": len(s), "mean": s.mean(), "sd": s.std(ddof=1)})
    return pd.DataFrame(rows)
