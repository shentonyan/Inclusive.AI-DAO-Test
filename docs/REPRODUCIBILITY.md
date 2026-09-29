# Reproducibility notes

**English** | [简体中文](REPRODUCIBILITY.zh-CN.md)

Article: Sharma, T., Potter, Y., Park, J., Liu, Y., Huang, Y., Liu, S., Song, D.,
Hancock, J. & Wang, Y. *Democratic governance through DAO-based deliberation and
voting for inclusive decision making in AI models.* Scientific Reports 16, 11792
(2026). <https://doi.org/10.1038/s41598-026-40180-8>

This is an independent re-analysis of the released OSF files. The code repository
named in the article's "Code availability" section was not available when this was
written, so the analysis was rebuilt from the article's description and the data.
Every claim below is produced by code in this repository; see
`results/verification_report.md` for the full comparison.

## 0. Status ledger: what is and is not reproduced

"Reasons" for non-reproduction are hypotheses unless marked as verified.

| Item in the article | Status | Evidence | Reason if not reproduced |
|---|---|---|---|
| Table 1 (means, SDs, n; both rounds) | Reproduced, 70 of 72 entries | `results/verification_report.md` | The 2 other entries (round 2, choice-4 SD of both quadratic rows, printed 0.201, data 0.209) look like a typing error (verified against the data) |
| Tables 2 and 3, one-way MANOVAs in the text | Reproduced, 58 of 58 | verification report | none |
| Regression coefficients of token ratio on voting method | Reproduced, 8 of 8 | verification report | none |
| Survey regressions quoted in the text (Q1_1, Q1_2, Q2_1, Q2_10, ...) | Reproduced, 10 of 10 | verification report | none |
| Fig. 4 | Reproduced (compared through Table 1, largest difference 0.0005) | `fig4_compare.png` | none |
| Fig. 5 | Reproduced (12 bars, largest difference 0.006) | `agreement_figs5_7.png` | none; the article's figure shows reverse-worded items reversed |
| Fig. 6 | Reproduced (36 bars, largest difference 0.014) | same | none |
| Fig. 7 (V-Dem sub-scales) | Reproduced **with an inferred item mapping** (40 bars, largest difference 0.011) | `fig7_*`, `vdem_text_check.csv` | Mapping not in the files (verified); ours is inferred |
| V-Dem regressions quoted in the text | 5 of 7 reproduced | `vdem_text_check.csv` | Political Equality p (0.068 vs 0.058) and the Deliberative interaction (+0.063 vs +0.6029) unresolved; possibly a different sub-scale definition, item subset or model for these two |
| Two survey means quoted in the text ("voting method meaningful" 4.14, "relevant" 4.03) | Not reproduced (data: 4.17 and 4.19) | verification report, section 3 | Unknown; possibly a different subset or sample |
| Fig. 3 (satisfaction) | **Not computable**; re-plotted from the article's own numbers | `fig3_*`, section 7 of `FIGURE_COMPARISON.md` | The three statements are not in the released files. The figure implies N = 138 and the caption mistypes two percentages (verified) |
| Fig. 8 (correlation matrix) | **Not reproduced** (0 of 148 printed cells) | `fig8_*`, section 8 | The two survey files cannot be linked (no shared id, different row counts, condition labels agree in 19 % of rows); the row-to-item order of the value survey is assumed |
| Fig. 9 (t-SNE clusters) | **Not reproduced**; a substitute embedding is shown | `fig9_*`, section 9 | Ada-2 embeddings unavailable offline; embedding, t-SNE settings and message selection not specified; the cluster partition is not stable across embeddings (ARI 0.06 between two) |
| Demographic percentages | Not reproducible | section 3 | Demographics are not in the released files; the percentages imply a denominator of 184 |
| Recruitment / platform details | Not reproducible | | Cannot be re-run |
| Sample sizes | Inconsistent across files: 177 (votes), 182 / 183 (surveys), 184 (demographics), 138 (Fig. 3) | `sample_sizes.csv` | Not explained in the article |

## 1. What reproduces

154 numbers transcribed from the article were compared with the output of this code.
152 match to one unit in the last printed digit; the other 2 are a printing
discrepancy in the article (section 3.4).

| Article item | Result |
|---|---|
| Table 1 (means, SDs, n; both rounds) | 70 of 72 match |
| Table 2 (Pillai's trace, F, df, p) | 20 of 20 |
| Table 3 (with interaction) | 30 of 30 |
| One-way MANOVA quoted in the text | 8 of 8 |
| Regression of token ratio on voting method (8 coefficients) | 8 of 8 |
| Survey regressions quoted in the text (coefficient and p) | 10 of 10 |
| Fig. 5 values quoted in the text | 6 of 6 |

Figs 4-7 were redrawn from the data (`results/figures/`) and compared with the article's figures (`docs/FIGURE_COMPARISON.md`).

## 2. How the article's variables map onto the files

These are not stated in the article; they were recovered by finding the definitions
that reproduce the printed numbers.

- **Token ratio** = `choice_i / votes_given`, i.e. a share of the *budget*, not of the
  tokens actually spent. Dividing by the tokens spent does not reproduce Table 1.
- **`early` = the 20/80 power condition.** The file named `anonymous_round3_vote.csv`
  is the article's round 2.
- **Table 2 is an additive two-factor MANOVA** (`quadratic + same`), although the text
  calls it one-way. The separate one-way results the text quotes (for example
  P = 0.0222 in round 1) are also reproduced and differ slightly from Table 2 for
  that reason.
- **Survey regressions** are single-predictor OLS on the raw 1-5 scores of 182
  respondents. `Q1_1` ("indecisive"), `Q1_2` ("not good at maintaining order") and
  `Q2_10` ("can result in unexpected outcome") are reverse-worded, so a negative
  coefficient means a more favourable view. The signs in the text are consistent
  with that. Figs 5-6 display these three items reversed (6 - x).

## 3. Discrepancies found in the article (verified against the data)

1. **The round-2 sample includes 8 rows labelled `pilots`.** Table 1 (round 2) is
   reproduced only with them; without them every mean changes. The article describes
   round 2 as blind participants in the US and mentions a separate pilot; the file's
   `phase` labels (`pilots` 8, `round-1` 5, `round-2` 17, `round-3` 45) do not map onto
   that description.
2. **Sample sizes differ across the files.** Votes: 177 (102 + 75). Governance survey:
   182 respondents. AI-value survey: 183. The demographic percentages (for example
   32.07 %, 60.33 %) correspond to a denominator of 184, not 177.
3. **Part of the budget is unspent in 23 of 177 vote rows** (16 rows in round 1 leave
   tokens unspent, 1 overspends by one token, and 6 of the 8 pilot rows in round 2
   leave tokens unspent). Because ratios are shares of the budget, the four
   ratios then sum to less than 1, which is why Table 1's means do not sum to 1. In the
   round-2 rows that spend the whole budget the four ratios sum to exactly 1, so a
   four-variable MANOVA is rank deficient there; the published degrees of freedom
   (4) in round 2 depend on the six pilot rows that left tokens unspent. Without the pilots, `statsmodels` reports 3.
4. **Table 1, round 2:** the SD of choice 4 is printed as 0.201 in both quadratic
   rows. The data give 0.209 in both (0.2087 and 0.2089), so one printed value looks
   like a transcription error. All other Table 1 entries match.
5. **Table 3, round 2, voting power:** the text says the voting-power condition
   "significantly affects" the outcome (Pillai 0.11, P = 0.08). Table 3 gives
   P = 0.0806, which is not significant at the 0.05 level.
6. **Two survey means in the text are not reproduced.** "Voting method meaningful":
   article 4.14 (SD 0.815), data 4.17 (0.71). "Voting method relevant": article
   4.03 (0.92), data 4.19 (0.77) (n = 182).

## 4. Sensitivity analyses (not in the article)

`results/tables/sensitivity_*.csv`, `results/figures/sensitivity_pvalues.png`.

P-value for the effect of **voting method** (quadratic vs ranked), Pillai's trace:

| Data treatment | Round 1 | Round 2 |
|---|---:|---:|
| As published (Table 2) | 0.0233 | 0.3786 |
| Excluding the `pilots` rows | 0.0233 | 0.5195 |
| Rows that spent the whole budget only | 0.1068 | 0.4772 |
| Shares of tokens actually spent | 0.0419 | 0.5171 |
| Published ratios, choice 4 dropped (3 variables) | 0.0117 | 0.3211 |
| Additive log-ratio (zeros + 0.5 token) | 0.0311 | 0.7602 |
| Permutation test (10,000 shuffles, 4 variables) | 0.0229 | 0.3665 |

Where the four ratios sum to exactly 1 the code drops the last one automatically, so the
degrees of freedom in these rows are 3. Reading of the table: the round-1 difference by
voting method stays near or below 0.05 under most treatments but is not significant
when only rows that spent the whole budget are used (n = 85). No treatment gives a
significant voting-method effect in round 2. The **voting-power** effect is not
significant under any of these treatments (smallest p = 0.087, additive log-ratio,
round 1); in Table 3's interaction model the round-2 value is 0.0806.

Other checks:

- **Both rounds pooled with a round effect** (`sensitivity_pooled_round_effect.csv`):
  voting method P = 0.0487, round P = 0.0262, voting power P = 0.4485,
  interaction P = 0.5444. The two rounds differ from each other.
- **Multiple comparisons.** The survey regressions were run on 12 items with no
  adjustment. After Holm correction within each model and term, only `Q1_1` on voting
  power (Holm P = 0.0012) and `Q2_10` on voting power (P < 0.001) remain
  significant. `Q1_2` on voting method (raw P = 0.031, Holm 0.37), `Q1_2` on voting
  power (0.046, Holm 0.46) and `Q2_5` on voting method (0.042, Holm 0.46) do not.
- **What each rule would have decided** (`outcomes_by_condition.csv`). The article
  analyses how tokens were spent, not which option won. This table shows the winner by
  raw tokens and, for the quadratic conditions, by the square root of each person's
  tokens. It assumes the `choice_i` columns are token counts in every condition,
  which the data do not state; treat it as exploratory.

## 5. Limits on what the article's design can show

- Token shares describe how people spent a budget under each rule. They do not, by
  themselves, show that quadratic voting increased the influence of minority
  groups, and there is no one-person-one-vote condition to compare against.
- Group membership (Global South, visually impaired, and so on) is not in the released
  files, so no analysis by group is possible.

## 6. Not reproducible from the released files

- **V-Dem sub-scales (Fig. 7): only partly.** The item mapping is not in the files. A
  mapping into consecutive item blocks (`vdem.py`) reproduces all 40 bars of Fig. 7 and five of
  seven quoted regressions, but it is inferred, and the Political Equality p-value and the
  Deliberative interaction are not reproduced. See `docs/FIGURE_COMPARISON.md`, section 4.
- **Fig. 8 correlations:** not reproduced. The two survey files have no participant id and
  the rows do not align; see `FIGURE_COMPARISON.md`, section 8, for the diagnostics.
- **Fig. 3:** the satisfaction statements are not in the released files; it is only re-plotted
  from the article's numbers (section 7 there).
- **Fig. 9 clustering** used OpenAI Ada-2 embeddings, which are not available offline. A
  substitute (spaCy word vectors) is in `fig9.py`; its result depends strongly on the embedding
  and is not a reproduction (section 9 there). An earlier TF-IDF version was replaced by it because k-means
  isolated groups of identical short messages. The article also says the elbow method "maximizes"
  the within-cluster sum of squares; the elbow criterion looks for where it stops falling quickly.
- **Recruitment and platform details** (snowball, Facebook, direct messages, and
  later Prolific) cannot be re-run.

## 7. Questions worth putting to the authors

1. Which rows make up the article's round 2, and why are `pilots` rows included?
2. The mapping of `Q3_*`/`Q4_*` items to the ten V-Dem sub-scales (ours is inferred), and how the Political Equality p-value (0.058) and the Deliberative interaction (0.6029, p = 0.033) were computed.
3. Whether `choice_i` holds tokens or votes in the quadratic conditions.
4. A participant id (or a shared key) that links the votes and the two surveys.
5. Which of 177, 182, 183, 184 or 138 is the analysed N for each figure, and why Fig. 3 has 138 respondents.
6. The Ada-2 embeddings (or the exact preprocessing and t-SNE settings) behind Fig. 9, and which messages were embedded.
7. Whether the middle-statement percentages in the Fig. 3 caption (7.2 %, 0.2 %) are typos for 2.2 % and 0.7 %.
