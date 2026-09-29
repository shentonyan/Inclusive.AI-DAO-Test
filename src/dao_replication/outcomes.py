"""What would each condition have decided?

The paper analyses how tokens were *spent*; it never reports which proposal
won under each rule. This module computes that from the released votes.

ASSUMPTION (not stated in the data dictionary): the choice_i columns are token
counts in every condition. Under quadratic voting a participant who spends t
tokens on a choice casts sqrt(t) votes (the paper's own description), so
quadratic conditions are aggregated with sqrt(t); ranked/weighted conditions
are aggregated with t as-is. If the columns in the quadratic files already
hold votes rather than tokens, the "qv_votes" columns are not meaningful and
only the raw-token columns should be read.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import CHOICES, CONDITIONS


def outcomes(votes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (rnd, cond), d in votes.groupby(["round", "cond"]):
        tokens = d[CHOICES].sum()
        if cond.startswith("quadratic"):
            eff = np.sqrt(d[CHOICES]).sum()
            rule = "sqrt(tokens) per person"
        else:
            eff = tokens.astype(float)
            rule = "tokens"
        row = {"round": rnd, "cond": cond, "n": len(d), "rule": rule}
        for c in CHOICES:
            row[f"tokens_{c[-1]}"] = int(tokens[c])
        for c in CHOICES:
            row[f"effective_share_{c[-1]}"] = eff[c] / eff.sum()
        row["winner_by_tokens"] = int(tokens.values.argmax()) + 1
        row["winner_by_rule"] = int(eff.values.argmax()) + 1
        rows.append(row)
    out = pd.DataFrame(rows)
    out["cond"] = pd.Categorical(out["cond"], CONDITIONS, ordered=True)
    return out.sort_values(["round", "cond"]).reset_index(drop=True)
