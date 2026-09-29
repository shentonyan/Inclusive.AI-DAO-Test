"""Tables 2 and 3: Pillai's-trace MANOVA on the four token ratios.

Table 2 in the paper is an additive two-factor model (quadratic + same), even
though the surrounding text calls it "one-way"; the genuine one-way numbers
quoted in the text are produced by `oneway`. Table 3 adds the interaction.
"""

from __future__ import annotations

import warnings

import pandas as pd
from statsmodels.multivariate.manova import MANOVA

from .config import RATIOS

DV = " + ".join(RATIOS)


def pillai(df: pd.DataFrame, rhs: str, dvs: list[str] | None = None) -> pd.DataFrame:
    """Pillai's trace for every non-intercept term of `dvs ~ rhs`."""
    lhs = " + ".join(dvs) if dvs else DV
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = MANOVA.from_formula(f"{lhs} ~ {rhs}", data=df).mv_test()
    rows = []
    for term, tab in res.results.items():
        if term == "Intercept":
            continue
        s = tab["stat"].loc["Pillai's trace"]
        rows.append(
            {
                "term": term,
                "pillai": s["Value"],
                "num_df": s["Num DF"],
                "den_df": s["Den DF"],
                "F": s["F Value"],
                "p": s["Pr > F"],
            }
        )
    return pd.DataFrame(rows)


def _by_round(votes: pd.DataFrame, rhs: str, model: str, dvs=None) -> pd.DataFrame:
    out = []
    for rnd, d in votes.groupby("round"):
        t = pillai(d, rhs, dvs)
        t.insert(0, "round", rnd)
        t.insert(1, "model", model)
        t["n"] = len(d)
        out.append(t)
    return pd.concat(out, ignore_index=True)


def table2(votes: pd.DataFrame) -> pd.DataFrame:
    """Additive two-factor MANOVA (paper Table 2)."""
    return _by_round(votes, "quadratic + same", "additive")


def table3(votes: pd.DataFrame) -> pd.DataFrame:
    """Two-factor MANOVA with interaction (paper Table 3)."""
    return _by_round(votes, "quadratic * same", "interaction")


def oneway(votes: pd.DataFrame) -> pd.DataFrame:
    """Separate one-factor MANOVAs (the numbers quoted in the paper's text)."""
    a = _by_round(votes, "quadratic", "oneway-quadratic")
    b = _by_round(votes, "same", "oneway-same")
    return pd.concat([a, b], ignore_index=True)
