"""Table 1: mean and SD of the token ratio per choice, by round and condition."""

from __future__ import annotations

import pandas as pd

from .config import CONDITIONS, RATIOS


def table1(votes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rnd, d_round in votes.groupby("round"):
        for cond in CONDITIONS:
            d = d_round[d_round["cond"] == cond]
            row = {"round": rnd, "cond": cond, "n": len(d)}
            for r in RATIOS:
                row[f"mean_{r}"] = d[r].mean()
                row[f"sd_{r}"] = d[r].std(ddof=1)
            row["mean_sum"] = sum(row[f"mean_{r}"] for r in RATIOS)
            rows.append(row)
    return pd.DataFrame(rows)
