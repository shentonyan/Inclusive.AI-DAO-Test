# Independent re-analysis: DAO-based deliberation and voting for AI governance

**English** | [简体中文](README.zh-CN.md)

Code and notes for re-running the analyses in Sharma et al. (2026), *Democratic
governance through DAO-based deliberation and voting for inclusive decision making
in AI models*, Scientific Reports 16, 11792.
DOI: [10.1038/s41598-026-40180-8](https://doi.org/10.1038/s41598-026-40180-8)

This is an independent re-analysis of the data the authors released on OSF. It is not
affiliated with the authors. The code repository named in the article was not
available when this was written, so the analysis was rebuilt from the article's
description and the released data.

**Original article:** Sharma et al. (2026), *Scientific Reports* 16, 11792 —
<https://www.nature.com/articles/s41598-026-40180-8> (DOI: <https://doi.org/10.1038/s41598-026-40180-8>).
**Released data (OSF):** <https://osf.io/q6snh/>.

## Status

| Item | Result |
|---|---|
| Table 1, Table 2, Table 3, one-way MANOVA in the text | Reproduced |
| Regression coefficients quoted in the text | Reproduced |
| Figs 4-6 | Redrawn from the data and compared bar by bar with the article ([docs/FIGURE_COMPARISON.md](docs/FIGURE_COMPARISON.md), [中文](docs/FIGURE_COMPARISON.zh-CN.md)); all within reading error |
| Fig. 7 (V-Dem sub-scales) | All 40 bars reproduced with an item mapping inferred by us; 5 of 7 quoted regressions match, 2 do not |
| Fig. 3 | Not computable (statements absent from the released files); re-plotted from the article's numbers. Implies N = 138; the caption mistypes two percentages |
| Fig. 8 | Not reproduced: 0 of 148 printed cells; the two survey files cannot be linked |
| Fig. 9 | Not reproduced: Ada-2 embeddings unavailable; a substitute embedding is shown and its clusters are not stable across embeddings |

152 of 154 numbers transcribed from the article match. The other two are a printed
value in Table 1 that the data do not support ([details](docs/REPRODUCIBILITY.md); [中文](docs/REPRODUCIBILITY.zh-CN.md)).
The full list of what is and is not reproduced, with possible reasons, is section 0 of that file.
The notes also record several places where the article's sample sizes and text
differ from the released files, and sensitivity analyses that the article does not
report.

## Figures: article vs. replication

Each figure below is drawn from this repository's own analysis of the released data. Where the
article's numbers are shown next to ours, they were measured or read from the article's figures
(`data/paper_figures/`); the article's images themselves are not reproduced here. Read the
original figures in the [article](https://www.nature.com/articles/s41598-026-40180-8) alongside these.

### Fig. 3 — satisfaction (not computable from the released data; re-plotted)
![Fig. 3: article vs. caption percentages](results/figures/fig3_paper_layout_pair.png)

Top: shares read from the article's own graphic. Bottom: the percentages quoted in its caption.
The three statements are not in the released files. The shares imply N = 138, and two caption
percentages for the middle statement (7.2 %, 0.2 %) disagree with the graphic (2.2 %, 0.7 %).

### Fig. 4 — token allocation (reproduced)
![Fig. 4: replication vs. Table 1](results/figures/fig4_compare.png)

Lines: replication. Rings: the article's Table 1 means. Largest difference 0.0005.

### Figs 5–7 — survey ratings (reproduced; Fig. 7 with an inferred item mapping)
![Fig. 5: article layout, article values (top) vs. replication (bottom)](results/figures/fig5_paper_layout_pair.png)
![Fig. 6: article layout, article values (top) vs. replication (bottom)](results/figures/fig6_paper_layout_pair.png)
![Fig. 7: article layout, article values (top) vs. replication (bottom)](results/figures/fig7_paper_layout_pair.png)

Top of each: values measured from the article's figure. Bottom: replication. Largest differences:
0.006 (Fig. 5), 0.014 (Fig. 6), 0.011 (Fig. 7); the reading error is about 0.015. Bars start at the
scale minimum (1). The item-to-sub-scale mapping behind Fig. 7 is inferred, not supplied by the authors.

![Agreement of all 88 bars](results/figures/agreement_figs5_7.png)

With 95 % confidence intervals (the article draws none), per-item panels:
[Fig. 5](results/figures/fig5_compare_panels.png), [Fig. 6](results/figures/fig6_compare_panels.png), [Fig. 7](results/figures/fig7_compare_panels.png).

### Fig. 8 — correlation matrix (not reproduced)
![Fig. 8: article's printed cells (top) vs. replication attempt (bottom)](results/figures/fig8_paper_vs_replication.png)

Top: the 148 cells printed in the article. Bottom: released data with respondents paired by row
index, which is an assumption because the two survey files share no participant id. 0 of 148
printed cells are reproduced, and the result is indistinguishable from unlinked data.

### Fig. 9 — message clusters (not reproduced; substitute embedding)
![Fig. 9: t-SNE with a substitute embedding](results/figures/fig9_tsne_substitute_embedding.png)

The article used OpenAI Ada-2 embeddings, which were not available here; this uses spaCy word
vectors. The partition changes strongly with the embedding (ARI 0.06 against a TF-IDF version), so
it should not be read as the article's clusters. No message text is shown.

Details, numbers and caveats for every figure: [docs/FIGURE_COMPARISON.md](docs/FIGURE_COMPARISON.md).

## Quick start (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .

# Put the six OSF CSV files in data\raw\ (see data\README.md), or point at them:
# $env:DAO_DATA_DIR = "D:\path\to\osf-files"

python scripts\run_all.py          # tables, figures, verification report (about 30 s)
python scripts\run_all.py --quick  # 1,000 permutations instead of 10,000
pytest                             # compares the output with the article's numbers
```

Fig. 9 needs the optional text extras: `pip install scikit-learn spacy; python -m spacy download en_core_web_md`
(skipped when absent). The data are not included in this repository; `data/README.md` says where to get
them and lists SHA-256 checksums. Tests are skipped when the data are absent.

## Outputs

Written to `results/` (the committed copies were produced with Python 3.11,
pandas 3.0, statsmodels 0.15):

| Path | Content |
|---|---|
| `results/verification_report.md` | Every article number next to the computed value |
| `results/tables/` | Table 1-3, item regressions, sensitivity analyses, outcomes, sample sizes |
| `results/figures/` | Figs 3-6, 8, 9 (substitute), a sensitivity plot, and article-vs-replication comparisons (`*_paper_layout_pair`, `*_compare_panels`, `agreement_figs5_7`, `fig4_compare`) |
| `data/paper_figures/` | Bar heights measured from the article's Figs 5-7 (about +-0.015) |

## Layout

```
src/dao_replication/
  data.py          load the OSF files, derive the article's variables
  table1.py        Table 1
  manova.py        Tables 2-3 and the one-way MANOVAs
  survey.py        item regressions, Holm / BH adjustment
  sensitivity.py   alternative data treatments, permutation test, sample sizes
  outcomes.py      which option each rule would have chosen (exploratory)
  verify.py        compare with the article's printed numbers
  paper_values.py  numbers transcribed from the article
  figures.py       Figs 4-6, sensitivity plot
  vdem.py          inferred V-Dem sub-scale mapping (Fig. 7)
  compare.py       article-vs-replication tables and figures
  digitize.py      optional: measure bar heights from the article's images
  paper_extract.py optional: read Fig. 3 / Fig. 8 numbers from the article PDF
  fig3.py fig8.py fig9.py   Figs 3, 8, 9 (re-plot / attempt / substitute)
scripts/run_all.py
tests/test_reproduction.py
docs/REPRODUCIBILITY.md   docs/REPRODUCIBILITY.zh-CN.md
docs/FIGURE_COMPARISON.md docs/FIGURE_COMPARISON.zh-CN.md
```

## Caveats

- Definitions such as "token ratio = `choice_i / votes_given`" were recovered by
  matching the article's printed numbers; the data have no dictionary.
- `outcomes.py` assumes the `choice_i` columns are token counts in every condition,
  which the files do not state.
- The V-Dem sub-scale item mapping is inferred, not supplied by the authors.
- The article's PDF and images are not in this repository; `data/paper_figures/` holds only numbers measured or read from them.
- The results describe how participants spent a token budget under each rule.
  They do not by themselves show effects on minority influence.

## License

Code: MIT (see `LICENSE`). The data and the article are subject to their own terms.
