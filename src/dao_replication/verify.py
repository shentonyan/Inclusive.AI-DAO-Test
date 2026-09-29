"""Compare every reproducible number in the paper with what the released data give."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import pandas as pd
import statsmodels.formula.api as smf

from . import paper_values as pv
from .config import CHOICES, RATIOS
from .data import REVERSE_ITEMS
from .manova import oneway, table2, table3
from .survey import item_regressions
from .table1 import table1


@dataclass
class Check:
    group: str
    name: str
    paper: float
    computed: float
    tol: float
    note: str = ""  # set when a mismatch is a documented discrepancy in the article

    @property
    def ok(self) -> bool:
        return abs(self.paper - self.computed) <= self.tol

    @property
    def explained(self) -> bool:
        """Mismatch that is documented in paper_values.DOCUMENTED_MISMATCHES."""
        return (not self.ok) and bool(self.note)

    @property
    def diff(self) -> float:
        return self.computed - self.paper


def _tol(decimals: int) -> float:
    """One unit in the last printed digit (covers rounding and truncation)."""
    return 10.0**-decimals + 1e-9


def run_checks(votes: pd.DataFrame, gov: pd.DataFrame) -> list[Check]:
    out: list[Check] = []

    # Table 1
    t1 = table1(votes).set_index(["round", "cond"])
    for (rnd, cond), (n, means, sds, dec) in pv.TABLE1.items():
        row = t1.loc[(rnd, cond)]
        out.append(Check("Table 1", f"R{rnd} {cond} n", n, float(row["n"]), 0.0))
        for i, r in enumerate(RATIOS):
            out.append(Check("Table 1", f"R{rnd} {cond} mean choice {i+1}", means[i], float(row[f"mean_{r}"]), _tol(dec)))
            out.append(Check("Table 1", f"R{rnd} {cond} sd choice {i+1}", sds[i], float(row[f"sd_{r}"]), _tol(dec)))

    # Tables 2 and 3
    for label, paper, table in (("Table 2", pv.TABLE2, table2(votes)), ("Table 3", pv.TABLE3, table3(votes))):
        t = table.set_index(["round", "term"])
        for (rnd, term), (v, ndf, ddf, f, p) in paper.items():
            row = t.loc[(rnd, term)]
            base = f"R{rnd} {term}"
            out.append(Check(label, f"{base} Pillai", v, float(row["pillai"]), _tol(4)))
            out.append(Check(label, f"{base} num df", ndf, float(row["num_df"]), 0.0))
            out.append(Check(label, f"{base} den df", ddf, float(row["den_df"]), 0.0))
            out.append(Check(label, f"{base} F", f, float(row["F"]), _tol(4)))
            out.append(Check(label, f"{base} p", p, float(row["p"]), _tol(4)))

    # One-way MANOVA quoted in the text
    ow = oneway(votes).set_index(["round", "term"])
    for (rnd, term), (v, p) in pv.ONEWAY_TEXT.items():
        row = ow.loc[(rnd, term)]
        out.append(Check("One-way (text)", f"R{rnd} {term} Pillai", v, float(row["pillai"]), _tol(4)))
        out.append(Check("One-way (text)", f"R{rnd} {term} p", p, float(row["p"]), _tol(4)))

    # Regression of ratio on voting method
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for rnd, coefs in pv.QUADRATIC_COEF.items():
            d = votes[votes["round"] == rnd]
            for i, r in enumerate(RATIOS):
                b = smf.ols(f"{r} ~ quadratic", data=d).fit().params["quadratic"]
                out.append(Check("Ratio ~ quadratic", f"R{rnd} choice {i+1}", coefs[i], float(b), _tol(4)))

    # Survey regressions
    reg = item_regressions(gov).set_index(["item", "model", "term"])
    for key, (coef, p) in pv.SURVEY_REG.items():
        row = reg.loc[key]
        out.append(Check("Survey regression", f"{key[0]} {key[1]} coef", coef, float(row["coef"]), _tol(4)))
        out.append(Check("Survey regression", f"{key[0]} {key[1]} p", p, float(row["p"]), _tol(3)))

    # Fig. 5 numbers in the text (equal-power conditions pooled)
    eq = gov[gov["same"] == 1]
    for label, (item, rev, mean, sd) in pv.FIG5_TEXT.items():
        x = 6 - eq[item] if rev else eq[item]
        out.append(Check("Fig. 5 (text)", f"{label} mean", mean, float(x.mean()), _tol(2)))
        out.append(Check("Fig. 5 (text)", f"{label} sd", sd, float(x.std(ddof=1)), _tol(2)))
    for c in out:
        key = (c.group, c.name)
        if key in pv.DOCUMENTED_MISMATCHES:
            c.note = pv.DOCUMENTED_MISMATCHES[key]
    return out


def computed_mismatch_details(gov: pd.DataFrame) -> pd.DataFrame:
    """The survey statistics the text quotes but the data do not give."""
    rows = []
    for item, mean, sd in (("Q2_1", 4.14, 0.815), ("Q2_3", 4.03, 0.92)):
        rows.append(
            {
                "item": item,
                "paper_mean": mean,
                "paper_sd": sd,
                "data_mean": round(gov[item].mean(), 2),
                "data_sd": round(gov[item].std(ddof=1), 2),
                "n": int(gov[item].notna().sum()),
            }
        )
    return pd.DataFrame(rows)


def to_markdown(checks: list[Check], extra: dict[str, pd.DataFrame] | None = None) -> str:
    df = pd.DataFrame(
        [
            {"group": c.group, "check": c.name, "paper": c.paper, "computed": round(c.computed, 6), "diff": round(c.diff, 6), "ok": c.ok, "note": c.note}
            for c in checks
        ]
    )
    lines = ["# Verification report", ""]
    summary = df.groupby("group", sort=False)["ok"].agg(["sum", "count"])
    lines += ["| Group | Matched | Total |", "|---|---:|---:|"]
    for g, r in summary.iterrows():
        lines.append(f"| {g} | {int(r['sum'])} | {int(r['count'])} |")
    n_ok = int(df["ok"].sum())
    lines += [
        "",
        f"**{n_ok} of {len(df)} numbers match** (tolerance: one unit in the last printed digit).",
        "",
    ]

    bad = df[~df["ok"]].drop(columns=["ok"])
    if len(bad):
        lines += [f"## Numbers that do not match ({len(bad)})", "", bad.to_markdown(index=False), ""]
    else:
        lines += ["No mismatches among the numbers checked.", ""]

    lines += ["## Known discrepancies in the article", ""]
    lines += [f"- {m}" for m in pv.KNOWN_MISMATCHES]
    lines += ["", "## Not testable with the released files", ""]
    lines += [f"- {m}" for m in pv.NOT_TESTABLE]
    for title, table in (extra or {}).items():
        lines += ["", f"## {title}", "", table.to_markdown(index=False), ""]
    return "\n".join(lines) + "\n"
