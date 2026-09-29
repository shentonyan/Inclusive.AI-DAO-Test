# Verification report

| Group | Matched | Total |
|---|---:|---:|
| Table 1 | 70 | 72 |
| Table 2 | 20 | 20 |
| Table 3 | 30 | 30 |
| One-way (text) | 8 | 8 |
| Ratio ~ quadratic | 8 | 8 |
| Survey regression | 10 | 10 |
| Fig. 5 (text) | 6 | 6 |

**152 of 154 numbers match** (tolerance: one unit in the last printed digit).

## Numbers that do not match (2)

| group   | check                          |   paper |   computed |     diff | note                                                                  |
|:--------|:-------------------------------|--------:|-----------:|---------:|:----------------------------------------------------------------------|
| Table 1 | R2 quadratic-equal sd choice 4 |   0.201 |   0.208687 | 0.007687 | printed 0.201; data give 0.209 (same value printed for the 20/80 row) |
| Table 1 | R2 quadratic-early sd choice 4 |   0.201 |   0.208874 | 0.007874 | printed 0.201; data give 0.209 (same value printed for the equal row) |

## Known discrepancies in the article

- Table 1, round 2: the SD of choice 4 is printed as 0.201 in both quadratic rows; the data give 0.209 for both, so one printed value looks like a transcription error. All other Table 1 entries match.
- Sample size: votes n=177 (102+75) but the governance survey has 182 respondents, the AI-value survey 183, and the demographic percentages imply a denominator of 184.
- Round 2 is described as blind US participants; Table 1 (round 2) is reproduced only when 8 rows labelled 'pilots' in the file named 'round3' are included.
- Text says the round-2 voting-power effect is significant (Pillai 0.11, P=0.08); Table 3 gives P=0.0806, which is not significant at 0.05.
- Text: mean 4.14 (SD 0.815) for 'voting method meaningful' and 4.03 (SD 0.92) for 'voting method relevant'; the released survey gives 4.17 (0.71) and 4.19 (0.77) on n=182.

## Not testable with the released files

- V-Dem sub-scale results (Fig. 7 and regressions on Electoral, Liberal, ... Judicial Constraints): the mapping from the 24 Q3_/Q4_ statements to the ten sub-scales is not in the released files.
- Fig. 8 correlations: the two survey files have no participant id and their rows do not align (about 19% agreement in condition labels at equal row index).
- Fig. 3 satisfaction items, demographics and the LLM-usage figure: not in the released files.
- Fig. 9 clustering: used OpenAI Ada-2 embeddings (needs an API key). A TF-IDF substitute was tried and dropped: k-means isolated groups of identical short messages and left 4,557 of 5,057 in one cluster.

## Survey statistics quoted in the text but not reproduced

| item   |   paper_mean |   paper_sd |   data_mean |   data_sd |   n |
|:-------|-------------:|-----------:|------------:|----------:|----:|
| Q2_1   |         4.14 |      0.815 |        4.17 |      0.71 | 182 |
| Q2_3   |         4.03 |      0.92  |        4.19 |      0.77 | 182 |


## Sample sizes in the released files

| source                                            |   n |
|:--------------------------------------------------|----:|
| vote files, round 1                               | 102 |
| vote files, round 2 (file 'round3', incl. pilots) |  75 |
| vote files, total (paper: 177)                    | 177 |
| governance survey respondents                     | 182 |
| AI-value survey respondents                       | 183 |


## Rows that leave part of the budget unallocated

|   round | phase   |   n |   n_underallocated |   n_overallocated |   mean_unspent_share |
|--------:|:--------|----:|-------------------:|------------------:|---------------------:|
|       1 | main    | 102 |                 16 |                 1 |            0.0980882 |
|       2 | pilots  |   8 |                  6 |                 0 |            0.204687  |
|       2 | round-1 |   5 |                  0 |                 0 |            0         |
|       2 | round-2 |  17 |                  0 |                 0 |            0         |
|       2 | round-3 |  45 |                  0 |                 0 |            0         |

