# Data

**English** | [简体中文](README.zh-CN.md)

The raw files are **not** stored in this repository. They are the public OSF
files that accompany the article (project `q6snh`, <https://osf.io/q6snh/>).
Download the archive `q6snh-osfstorage-archive.zip`, unzip it, and put the six
CSV files in `data/raw/` (or point `DAO_DATA_DIR` at the folder that holds them).

```powershell
New-Item -ItemType Directory -Force data\raw | Out-Null
Expand-Archive -Path "$HOME\Downloads\q6snh-osfstorage-archive.zip" -DestinationPath data\raw
```

Terms of use for the data are those stated on the OSF project page.

## Files used

SHA-256 checksums are of the copies used for the results in this repository.

| File | Rows | Used for | SHA-256 |
|---|---:|---|---|
| `anonymous_round1_vote.csv` | 102 | Round 1 votes | `a004bb31559ff1fc58f716ff4ca20a0a2645811c8a89333f72b159e0d936c6b0` |
| `anonymous_round3_vote.csv` | 75 | Round 2 votes (see below) | `a7c9b563811e67bbda49bd4c891ac8e35643f6d5dfb7f20d62af115bbff2db39` |
| `anonymized_gov-survey_two_rounds.csv` | 183 (182 respondents + 1 question-text row) | Fig. 5-6 items, survey regressions | `d573e6d2c1df604aae86f267b3f310199d6d6bb0aeccc029de35a88d052723a9` |
| `anonymized_value-survey_two_rounds.csv` | 183 | AI-value items (Fig. 8 attempt; not linkable to the governance survey, see docs) | `87f504dbe251b17d2186b88fb5f37f72d48b329fbff1aa73fe521dda86429f7c` |
| `Human-AI-chat.csv` | 5,065 | Fig. 9 substitute analysis | `6e7111f24c84313c112b76c1c0dd6c616e131b8eda5b9fc8eaa47f2b53ae3515` |
| `Group-Discussion.csv` | 801 | not used | `d97e5e211205432075146135715ce92d34179bf4e69ce1fed96b37d7bc51bd72` |

Check them with:

```powershell
Get-FileHash data\raw\*.csv -Algorithm SHA256
```

## Column notes (inferred from the data, not from a data dictionary)

**Vote files**

| Column | Meaning |
|---|---|
| `pod-categorical` (round 1) / `pod` (round 2) | Condition: `quadratic-equal`, `quadratic-early`, `ranked-equal`, `ranked-early`. `early` is the paper's 20/80 power distribution. |
| `votes_given` | Token budget: 100 (equal), 400 or 25 (20/80). |
| `choice_1` ... `choice_4` | Tokens placed on each proposal option (Fig. 1). |
| `phase` (round-2 file only) | `pilots` (8 rows), `round-1` (5), `round-2` (17), `round-3` (45). |

The round-2 file has no participant id. The file named `round3` is the
paper's round 2 (n = 75, matching Table 1).

**Governance survey.** `Q1_*` decision process (Fig. 5), `Q2_*` voting mechanism
(Fig. 6), `Q3_*` and `Q4_*` democratic-quality statements (Fig. 7, sub-scale
mapping not provided; an inferred one is in `vdem.py`). Answers are text such as `4: Agree`; the first data row
holds the question wording.

## Measured article values

Files in `data/paper_figures/` are measurements or readings of the published article's figures, not author data:

- `fig{5,6,7}_digitized.csv`: bar heights measured from the article's Figs 5-7 images (accuracy about +-0.015; see `docs/FIGURE_COMPARISON.md`, section 2).
- `fig3_segments.csv`: category shares read from the Fig. 3 vector graphic.
- `fig8_printed_cells.csv`: the 148 correlations printed in Fig. 8 (the article prints only cells with |r| >= 0.1).
