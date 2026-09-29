# 独立复现：基于 DAO 的审议与投票用于 AI 治理

[English](README.md) | **简体中文**

本仓库包含重新运行 Sharma 等（2026）分析所用的代码和说明：*Democratic governance through
DAO-based deliberation and voting for inclusive decision making in AI models*，
Scientific Reports 16, 11792，DOI：[10.1038/s41598-026-40180-8](https://doi.org/10.1038/s41598-026-40180-8)。

这是基于作者在 OSF 上公开的数据所做的独立复现，与作者无关联。论文中提到的原始代码仓库在
撰写本仓库时已无法访问，因此分析是根据论文描述和公开数据重新搭建的。

**原文：**Sharma 等（2026），*Scientific Reports* 16, 11792 ——
<https://www.nature.com/articles/s41598-026-40180-8>（DOI：<https://doi.org/10.1038/s41598-026-40180-8>）。
**作者公开的数据（OSF）：**<https://osf.io/q6snh/>。

## 复现状态

| 项目 | 结果 |
|---|---|
| Table 1、Table 2、Table 3、正文中的单因素 MANOVA | 已复现 |
| 正文中引用的回归系数 | 已复现 |
| 图 4–6 | 已用数据重绘，并与论文逐柱对比（[docs/FIGURE_COMPARISON.zh-CN.md](docs/FIGURE_COMPARISON.zh-CN.md)），全部在读图误差内一致 |
| 图 7（V-Dem 子量表） | 用我们推断的题目映射，40 根柱全部复现；正文 7 个回归中 5 个吻合，2 个不吻合 |
| 图 3 | 无法计算（三个陈述不在公开文件中）；按论文自己的数值重绘。对应 N = 138，且正文有两个百分比与图不一致 |
| 图 8 | 未复现：论文印出的 148 个格子，0 个吻合；两份问卷无法配对 |
| 图 9 | 未复现：Ada-2 嵌入不可用；给出替代嵌入的结果，其聚类对嵌入方式很敏感 |

论文中转录的 154 个可核对数字里，152 个吻合。另外 2 个是 Table 1 中数据不支持的印刷数值
（[详情](docs/REPRODUCIBILITY.zh-CN.md)）。文档还记录了论文样本量、正文与公开文件不一致的地方，
以及论文没有报告的敏感性分析。完整的"已复现 / 未复现 / 可能原因"清单见
[docs/REPRODUCIBILITY.zh-CN.md](docs/REPRODUCIBILITY.zh-CN.md) 第 0 节。

## 图表：论文 vs 复现

下列每张图都由本仓库对公开数据的分析生成。图中与我们并列的论文数值，是从论文的图中量出或读出的
（`data/paper_figures/`）；论文的图像本身没有放在这里。请对照
[原文](https://www.nature.com/articles/s41598-026-40180-8)中的原图阅读。

### 图 3 —— 满意度（无法由公开数据计算；仅重绘）
![图 3：论文图 vs 说明文字百分比](results/figures/fig3_paper_layout_pair.png)

上：从论文自己的图形读出的比例。下：其说明文字中给出的百分比。三个陈述不在公开文件中。这些比例
对应 N = 138；中间陈述在说明文字中的两个百分比（7.2%、0.2%）与图形（2.2%、0.7%）不一致。

### 图 4 —— token 分配（已复现）
![图 4：复现 vs Table 1](results/figures/fig4_compare.png)

线：复现。圆环：论文 Table 1 的均值。最大差 0.0005。

### 图 5–7 —— 问卷评分（已复现；图 7 依赖推断的题目映射）
![图 5：论文版式，上为论文数值，下为复现](results/figures/fig5_paper_layout_pair.png)
![图 6：论文版式，上为论文数值，下为复现](results/figures/fig6_paper_layout_pair.png)
![图 7：论文版式，上为论文数值，下为复现](results/figures/fig7_paper_layout_pair.png)

每张图上方：从论文图中量出的数值；下方：复现。最大差：0.006（图 5）、0.014（图 6）、0.011
（图 7）；读图误差约 0.015。柱子从量表最小值（1）画起。图 7 背后的题目到子量表映射是推断的，
不是作者提供的。

![88 根柱的一致性](results/figures/agreement_figs5_7.png)

带 95% 置信区间的逐题面板（论文没有画置信区间）：
[图 5](results/figures/fig5_compare_panels.png)、[图 6](results/figures/fig6_compare_panels.png)、[图 7](results/figures/fig7_compare_panels.png)。

### 图 8 —— 相关矩阵（未复现）
![图 8：论文印出的格子（上）vs 复现尝试（下）](results/figures/fig8_paper_vs_replication.png)

上：论文印出的 148 个格子。下：公开数据按行号配对的结果——因为两份问卷没有共同 ID，这个配对只是
假设。148 个已印格子 0 个复现，结果与未配对的数据无法区分。

### 图 9 —— 消息聚类（未复现；替代嵌入）
![图 9：替代嵌入的 t-SNE](results/figures/fig9_tsne_substitute_embedding.png)

论文用 OpenAI Ada-2 嵌入，这里无法获得；此图使用 spaCy 词向量。划分随嵌入方式变化很大（与 TF-IDF
版本的 ARI 仅 0.06），不应当作论文的聚类来读。图中不含消息文本。

每张图的细节、数字和注意事项见 [docs/FIGURE_COMPARISON.zh-CN.md](docs/FIGURE_COMPARISON.zh-CN.md)。

## 主要发现

1. 第二轮的分析样本包含 8 行标为 `pilots` 的数据，去掉后 Table 1 第二轮无法复现。
2. 样本量不一致：投票数据 177 人，治理问卷 182 人，价值观问卷 183 人，人口统计百分比对应分母
   184，图 3 对应 138。
3. 有 23 行没有花完预算；由于"比例"按预算而不是实际花费计算，Table 1 的均值之和小于 1。
   花完预算的第二轮数据中四个比例之和恒为 1，四变量 MANOVA 秩亏。
4. 第一轮"二次投票"效应对数据处理方式较敏感：论文 P = 0.0233，只保留花完预算的行为 0.1068，
   其余处理在 0.01–0.04 之间；第二轮在所有处理下均不显著。
5. 对 12 个问卷题目做的回归没有多重比较校正；Holm 校正后只有 `Q1_1` 与 `Q2_10` 对投票权重的
   效应仍显著。

## 快速开始（Windows PowerShell）

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .

# 把 OSF 的 6 个 CSV 放进 data\raw\（见 data\README.zh-CN.md），或指定目录：
# $env:DAO_DATA_DIR = "D:\path\to\osf-files"

python scripts\run_all.py          # 表格、图和核对报告（默认 10,000 次置换，需几分钟）
python scripts\run_all.py --quick  # 仅 1,000 次置换
pytest                             # 将结果与论文数字逐项比对
```

图 9 需要可选依赖（没有时会自动跳过）：

```powershell
pip install scikit-learn spacy
python -m spacy download en_core_web_md
```

数据文件不包含在仓库中，获取方式和 SHA-256 校验值见 `data/README.zh-CN.md`。没有数据时测试会被跳过。

## 输出

写入 `results/`（仓库中已提交的版本由 Python 3.11、pandas 3.0、statsmodels 0.15 生成）：

| 路径 | 内容 |
|---|---|
| `results/verification_report.md` | 论文中每个数字与计算值并列 |
| `results/tables/` | Table 1–3、题目回归、敏感性分析、对比表、图 3/8/9 的诊断表 |
| `results/figures/` | 图 3–6、8、9（替代）、敏感性图，以及论文与复现的对比图 |
| `data/paper_figures/` | 从论文图 5–7 量出的柱高（约 ±0.015），以及从 PDF 读出的图 3、图 8 数值 |

## 目录结构

```
src/dao_replication/
  data.py          读取 OSF 文件，生成论文中的变量
  table1.py        Table 1
  manova.py        Table 2–3 与单因素 MANOVA
  survey.py        题目回归、Holm / BH 校正
  sensitivity.py   其他数据处理方式、置换检验、样本量
  outcomes.py      各规则会选出哪个选项（探索性）
  vdem.py          推断的 V-Dem 子量表映射（图 7）
  compare.py       论文与复现的对比表和图
  fig3.py fig8.py fig9.py   图 3、8、9（重绘 / 复现尝试 / 替代）
  digitize.py      可选：从论文图像量出柱高
  paper_extract.py 可选：从论文 PDF 读出图 3、图 8 的数值
  verify.py        与论文印刷数字比对
  paper_values.py  从论文转录的数字
  figures.py       图 4–6、敏感性图
scripts/run_all.py
tests/test_reproduction.py
docs/REPRODUCIBILITY.md   docs/REPRODUCIBILITY.zh-CN.md
docs/FIGURE_COMPARISON.md docs/FIGURE_COMPARISON.zh-CN.md
```

## 需要注意

- 诸如"token 比例 = `choice_i / votes_given`"这样的定义，是通过对照论文印出的数字反推得到的；
  数据没有变量字典。
- `outcomes.py` 假设所有条件下 `choice_i` 列都是 token 数，文件里没有说明。
- V-Dem 子量表的题目映射是推断的，不是作者提供的。
- 结果描述的是参与者在各规则下如何分配 token 预算，本身并不能证明对少数群体影响力的效应。
- 论文的 PDF 和图像没有放进仓库；`data/paper_figures/` 里只有从中量出或读出的数值。

## 许可

代码：MIT（见 `LICENSE`）。数据和论文适用各自的条款。
