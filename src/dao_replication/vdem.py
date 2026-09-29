"""V-Dem sub-scales of the governance survey (paper Fig. 7).

The released files do not say which of the 24 `Q3_*` / `Q4_*` statements form
which of the ten sub-scales. This mapping was INFERRED: consecutive item blocks
were searched against the digitised Fig. 7 bar heights and against the
regression coefficients quoted in the text. Seven of ten sub-scale columns match
Fig. 7 within the digitisation error and five text coefficients match exactly
(see docs/FIGURE_COMPARISON.md). It is not an author-supplied mapping.
"""

from __future__ import annotations

import warnings

import pandas as pd
import statsmodels.formula.api as smf

from .config import CONDITIONS

VDEM_ITEMS = {
    "Electoral": ["Q3_1", "Q3_2"],
    "Liberal": ["Q3_3", "Q3_4"],
    "Participatory": ["Q3_5", "Q3_6", "Q3_7"],
    "Deliberative": ["Q3_8", "Q3_9", "Q3_10"],
    "Egalitarian": ["Q3_11", "Q3_12", "Q3_13"],
    "Rule of Law": ["Q4_1", "Q4_2"],
    "Civil Liberties": ["Q4_3", "Q4_4", "Q4_5"],
    "Political Equality": ["Q4_6", "Q4_7"],
    "Civil Society Participation": ["Q4_8", "Q4_9"],
    "Judicial Constraints": ["Q4_10", "Q4_11"],
}


def subscales(gov: pd.DataFrame) -> pd.DataFrame:
    """Row mean of a sub-scale's items; NaN if any item is missing (this is the
    handling that reproduces the text's Judicial Constraints result, n = 180)."""
    out = gov[["cond", "quadratic", "same"]].copy()
    for name, items in VDEM_ITEMS.items():
        out[name] = gov[items].mean(axis=1, skipna=False)
    return out


def condition_means(sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in VDEM_ITEMS:
        for cond in CONDITIONS:
            s = sub.loc[sub["cond"] == cond, name].dropna()
            rows.append({"item": name, "cond": cond, "n": len(s), "mean": s.mean(), "sd": s.std(ddof=1)})
    return pd.DataFrame(rows)


def regressions(sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for name in VDEM_ITEMS:
            d = sub.dropna(subset=[name]).rename(columns={name: "y"})
            for model, f in (("oneway_quadratic", "y ~ quadratic"), ("oneway_same", "y ~ same"),
                             ("additive", "y ~ quadratic + same"), ("interaction", "y ~ quadratic * same")):
                fit = smf.ols(f, d).fit()
                for t in fit.params.index[1:]:
                    rows.append({"subscale": name, "model": model, "term": t, "coef": fit.params[t],
                                 "p": fit.pvalues[t], "n": int(fit.nobs)})
    return pd.DataFrame(rows)
