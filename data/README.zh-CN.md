# 数据

[English](README.md) | **简体中文**

原始文件**不**保存在本仓库中。它们是论文配套的 OSF 公开文件（项目 `q6snh`，
<https://osf.io/q6snh/>）。下载压缩包 `q6snh-osfstorage-archive.zip`，解压后把 6 个 CSV 放进
`data/raw/`（或用 `DAO_DATA_DIR` 指向存放它们的文件夹）。

```powershell
New-Item -ItemType Directory -Force data\raw | Out-Null
Expand-Archive -Path "$HOME\Downloads\q6snh-osfstorage-archive.zip" -DestinationPath data\raw
```

数据的使用条款以 OSF 项目页面所述为准。

## 使用的文件

SHA-256 校验值对应本仓库结果所用的副本。

| 文件 | 行数 | 用途 | SHA-256 |
|---|---:|---|---|
| `anonymous_round1_vote.csv` | 102 | 第一轮投票 | `a004bb31559ff1fc58f716ff4ca20a0a2645811c8a89333f72b159e0d936c6b0` |
| `anonymous_round3_vote.csv` | 75 | 第二轮投票（见下） | `a7c9b563811e67bbda49bd4c891ac8e35643f6d5dfb7f20d62af115bbff2db39` |
| `anonymized_gov-survey_two_rounds.csv` | 183（182 名受访者 + 1 行题目文字） | 图 5–7 题目、问卷回归 | `d573e6d2c1df604aae86f267b3f310199d6d6bb0aeccc029de35a88d052723a9` |
| `anonymized_value-survey_two_rounds.csv` | 183 | AI 价值题目（图 8 尝试；无法与治理问卷配对，见文档） | `87f504dbe251b17d2186b88fb5f37f72d48b329fbff1aa73fe521dda86429f7c` |
| `Human-AI-chat.csv` | 5,065 | 图 9 替代分析 | `6e7111f24c84313c112b76c1c0dd6c616e131b8eda5b9fc8eaa47f2b53ae3515` |
| `Group-Discussion.csv` | 801 | 未使用 | `d97e5e211205432075146135715ce92d34179bf4e69ce1fed96b37d7bc51bd72` |

用下面的命令检查：

```powershell
Get-FileHash data\raw\*.csv -Algorithm SHA256
```

## 列说明（由数据反推，并非来自数据字典）

**投票文件**

| 列 | 含义 |
|---|---|
| `pod-categorical`（第一轮）/ `pod`（第二轮） | 条件：`quadratic-equal`、`quadratic-early`、`ranked-equal`、`ranked-early`。`early` 即论文的 20/80 权力分配。 |
| `votes_given` | token 预算：100（equal）、400 或 25（20/80）。 |
| `choice_1` ... `choice_4` | 放在四个提案选项上的 token（图 1）。 |
| `phase`（仅第二轮文件） | `pilots`（8 行）、`round-1`（5）、`round-2`（17）、`round-3`（45）。 |

第二轮文件没有参与者 ID。名为 `round3` 的文件是论文的第二轮（n = 75，与 Table 1 一致）。

**治理问卷。**`Q1_*` 决策过程（图 5），`Q2_*` 投票机制（图 6），`Q3_*` 与 `Q4_*` 民主质量
陈述（图 7，子量表映射未提供；`vdem.py` 中有推断的映射）。答案是形如 `4: Agree` 的文字；
第一行数据是题目原文。

## 从论文中量出或读出的数值

`data/paper_figures/` 中的文件是对已发表论文图的测量或读取，不是作者的数据：

- `fig{5,6,7}_digitized.csv`：从论文图 5–7 的图像量出的柱高（精度约 ±0.015，见
  `docs/FIGURE_COMPARISON.zh-CN.md` 第 2 节）。
- `fig3_segments.csv`：从图 3 矢量图形读出的各段比例。
- `fig8_printed_cells.csv`：图 8 中印出的 148 个相关系数（论文只印 |r| ≥ 0.1 的格子）。
