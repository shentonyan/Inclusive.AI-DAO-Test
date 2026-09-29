"""Loading and light cleaning of the OSF files.

Nothing here alters a value; it only renames columns, parses Likert text into
numbers and derives the analysis variables used in the paper.
"""

from __future__ import annotations

import re

import pandas as pd

from .config import CHOICES, CONDITIONS, RATIOS, data_path

# Reverse-worded items in the governance survey. The paper's regression
# coefficients are computed on the RAW scores, while its bar charts (Figs 5-6)
# show these items reversed (so "indecisive" is displayed as "decisive").
REVERSE_ITEMS = ["Q1_1", "Q1_2", "Q2_10"]


def _add_design_columns(df: pd.DataFrame, cond_col: str) -> pd.DataFrame:
    df = df.copy()
    df["cond"] = df[cond_col]
    unknown = set(df["cond"]) - set(CONDITIONS)
    if unknown:
        raise ValueError(f"Unexpected condition labels: {unknown}")
    df["quadratic"] = df["cond"].str.startswith("quadratic").astype(int)
    df["same"] = df["cond"].str.endswith("equal").astype(int)  # 1 = equal power, 0 = 20/80
    return df


def load_votes(include_pilots: bool = True) -> pd.DataFrame:
    """Both voting files stacked, with the paper's design and ratio variables.

    Columns added
    -------------
    round      1 or 2 (paper numbering; round 2 comes from the file named "round3")
    phase      "main" for round 1; the file's own phase label for round 2
    quadratic  1 = quadratic voting, 0 = ranked (weighted) voting
    same       1 = equal voting power, 0 = 20/80 power
    r1..r4     choice_i / votes_given (this is what reproduces Table 1)
    allocated  sum of the four choice columns
    unspent    votes_given - allocated
    """
    r1 = pd.read_csv(data_path("vote_round1")).rename(columns={"pod-categorical": "cond0"})
    r1["round"] = 1
    r1["phase"] = "main"
    r1 = r1.rename(columns={"pod": "pod_index"})
    r1["user"] = r1["user"].astype(str)
    r1 = _add_design_columns(r1, "cond0")

    r2 = pd.read_csv(data_path("vote_round2")).rename(columns={"pod": "cond0"})
    r2["round"] = 2
    r2["user"] = [f"R2_{i:03d}" for i in range(len(r2))]  # file has no ids
    r2 = _add_design_columns(r2, "cond0")
    if not include_pilots:
        r2 = r2[r2["phase"] != "pilots"]

    cols = ["round", "phase", "user", "cond", "quadratic", "same", "votes_given", *CHOICES]
    votes = pd.concat([r1[cols], r2[cols]], ignore_index=True)

    if (votes["votes_given"] <= 0).any():
        raise ValueError("votes_given must be positive")
    for c, r in zip(CHOICES, RATIOS):
        votes[r] = votes[c] / votes["votes_given"]
    votes["allocated"] = votes[CHOICES].sum(axis=1)
    votes["unspent"] = votes["votes_given"] - votes["allocated"]
    return votes


def _likert(series: pd.Series) -> pd.Series:
    """'4: Agree' -> 4.0 ; '5:Strongly Agree' -> 5.0 ; anything else -> NaN."""
    return series.astype(str).str.extract(r"^\s*(\d)\s*:")[0].astype(float)


def load_gov_survey() -> tuple[pd.DataFrame, dict[str, str]]:
    """Governance-perception survey (Q1_*: process, Q2_*: mechanism, Q3_/Q4_*: quality).

    The CSV's first data row is the Qualtrics question text; it is removed and
    returned as a {column: statement} dict.
    """
    raw = pd.read_csv(data_path("gov_survey"))
    header = raw[raw["pod"].isna()].iloc[0]
    items = [c for c in raw.columns if c != "pod"]
    texts = {c: re.sub(r"^.*? - ", "", str(header[c])) for c in items}

    df = raw[raw["pod"].notna()].copy().reset_index(drop=True)
    for c in items:
        df[c] = _likert(df[c])
    df = _add_design_columns(df, "pod")
    return df, texts


def load_value_survey() -> pd.DataFrame:
    """AI-value survey (q1A-G, q2A-K), numeric 1-5."""
    df = pd.read_csv(data_path("value_survey"))
    return _add_design_columns(df, "pod")


def load_text(key: str) -> pd.DataFrame:
    """'human_ai_chat' or 'group_discussion'."""
    return pd.read_csv(data_path(key))
