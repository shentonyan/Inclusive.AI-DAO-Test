"""Read the numbers behind the article's Fig. 3 and Fig. 8 from the article PDF.

Optional tooling (needs PyMuPDF and your own copy of the article PDF, which is not
redistributed here). Both figures are vector graphics or live text in the PDF, so
the values are exact rather than measured from pixels:

* Fig. 3: the widths of the filled bar segments give each answer category's share.
* Fig. 8: every printed correlation is a text span; its x/y position gives the
  cell (22 columns spaced 12.55 pt from x = 241.75, 18 rows spaced 7.705 pt from
  y = 56.08). Cells with |r| < 0.1 are not printed in the article.

    python -m dao_replication.paper_extract path/to/article.pdf
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[2] / "data" / "paper_figures"

FIG3_COLOURS = {
    (0.48, 0.76, 0.74): "Strongly Agree", (0.74, 0.88, 0.87): "Agree", (0.83, 0.83, 0.83): "Somewhat Agree",
    (0.94, 0.88, 0.76): "Neutral", (0.87, 0.76, 0.51): "Somewhat Disagree", (0.85, 0.65, 0.22): "Disagree",
}
FIG3_BARS = {60: "contributions", 97: "trust", 133: "experience"}  # by y position on page 5
FIG3_X_LEFT, FIG3_X_RIGHT = 181.01, 469.83  # 0 % and 100 % of the axis

FIG8_ROWS = [
    "Prioritizing generating diverse outputs", "Customization options, like specifying gender or ethnicity",
    "A diverse dataset in AI training for fair representation", "Uncertainty handling to avoid assumptions and ensure diversity",
    "Feedback loops with users to ensure inclusivity", "Ethical considerations, like avoiding stereotypes",
    "Prioritizing cultural diversity and gender", "The use case is not relevant to me",
    "I feel AI could infringe on my representation", "I do not fully trust in the abilities of AI model",
    "Use case is too important to let the AI model decide", "I love organizing, and deciding everything myself",
    "Not be clear how decisions are produced by AI", "AI in general would treat me fairly",
    "I believe AI actor would take necessary measures", "I believe that AI would not intentionally harm me",
    "I am better off with decisions made by AI", "I would be willing to let AI help me",
]
# The 18 rows are assumed to be the value-survey columns in file order (q1A-G, q2A-K).
FIG8_VALUE_COLS = ["q1A", "q1B", "q1C", "q1D", "q1E", "q1F", "q1G"] + ["q2" + c for c in "ABCDEFGHIJK"]
FIG8_COLS = ["Q1_1", "Q1_2", "Q1_3", "Q2_1", "Q2_3", "Q2_4", "Q2_5", "Q2_6", "Q2_7", "Q2_8", "Q2_9", "Q2_10",
             "Electoral", "Liberal", "Participatory", "Deliberative", "Egalitarian", "Rule of Law",
             "Civil Liberties", "Political Equality", "Civil Society Participation", "Judicial Constraints"]


def extract_fig3(pdf: str) -> pd.DataFrame:
    import pymupdf

    pg = pymupdf.open(pdf)[4]
    width = FIG3_X_RIGHT - FIG3_X_LEFT
    segs = collections.defaultdict(dict)
    for dr in pg.get_drawings():
        r = dr["rect"]
        if dr.get("fill") and abs(r.height - 18.3) < 0.3 and 40 < r.y0 < 260:
            c = tuple(round(x, 2) for x in dr["fill"])
            if c in FIG3_COLOURS:
                segs[round(r.y0)][FIG3_COLOURS[c]] = 100 * (r.x1 - r.x0) / width
    rows = []
    for y, name in FIG3_BARS.items():
        d = segs[y]
        d["Strongly Disagree"] = max(0.0, 100 - sum(d.values()))  # drawn in white, so found as the remainder
        for cat, pct in d.items():
            rows.append({"statement": name, "category": cat, "pct_figure": round(pct, 3)})
    return pd.DataFrame(rows)


def _spans(pg):
    items = []
    for b in pg.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                x0, y0, x1, y1 = s["bbox"]
                t = s["text"].replace("−", "-")
                if y0 < 200 and x0 < 535 and t.strip() and re.fullmatch(r"[\d.\- ]+", t) and x1 - x0 < 40:
                    items.append([x0, x1, round(y0, 1), t.strip()])
    items.sort(key=lambda z: (z[2], z[0]))
    out, cur = [], None
    for x0, x1, y, t in items:  # some numbers are stored one character per span
        if cur and cur[2] == y and x0 - cur[1] < 1.2:
            cur[1], cur[3] = x1, cur[3] + t
        else:
            if cur:
                out.append(cur)
            cur = [x0, x1, y, t]
    if cur:
        out.append(cur)
    return [(float(c[3]), (c[0] + c[1]) / 2, c[2] + 3.9) for c in out if re.fullmatch(r"-?\d*\.\d+", c[3])]


def extract_fig8(pdf: str) -> pd.DataFrame:
    import pymupdf

    r = np.array(_spans(pymupdf.open(pdf)[9]))
    col = np.round((r[:, 1] - 241.75) / 12.55).astype(int)
    row = np.round((r[:, 2] - 56.08) / 7.705).astype(int)
    m = np.full((18, 22), np.nan)
    for v, i, j in zip(r[:, 0], row, col):
        m[i, j] = v
    df = pd.DataFrame(m, index=FIG8_VALUE_COLS, columns=FIG8_COLS)
    df.insert(0, "row_label", FIG8_ROWS)
    return df


def main(pdf: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    extract_fig3(pdf).to_csv(OUT / "fig3_segments.csv", index=False)
    extract_fig8(pdf).to_csv(OUT / "fig8_printed_cells.csv")


if __name__ == "__main__":
    main(sys.argv[1])
