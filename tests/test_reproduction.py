"""Tests compare code output with numbers printed in the paper.

They need the OSF CSV files (see data/README.md); without them they are skipped.
"""

from __future__ import annotations

import pytest

from dao_replication import verify
from dao_replication.config import FILES, data_dir
from dao_replication.data import load_gov_survey, load_value_survey, load_votes

pytestmark = pytest.mark.skipif(
    not all((data_dir() / f).exists() for f in FILES.values()),
    reason="OSF data files not found; see data/README.md",
)


@pytest.fixture(scope="module")
def votes():
    return load_votes()


@pytest.fixture(scope="module")
def gov():
    return load_gov_survey()[0]


@pytest.fixture(scope="module")
def checks(votes, gov):
    return verify.run_checks(votes, gov)


def test_sample_sizes(votes, gov):
    assert len(votes) == 177
    assert (votes["round"] == 1).sum() == 102
    assert (votes["round"] == 2).sum() == 75
    assert len(gov) == 182
    assert len(load_value_survey()) == 183


def test_every_paper_number_matches_or_is_documented(checks):
    unexplained = [c for c in checks if not c.ok and not c.explained]
    assert not unexplained, "\n".join(f"{c.group}: {c.name} paper={c.paper} computed={c.computed:.6f}" for c in unexplained)


@pytest.mark.parametrize("group", ["Table 1", "Table 2", "Table 3", "One-way (text)", "Ratio ~ quadratic", "Survey regression", "Fig. 5 (text)"])
def test_group_is_covered(checks, group):
    assert any(c.group == group for c in checks)


def test_documented_mismatches_are_really_mismatches(checks):
    # If the data ever start matching, the note in paper_values.py is stale.
    assert all(not c.ok for c in checks if c.note)


def test_round2_needs_the_pilot_rows(votes):
    """Table 1 (round 2) is reproduced only with the 8 'pilots' rows included."""
    from dao_replication.table1 import table1

    without = load_votes(include_pilots=False)
    a = table1(votes).query("round == 2")["mean_r1"].round(3).tolist()
    b = table1(without).query("round == 2")["mean_r1"].round(3).tolist()
    assert a != b
    assert (votes["phase"] == "pilots").sum() == 8


def test_unspent_budget(votes):
    under = votes[votes["unspent"] != 0]
    assert len(under) == 23
    assert set(under[under["round"] == 2]["phase"]) == {"pilots"}


def test_permutation_statistic_equals_oneway_pillai(votes):
    from dao_replication.manova import oneway
    from dao_replication.sensitivity import permutation_pillai

    perm = permutation_pillai(votes, n_perm=50).set_index(["round", "factor"])["pillai"]
    ow = oneway(votes).set_index(["round", "term"])["pillai"]
    for key in perm.index:
        assert perm[key] == pytest.approx(ow[key], abs=1e-4)


# ---- figure comparison ---------------------------------------------------------
def test_figs5_to_7_agree_with_digitised_article_values(gov):
    from dao_replication import compare

    tab = compare.figure_tables(gov)
    assert len(tab) == 4 * (3 + 9 + 10)
    assert tab["diff"].abs().max() < 0.02  # reading error is about 0.015


def test_table1_comparison_only_known_mismatches(votes):
    from dao_replication import compare
    from dao_replication.table1 import table1

    t = compare.table1_comparison(table1(votes))
    bad = t[~t["matches_printed"]]
    assert len(bad) == 2 and (bad["stat"] == "sd").all() and (bad["choice"] == 4).all() and (bad["round"] == 2).all()


def test_vdem_inferred_mapping_reproduces_five_text_results(gov, tmp_path):
    from dao_replication import compare, vdem

    vdem.regressions(vdem.subscales(gov)).to_csv(tmp_path / "vdem_regressions_inferred.csv", index=False)
    t = compare.vdem_text_check(tmp_path).set_index("subscale")
    for s in ("Electoral", "Liberal", "Participatory", "Civil Liberties", "Judicial Constraints"):
        assert t.loc[s, "coef_match"] and t.loc[s, "p_match"], s
    assert t.loc["Political Equality", "coef_match"] and not t.loc["Political Equality", "p_match"]
    assert not t.loc["Deliberative", "coef_match"]


# ---- Figs 3, 8, 9 ---------------------------------------------------------------
def test_fig3_caption_inconsistency_and_n():
    from dao_replication import fig3

    long, summ = fig3.consistency_table()
    s = summ.set_index("statement")
    assert (s["smallest_N_consistent_with_figure"] == 138).all()
    assert abs(s.loc["trust", "sum_of_caption_pcts"] - 104.5) < 1e-9
    bad = long[long["diff"].abs() > 0.1]
    assert set(bad["statement"]) == {"trust"}


def test_fig8_article_cells_and_pairing_does_not_reproduce(gov):
    from dao_replication import fig8

    paper, _ = fig8.paper_matrix()
    assert paper.shape == (18, 22) and int(paper.notna().sum().sum()) == 148
    diag, _ = fig8.diagnostics(gov, load_value_survey(), n_null=20)
    d = dict(zip(diag["diagnostic"], diag["value"]))
    assert d["printed cells reproduced within 0.005 (row-index pairing)"] == 0


def test_fig9_runs_when_spacy_available():
    from dao_replication import fig9

    if not fig9.spacy_available():
        pytest.skip("spaCy en_core_web_md not installed")
    m, elbow, stab, summ = fig9.analyse()
    assert set(m["cluster"]) == {0, 1, 2, 3} and int(m["count"].sum()) == 5057
    assert "text" not in summ.columns
