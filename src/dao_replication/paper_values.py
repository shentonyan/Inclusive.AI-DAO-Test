"""Numbers printed in Sharma et al. (2026), Sci. Rep. 16:11792, transcribed from
the article text and tables. `decimals` is the number of decimals printed, which
sets the tolerance used when comparing (one unit in the last printed digit).
"""

from __future__ import annotations

# ---- Table 1 ---------------------------------------------------------------
# (round, condition) -> (n, means[4], sds[4], decimals)
TABLE1 = {
    (1, "quadratic-equal"): (26, [0.1627, 0.1596, 0.3219, 0.2580], [0.1519, 0.1352, 0.2086, 0.1967], 4),
    (1, "quadratic-early"): (24, [0.0901, 0.1493, 0.3358, 0.2646], [0.1415, 0.1549, 0.2111, 0.2473], 4),
    (1, "ranked-equal"): (27, [0.1478, 0.2548, 0.3200, 0.2100], [0.1695, 0.1614, 0.1953, 0.1679], 4),
    (1, "ranked-early"): (25, [0.1133, 0.2800, 0.3005, 0.2342], [0.2102, 0.2120, 0.2282, 0.1689], 4),
    (2, "quadratic-equal"): (20, [0.121, 0.210, 0.282, 0.332], [0.172, 0.140, 0.174, 0.201], 3),
    (2, "quadratic-early"): (19, [0.108, 0.210, 0.321, 0.344], [0.143, 0.207, 0.183, 0.201], 3),
    (2, "ranked-equal"): (18, [0.053, 0.177, 0.363, 0.407], [0.065, 0.165, 0.238, 0.240], 3),
    (2, "ranked-early"): (18, [0.107, 0.278, 0.381, 0.223], [0.167, 0.164, 0.231, 0.127], 3),
}

# ---- Table 2 (additive) and Table 3 (interaction) ---------------------------
# (round, term) -> (pillai, num_df, den_df, F, p)
TABLE2 = {
    (1, "quadratic"): (0.1100, 4, 96, 2.9677, 0.0233),
    (1, "same"): (0.0259, 4, 96, 0.6373, 0.6372),
    (2, "quadratic"): (0.0584, 4, 69, 1.0689, 0.3786),
    (2, "same"): (0.0551, 4, 69, 1.0056, 0.4107),
}
TABLE3 = {
    (1, "quadratic"): (0.0763, 4, 95, 1.9612, 0.1067),
    (1, "same"): (0.0094, 4, 95, 0.2249, 0.9239),
    (1, "quadratic:same"): (0.0090, 4, 95, 0.2153, 0.9293),
    (2, "quadratic"): (0.0578, 4, 68, 1.0432, 0.3915),
    (2, "same"): (0.1136, 4, 68, 2.1790, 0.0806),
    (2, "quadratic:same"): (0.0804, 4, 68, 1.4869, 0.2158),
}

# ---- One-way MANOVA quoted in the text ---------------------------------------
# (round, term) -> (pillai, p)
ONEWAY_TEXT = {
    (1, "quadratic"): (0.1100, 0.0222),
    (2, "quadratic"): (0.0583, 0.3714),
    (1, "same"): (0.0259, 0.6325),
    (2, "same"): (0.0550, 0.4034),
}

# ---- Regression of token ratio on the voting method --------------------------
# round -> coefficients of `quadratic` for r1..r4
QUADRATIC_COEF = {
    1: [-0.0034, -0.1123, 0.0180, 0.0396],
    2: [0.0345, -0.0178, -0.0716, 0.0228],
}

# ---- Survey regressions (n = 182) --------------------------------------------
# (item, model, term) -> (coef, p)
SURVEY_REG = {
    ("Q1_1", "oneway_same", "same"): (-0.4261, 0.000),
    ("Q1_2", "oneway_same", "same"): (-0.3056, 0.046),
    ("Q1_2", "oneway_quadratic", "quadratic"): (-0.3297, 0.031),
    ("Q2_10", "oneway_same", "same"): (-0.9719, 0.000),
    ("Q2_1", "interaction", "quadratic:same"): (0.6247, 0.003),
}

# ---- Fig. 5 numbers quoted in the text (equal-power conditions pooled) -------
# label -> (item, reversed, mean, sd)
FIG5_TEXT = {
    "decisive": ("Q1_1", True, 4.12, 0.74),
    "maintains order": ("Q1_2", True, 3.93, 1.00),
    "better than any other government": ("Q1_3", False, 3.85, 0.73),
}

# ---- Individual printed numbers the data do not reproduce ---------------------
# (group, check name) -> explanation. Used by verify.py to tell a documented
# discrepancy from a genuine failure of this code.
DOCUMENTED_MISMATCHES = {
    ("Table 1", "R2 quadratic-equal sd choice 4"): "printed 0.201; data give 0.209 (same value printed for the 20/80 row)",
    ("Table 1", "R2 quadratic-early sd choice 4"): "printed 0.201; data give 0.209 (same value printed for the equal row)",
}

# ---- Statements the released data contradict or cannot test ------------------
KNOWN_MISMATCHES = [
    "Table 1, round 2: the SD of choice 4 is printed as 0.201 in both quadratic rows; the data "
    "give 0.209 for both, so one printed value looks like a transcription error. All other "
    "Table 1 entries match.",
    "Sample size: votes n=177 (102+75) but the governance survey has 182 respondents, "
    "the AI-value survey 183, and the demographic percentages imply a denominator of 184.",
    "Round 2 is described as blind US participants; Table 1 (round 2) is reproduced only "
    "when 8 rows labelled 'pilots' in the file named 'round3' are included.",
    "Text says the round-2 voting-power effect is significant (Pillai 0.11, P=0.08); "
    "Table 3 gives P=0.0806, which is not significant at 0.05.",
    "Text: mean 4.14 (SD 0.815) for 'voting method meaningful' and 4.03 (SD 0.92) for "
    "'voting method relevant'; the released survey gives 4.17 (0.71) and 4.19 (0.77) on n=182.",
]

NOT_TESTABLE = [
    "V-Dem sub-scale results (Fig. 7 and regressions on Electoral, Liberal, ... Judicial "
    "Constraints): the mapping from the 24 Q3_/Q4_ statements to the ten sub-scales is not "
    "in the released files.",
    "Fig. 8 correlations: the two survey files have no participant id and their rows do not "
    "align (about 19% agreement in condition labels at equal row index).",
    "Fig. 3 satisfaction items, demographics and the LLM-usage figure: not in the released files.",
    "Fig. 9 clustering: used OpenAI Ada-2 embeddings (needs an API key). A TF-IDF substitute was tried "
    "and dropped: k-means isolated groups of identical short messages and left 4,557 of 5,057 in one cluster.",
]

# ---- V-Dem sub-scale regressions quoted in the text --------------------------
# (subscale, model, term) -> (coef, p, decimals); used with the INFERRED item mapping.
VDEM_TEXT = {
    ("Electoral", "oneway_same", "same"): (0.2787, 0.0011),
    ("Liberal", "oneway_quadratic", "quadratic"): (-0.2143, 0.0595),
    ("Participatory", "oneway_quadratic", "quadratic"): (-0.2234, 0.0439),
    ("Civil Liberties", "oneway_quadratic", "quadratic"): (-0.1978, 0.0219),
    ("Judicial Constraints", "oneway_quadratic", "quadratic"): (-0.2051, 0.0808),
    ("Political Equality", "oneway_quadratic", "quadratic"): (0.2582, 0.058),
    ("Deliberative", "interaction", "quadratic:same"): (0.6029, 0.033),
}
# Not reproduced with the inferred mapping (coefficient, p): see docs/FIGURE_COMPARISON.md.
VDEM_UNRESOLVED = {("Political Equality", "oneway_quadratic", "quadratic"): "coefficient matches, p differs",
                   ("Deliberative", "interaction", "quadratic:same"): "no match"}

# ---- Fig. 3 percentages as printed in the caption text --------------------------
# statement -> {category: percent}; the caption gives no value for categories it omits.
FIG3_TEXT = {
    "experience": {"Strongly Agree": 46.4, "Agree": 39.1, "Somewhat Agree": 10.9, "Neutral": 1.4,
                   "Somewhat Disagree": 0.7, "Strongly Disagree": 1.5},
    "trust": {"Strongly Agree": 25.4, "Agree": 47.1, "Somewhat Agree": 13.0, "Neutral": 11.6,
              "Somewhat Disagree": 7.2, "Disagree": 0.2},
    "contributions": {"Strongly Agree": 44.9, "Agree": 36.2, "Somewhat Agree": 9.4, "Neutral": 7.2,
                      "Somewhat Disagree": 1.4, "Disagree": 0.7},
}
