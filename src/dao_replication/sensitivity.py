"""Sensitivity analyses that go beyond what the paper reports.

Motivation (see docs/REPRODUCIBILITY.md):
  * the four ratios r1..r4 are divided by the budget, not by tokens actually
    spent, so 23 of 177 rows leave part of the budget unallocated;
  * in the round-2 rows that fully allocate, r1+r2+r3+r4 = 1 exactly, so a
    four-variable MANOVA is rank deficient there;
  * the round-2 file contains 8 rows labelled "pilots".
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import CHOICES, RATIOS, SEED
from .manova import pillai

# ---------------------------------------------------------------- variants


def _alr(shares: pd.DataFrame, ref: str = "r3", pseudo: float = 0.5) -> pd.DataFrame:
    """Additive log-ratio coordinates with a pseudo-count for zeros.

    `shares` are token counts (not ratios). Adding `pseudo` tokens to every
    cell before closing is a crude but transparent zero replacement.
    """
    x = shares + pseudo
    x = x.div(x.sum(axis=1), axis=0)
    others = [c for c in x.columns if c != ref]
    out = pd.DataFrame({f"alr_{c}": np.log(x[c] / x[ref]) for c in others}, index=x.index)
    return out


def manova_variants(votes: pd.DataFrame) -> pd.DataFrame:
    """Additive (Table 2-style) Pillai tests under alternative data treatments."""
    rows = []

    def add(label: str, d: pd.DataFrame, dvs: list[str]):
        for rnd, dd in d.groupby("round"):
            use = list(dvs)
            # If the ratios sum to exactly 1 in every row the 4-vector is
            # rank deficient (3 free dimensions); statsmodels would then return
            # numerically arbitrary results, so the last component is dropped.
            closed = set(dvs) == set(RATIOS) and bool(np.allclose(dd[dvs].sum(axis=1), 1.0))
            if closed:
                use = dvs[:-1]
            t = pillai(dd, "quadratic + same", use)
            t.insert(0, "round", rnd)
            t.insert(1, "variant", label)
            t["n"] = len(dd)
            t["n_dvs"] = len(use)
            t["closed_composition"] = closed
            rows.append(t)

    # 1. as published
    add("published (ratios of budget)", votes, RATIOS)

    # 2. drop the 8 rows labelled "pilots" (round 2 only)
    add("excluding rows labelled 'pilots'", votes[votes["phase"] != "pilots"], RATIOS)

    # 3. rows that spent the whole budget only
    full = votes[votes["unspent"] == 0]
    add("fully allocated rows only", full, RATIOS)

    # 4. shares of tokens actually spent
    shares = votes.copy()
    for c, r in zip(CHOICES, RATIOS):
        shares[r] = shares[c] / shares["allocated"]
    add("shares of tokens spent", shares, RATIOS)

    # 5. drop one component so the DV vector is not (near) collinear
    add("published ratios, choice 4 dropped (3 DVs)", votes, RATIOS[:3])

    # 6. log-ratio coordinates (3 DVs), zero handled by +0.5 token
    alr = _alr(votes[CHOICES].rename(columns=dict(zip(CHOICES, RATIOS))))
    va = pd.concat([votes.drop(columns=RATIOS), alr], axis=1)
    add("additive log-ratio, ref = choice 3 (3 DVs)", va, list(alr.columns))

    out = pd.concat(rows, ignore_index=True)
    return out[out["term"].isin(["quadratic", "same"])].reset_index(drop=True)


# ------------------------------------------------------ permutation tests


def _pillai_two_group(Y: np.ndarray, g: np.ndarray) -> float:
    """Pillai's trace for a two-group comparison (rank-1 hypothesis)."""
    n1 = int(g.sum())
    n0 = len(g) - n1
    Y1, Y0 = Y[g == 1], Y[g == 0]
    d = Y1.mean(axis=0) - Y0.mean(axis=0)
    E = (Y1 - Y1.mean(axis=0)).T @ (Y1 - Y1.mean(axis=0)) + (Y0 - Y0.mean(axis=0)).T @ (Y0 - Y0.mean(axis=0))
    lam = (n1 * n0 / len(g)) * float(d @ np.linalg.pinv(E) @ d)
    return lam / (1.0 + lam)


def permutation_pillai(votes: pd.DataFrame, n_perm: int = 10_000, seed: int = SEED) -> pd.DataFrame:
    """Marginal permutation test for each factor (labels shuffled), 4 DVs.

    This does not rely on multivariate normality, which the bounded, zero-heavy
    token ratios clearly violate. The observed statistic equals the paper's
    one-way Pillai value.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for rnd, d in votes.groupby("round"):
        Y = d[RATIOS].to_numpy(float)
        for factor in ["quadratic", "same"]:
            g = d[factor].to_numpy(int)
            obs = _pillai_two_group(Y, g)
            exceed = 0
            for _ in range(n_perm):
                if _pillai_two_group(Y, rng.permutation(g)) >= obs - 1e-12:
                    exceed += 1
            rows.append(
                {
                    "round": rnd,
                    "factor": factor,
                    "pillai": obs,
                    "p_permutation": (1 + exceed) / (n_perm + 1),
                    "n_perm": n_perm,
                    "n": len(d),
                }
            )
    return pd.DataFrame(rows)


# ------------------------------------------------------------- bookkeeping


def unspent_summary(votes: pd.DataFrame) -> pd.DataFrame:
    """How many rows leave part of the budget unallocated, by round and phase."""
    g = votes.assign(
        under=(votes["unspent"] > 0).astype(int),
        over=(votes["unspent"] < 0).astype(int),
        unspent_share=votes["unspent"] / votes["votes_given"],
    )
    return (
        g.groupby(["round", "phase"])
        .agg(
            n=("user", "size"),
            n_underallocated=("under", "sum"),
            n_overallocated=("over", "sum"),
            mean_unspent_share=("unspent_share", "mean"),
        )
        .reset_index()
    )


def sample_sizes(votes: pd.DataFrame, gov: pd.DataFrame, value: pd.DataFrame) -> pd.DataFrame:
    """Every place the paper's N can be checked against the released files."""
    rows = [
        ("vote files, round 1", int((votes["round"] == 1).sum())),
        ("vote files, round 2 (file 'round3', incl. pilots)", int((votes["round"] == 2).sum())),
        ("vote files, total (paper: 177)", len(votes)),
        ("governance survey respondents", len(gov)),
        ("AI-value survey respondents", len(value)),
    ]
    return pd.DataFrame(rows, columns=["source", "n"])


def pooled_with_round(votes: pd.DataFrame) -> pd.DataFrame:
    """Both rounds in one MANOVA with a round fixed effect (not in the paper)."""
    t = pillai(votes, "quadratic * same + C(round)")
    t["n"] = len(votes)
    return t
