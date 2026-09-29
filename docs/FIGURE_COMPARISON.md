# Figures: how the article draws them, and how the replication compares

**English** | [简体中文](FIGURE_COMPARISON.zh-CN.md)

All numbers below are produced by `scripts/run_all.py` (tables in
`results/tables/compare_*.csv`, figures in `results/figures/`) and checked by
`tests/test_reproduction.py`.

## 1. How the article's figures are made

| Figure | Content | Drawing method (read off the images) |
|---|---|---|
| Fig. 4 | Mean token ratio per choice, four conditions, two rounds | Line chart with markers; legend title "Trace", colours red / green / cyan / purple. Plotted values are those of Table 1. |
| Fig. 5 | 3 items on the decision process | Grouped bars, one group per condition, y axis 1.0-5.0, bars start at the axis minimum (1), black outlines, hatching on some fills, legend with the full item wording, x-axis title "Four conditions". No error bars, no n. |
| Fig. 6 | 9 items on the voting mechanism | Same design. |
| Fig. 7 | 10 V-Dem sub-scales | Same design, ten fills (grey, blue "/", pink, orange "*", brown, green "x", yellow, red "+", orange, purple "o"). |
| Fig. 3 | Satisfaction with the process, 3 statements | Horizontal stacked bars, 7 answer categories in shades of teal / grey / gold, x axis 0-100 %, legend on the right. See section 7. |
| Fig. 8 | Correlations, 18 AI-value items x 22 survey measures | Heat map, `PiYG` colour map on [-1, 1], each cell with \|r\| >= 0.1 annotated, blank otherwise. See section 8. |
| Fig. 9 | t-SNE of chat messages, 4 k-means clusters | Scatter with a different marker and colour per cluster, callout boxes quoting example messages. See section 9. |

`results/figures/fig{5,6,7}_paper_layout_pair.png` redraw this layout twice on the same axis:
top from the values measured in the article's image, bottom from the released data.

## 2. How the article's values were obtained

The article's Figs 5-7 are raster images. `src/dao_replication/digitize.py` locates the axes
frame (1.0 and 5.0), takes the group geometry from the bar clusters, and measures each bar's
top edge. The results are in `data/paper_figures/fig{5,6,7}_digitized.csv`.
Accuracy is about one pixel, roughly +-0.015 rating points. The measurements read slightly low
(mean difference to the replication: Fig. 5 -0.001, Fig. 6 -0.008, Fig. 7 -0.006), which is
consistent with measuring the centre of the 2 px outline. The article's figure files are not
redistributed here; only the measured numbers are.

## 3. Agreement

| Figure | Bars compared | Largest difference (replication - article) | Verdict |
|---|---:|---:|---|
| Fig. 4 (via Table 1 means) | 32 means | 0.0005 (three-decimal rounding) | Same |
| Fig. 5 | 12 | 0.006 | Same, within reading error |
| Fig. 6 | 36 | 0.014 | Same, within reading error |
| Fig. 7 | 40 | 0.011 | Same, **given the inferred item mapping** (section 4) |

Compare `results/figures/agreement_figs5_7.png` and the `*_compare_panels.png` figures, which
show the replication mean with its 95 % CI and the article's value as a hollow diamond.

## 4. The V-Dem sub-scales (Fig. 7) were recovered by inference

The article does not say which of the 24 `Q3_*`/`Q4_*` statements form which sub-scale, and the
mapping is not in the released files. An earlier attempt with arbitrary item subsets was
inconclusive. Assuming that sub-scales are consecutive item blocks and matching against the
40 measured bar heights and the text's regression coefficients gave `src/dao_replication/vdem.py`
(Electoral = Q3_1-2, Liberal = Q3_3-4, ... Judicial = Q4_10-11). Evidence and limits:

- All 40 bars of Fig. 7 are reproduced within 0.011.
- Five of seven regressions quoted in the text are reproduced exactly (coefficient and p):
  Electoral, Liberal, Participatory, Civil Liberties, Judicial Constraints
  (`results/tables/vdem_text_check.csv`).
- Judicial Constraints is reproduced only when respondents missing one of its two items
  are dropped (n = 180); averaging over the available item gives a bar that is 0.058 off.
- **Not reproduced:** Political Equality (coefficient +0.2582 matches, p = 0.068 against the
  printed 0.058) and the Deliberative interaction (article +0.6029, p = 0.033; replication
  +0.063, p = 0.73). No single `Q3_*`/`Q4_*` item or item subset gave that interaction
  coefficient. Something in the article's analysis for these two is unknown to us.
- The mapping is inferred, not confirmed by the authors. It is consistent with the data but
  a different assignment that gives the same bars cannot be ruled out.

## 5. Things to watch when reading the article's figures

1. **Reverse-worded items.** Figs 5-6 show Q1_1, Q1_2 and Q2_10 reversed (6 - x); the
   article's regression coefficients use the raw scores, so their signs are the opposite
   of what the bars suggest. Without reversal our means disagree with the figures by up to 2.4 points.
2. **Bars begin at 1, not 0.** That is the scale minimum, which is legitimate, but the
   visible ratio of bar heights is not a ratio of ratings.
3. **No uncertainty is drawn.** Group sizes are about 45 respondents and the 95 % CI half-width
   of a mean is 0.14-0.38 points (median 0.23), larger than most differences between
   conditions in Figs 5-7; the reversed item Q2_10 (voting power) is the visible exception.
   The panels show this.
4. **Fig. 4 uses budget shares.** Rows that do not spend the whole budget (23 of 177) make the
   four means sum to less than 1; the figure shows those means without saying so.
5. **Fig. 4 has no uncertainty either**, and round 2 includes eight rows labelled `pilots`.
6. **Sample sizes differ** between the figures' underlying files (177 / 182 / 183); n is not
   printed on the figures.
7. **Digitisation error** (+-0.015) bounds every statement in section 3; differences smaller
   than that cannot be seen from the article's images.

## 6. Where the replication differs in presentation (not in numbers)

Figures produced by `figures.py` (`fig4_interaction.png`, `fig5_process_perception.png`,
`fig6_mechanism_perception.png`) use dot plots instead of bars, fixed colour and marker per
condition, a legend on every figure, and CSV files with the plotted numbers. The comparison
figures use the article's own layout on purpose so that they can be laid side by side.

## 7. Fig. 3 (satisfaction): re-plotted, not recomputable

`results/figures/fig3_paper_layout_pair.png`, `results/tables/fig3_caption_vs_figure.csv`,
`fig3_summary.csv`. The three statements ("The experience was enjoyable or meaningful", ...)
are not columns of the released survey files, so the figure cannot be computed from the data.
Its shares were read exactly from the bar geometry in the PDF (`paper_extract.py`) and redrawn
in the article's layout. What this showed:

- **N = 138.** Every percentage of every bar is a whole number of respondents out of 138 (for
  example 46.38 % = 64 / 138). The other analyses use 177 (votes), 182 (governance survey) and
  183 (value survey); 138 is not explained anywhere in the article.
- **The caption text and the figure disagree for the middle statement.** The caption gives
  7.2 % "somewhat disagree" and 0.2 % "disagree" (the six percentages add up to 104.5 %). The
  figure shows 2.2 % (3 respondents) and 0.7 % (1 respondent), which adds up to 100 %.
  The caption is most likely mistyped. The other two statements agree with the figure to 0.05 points.
- The "Strongly Disagree" segment is drawn in white in the article, so it is invisible against
  the page; we outline it.

## 8. Fig. 8 (correlation matrix): not reproduced

`results/figures/fig8_paper_vs_replication.png`, `results/tables/fig8_diagnostics.csv`,
`fig8_our_matrix_row_index_pairing.csv`, `data/paper_figures/fig8_printed_cells.csv`.

Top panel: the article's 148 printed cells, read from the PDF's text layer (the article prints a
cell only when |r| >= 0.1). Bottom panel: the same layout from the released data.

The two survey files have no participant id, so the bottom panel had to pair respondents by
row index. That pairing is an assumption; the diagnostics indicate that it is wrong (or that the
files cannot be linked at all):

| Diagnostic | Value |
|---|---:|
| Cells printed in the article (\|r\| >= 0.1), of 396 | 148 |
| Cells with \|r\| >= 0.1 with our pairing | 61 |
| Same for random within-condition pairings (95 % range) | 47-116 |
| Printed cells reproduced within 0.005 | 0 of 148 |
| Correlation between our and the article's printed values | 0.05 (random pairings: 0.08) |
| Row-index-paired rows with the same condition label | 19 % (chance is about 25 %) |

Reading: our matrix is indistinguishable from an unlinked one, while the article's matrix has far
more sizeable correlations than unlinked data give. It shows a broad pattern, with the trust, fairness and
willingness items (bottom five rows) correlating positively with nearly every process and
quality measure (r about 0.1-0.33). That is consistent with the article having had linked
data, which we do not have. Other things to know:

- The 18 rows are assumed to be the 18 value-survey columns in file order (`q1A-G`, `q2A-K`);
  the files do not label them.
- 10 of the 22 columns are V-Dem sub-scales whose item mapping is inferred (section 4), so even
  with a correct link those columns carry that uncertainty. The 12 item columns do not.
- Fig. 8 uses the raw scores of the reverse-worded items: its column label reads "were
  indecisive", unlike Figs 5-6, which show the reversed item.
- With n of about 180, |r| = 0.145 is the two-sided 5 % threshold, but the article prints cells
  down to 0.10. The colouring therefore does not mark significance.

## 9. Fig. 9 (t-SNE of messages): substitute analysis, not a reproduction

`results/figures/fig9_tsne_substitute_embedding.png`, `fig9_elbow.png`,
`results/tables/fig9_*.csv`. Requires the optional `text` extras (scikit-learn, spaCy and the
`en_core_web_md` model). No message text is written to any output.

The article embedded messages with OpenAI Ada-2, clustered them with k-means (k = 4) and drew a
t-SNE plot. Ada-2 is not available offline here (the sandbox blocks model downloads and has no
API access, and we did not try to route around that), so the figure uses averaged spaCy word vectors.
The layout copies the article (marker shapes and colours per cluster, legend titled "Cluster");
the callout boxes, which quote participants, are replaced by aggregate statistics.

What we can say:

- The chat file has 5,057 messages but only 1,749 distinct ones; the article does not say
  whether repeats were kept. We embed distinct messages and weight by repeats.
- The elbow curve (`fig9_elbow.png`) decreases smoothly and has no visible elbow at k = 4.
  The article says the elbow method "maximizes" the within-cluster sum of squares; the
  criterion is where it stops falling quickly.
- The partition depends on the embedding: repeated k-means runs agree with each other (ARI 0.83-0.85), but
  a TF-IDF embedding gives a very different partition (ARI 0.06). A cluster structure that
  changes with the representation should not be given a fixed interpretation.
- Against the four themes in the article's caption, only one has a clear counterpart:
  our cluster D holds 219 messages, 97 % with at most three words, 46 % acknowledgements
  ("short responses"). Mentions of nurse / CEO are concentrated in clusters A (22 %) and C (10 %),
  but no cluster is dominated by them, and bias / harm words are rare everywhere (at most 9 %),
  so the article's "reflective comments on social biases" cluster is not identified.
- Cluster letters are ordered by size and do not correspond to the article's cluster numbers.
