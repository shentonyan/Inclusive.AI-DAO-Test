"""Smoke tests on SYNTHETIC data with the same file layout as the OSF files.

They need no download, so they run everywhere (including CI) and check that the
code loads the files, derives the variables, and produces every output. They say
nothing about the article's numbers; `test_reproduction.py` does that with the
real data.
"""

from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dao_replication import config
from dao_replication.config import CONDITIONS, FILES

ROOT = Path(__file__).resolve().parents[1]
LIKERT = {1: "1: Strongly Disagree", 2: "2: Disagree", 3: "3: Neutral", 4: "4: Agree", 5: "5:Strongly Agree"}
GOV_ITEMS = (["Q1_1", "Q1_2", "Q1_3", "Q2_1"] + [f"Q2_{i}" for i in range(3, 11)]
             + [f"Q3_{i}" for i in range(1, 14)] + [f"Q4_{i}" for i in range(1, 12)])
BUDGET = {"quadratic-equal": 100, "quadratic-early": 400, "ranked-equal": 100, "ranked-early": 25}


def _votes(rng, n_per_cond, round_no):
    rows = []
    for cond in CONDITIONS:
        for k in range(n_per_cond):
            b = BUDGET[cond]
            w = rng.dirichlet(np.ones(4))
            choices = np.floor(w * b).astype(int)
            if k == 0:  # one row that leaves budget unspent
                choices[0] = max(choices[0] - 3, 0)
            rows.append({"cond": cond, "votes_given": b, **{f"choice_{i + 1}": int(c) for i, c in enumerate(choices)}})
    df = pd.DataFrame(rows)
    if round_no == 1:
        return pd.DataFrame({"pod-categorical": df["cond"], "pod": range(len(df)), "user": [f"u{i}" for i in range(len(df))],
                             "votes_given": df["votes_given"], **{f"choice_{i}": df[f"choice_{i}"] for i in range(1, 5)}})
    phases = np.resize(["pilots", "round-1", "round-2", "round-3"], len(df))
    return pd.DataFrame({"pod": df["cond"], "phase": phases, "votes_given": df["votes_given"],
                         **{f"choice_{i}": df[f"choice_{i}"] for i in range(1, 5)}})


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    d = tmp_path_factory.mktemp("osf")
    rng = np.random.default_rng(0)
    _votes(rng, 6, 1).to_csv(d / FILES["vote_round1"], index=False)
    _votes(rng, 6, 2).to_csv(d / FILES["vote_round2"], index=False)
    n = 48
    conds = np.resize(CONDITIONS, n)
    gov = {"pod": conds}
    for it in GOV_ITEMS:
        gov[it] = [LIKERT[v] for v in rng.integers(1, 6, n)]
    header = {"pod": np.nan, **{it: f"Question text - statement for {it}" for it in GOV_ITEMS}}
    pd.concat([pd.DataFrame([header]), pd.DataFrame(gov)], ignore_index=True).to_csv(d / FILES["gov_survey"], index=False)
    val = {"pod": conds}
    for c in ["q1A", "q1B", "q1C", "q1D", "q1E", "q1F", "q1G"] + ["q2" + x for x in "ABCDEFGHIJK"]:
        val[c] = rng.integers(1, 6, n)
    pd.DataFrame(val).to_csv(d / FILES["value_survey"], index=False)
    pd.DataFrame({"text": [None, "hello", "yes", "no", "hello"] + [f"message {i}" for i in range(40)],
                  "aiResponse": ""}).to_csv(d / FILES["human_ai_chat"], index=False)
    pd.DataFrame({"text": ["I agree"]}).to_csv(d / FILES["group_discussion"], index=False)
    return d


@pytest.fixture()
def synth_env(synth, monkeypatch, tmp_path):
    monkeypatch.setenv("DAO_DATA_DIR", str(synth))
    monkeypatch.setenv("DAO_RESULTS_DIR", str(tmp_path / "results"))
    return synth


def test_load_votes_and_budget_ratios(synth_env):
    from dao_replication.data import load_votes

    v = load_votes()
    assert len(v) == 48 and set(v["round"]) == {1, 2} and set(v["cond"]) == set(CONDITIONS)
    assert np.allclose(v["r1"], v["choice_1"] / v["votes_given"])  # share of the budget, not of tokens spent
    assert (v["unspent"] >= 0).all() and (v["unspent"] > 0).any()
    assert len(load_votes(include_pilots=False)) < len(v)


def test_unknown_condition_is_rejected(tmp_path, monkeypatch, synth):
    from dao_replication.data import load_votes

    d = tmp_path / "bad"
    d.mkdir()
    for f in FILES.values():
        (d / f).write_bytes((synth / f).read_bytes())
    df = pd.read_csv(d / FILES["vote_round1"])
    df.loc[0, "pod-categorical"] = "something-else"
    df.to_csv(d / FILES["vote_round1"], index=False)
    monkeypatch.setenv("DAO_DATA_DIR", str(d))
    with pytest.raises(ValueError):
        load_votes()


def test_gov_survey_parsing_and_reverse_items(synth_env):
    from dao_replication.data import REVERSE_ITEMS, load_gov_survey
    from dao_replication.survey import condition_means

    gov, texts = load_gov_survey()
    assert len(gov) == 48 and set(texts) >= set(GOV_ITEMS)
    assert gov["Q1_1"].between(1, 5).all()
    raw = condition_means(gov, ["Q1_1"], reverse=False)["mean"].to_numpy()
    rev = condition_means(gov, ["Q1_1"], reverse=True)["mean"].to_numpy()
    assert "Q1_1" in REVERSE_ITEMS and np.allclose(raw + rev, 6)


def test_table1_and_manova_run(synth_env):
    from dao_replication.data import load_votes
    from dao_replication.manova import oneway, table2, table3
    from dao_replication.table1 import table1

    v = load_votes()
    t1 = table1(v)
    assert len(t1) == 8 and (t1["n"] == 6).all()
    for f in (table2, table3, oneway):
        assert len(f(v)) > 0


def test_vdem_mapping_uses_every_item_once(synth_env):
    from dao_replication import vdem
    from dao_replication.data import load_gov_survey

    items = [i for v in vdem.VDEM_ITEMS.values() for i in v]
    assert len(items) == len(set(items)) == 24
    gov, _ = load_gov_survey()
    sub = vdem.subscales(gov)
    assert list(vdem.VDEM_ITEMS) == [c for c in sub.columns if c in vdem.VDEM_ITEMS]
    gov.loc[0, "Q4_11"] = np.nan  # a missing item makes the whole sub-scale missing
    assert np.isnan(vdem.subscales(gov).loc[0, "Judicial Constraints"])


def test_fig8_matrix_shape(synth_env):
    from dao_replication import fig8
    from dao_replication.data import load_gov_survey, load_value_survey

    g, _ = load_gov_survey()
    c = fig8.corr_matrix(*fig8.paired_frames(g, load_value_survey()))
    assert c.shape == (18, 22)
    paper, rows = fig8.paper_matrix()
    assert paper.shape == (18, 22) and len(rows) == 18


def test_paper_extracts_are_committed():
    for f in ("fig3_segments.csv", "fig5_digitized.csv", "fig6_digitized.csv", "fig7_digitized.csv", "fig8_printed_cells.csv"):
        assert (ROOT / "data" / "paper_figures" / f).exists()


def test_run_all_quick_writes_outputs_without_optional_packages(synth_env, monkeypatch, tmp_path):
    from dao_replication import fig9

    monkeypatch.setattr(fig9, "spacy_available", lambda: False)  # Fig. 9 must be skipped, not crash
    monkeypatch.setattr(sys, "argv", ["run_all.py", "--quick"])
    with pytest.raises(SystemExit):  # exit status 1 is expected: synthetic data do not match the article
        runpy.run_path(str(ROOT / "scripts" / "run_all.py"), run_name="__main__")
    out = Path(config.results_dir())
    for f in ("verification_report.md", "tables/table1.csv", "tables/compare_figs5_7.csv", "tables/fig8_diagnostics.csv",
              "figures/fig3_paper_layout_pair.png", "figures/fig4_compare.png", "figures/fig7_paper_layout_pair.png",
              "figures/fig8_paper_vs_replication.png"):
        assert (out / f).exists(), f
    assert not (out / "figures" / "fig9_tsne_substitute_embedding.png").exists()
