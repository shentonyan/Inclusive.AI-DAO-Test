"""Run the whole re-analysis and write tables, figures and a verification report.

    python scripts/run_all.py                # everything
    python scripts/run_all.py --quick        # fewer permutations
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dao_replication import compare, fig3, fig8, fig9, figures, outcomes, sensitivity, survey, verify  # noqa: E402
from dao_replication.config import results_dir  # noqa: E402
from dao_replication.data import load_gov_survey, load_value_survey, load_votes  # noqa: E402
from dao_replication.manova import oneway, table2, table3  # noqa: E402
from dao_replication.table1 import table1  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="1,000 permutations instead of 10,000")
    ap.add_argument("--n-perm", type=int, default=10_000)
    args = ap.parse_args()

    out = results_dir()
    tables = out / "tables"
    tables.mkdir(exist_ok=True)

    votes = load_votes()
    gov, texts = load_gov_survey()
    value = load_value_survey()

    # ---- reproduction of the paper's numbers
    table1(votes).to_csv(tables / "table1.csv", index=False)
    table2(votes).to_csv(tables / "table2_manova_additive.csv", index=False)
    table3(votes).to_csv(tables / "table3_manova_interaction.csv", index=False)
    oneway(votes).to_csv(tables / "manova_oneway_text.csv", index=False)

    reg = survey.add_multiplicity(survey.item_regressions(gov))
    reg.to_csv(tables / "survey_item_regressions.csv", index=False)

    # ---- additional analyses
    variants = sensitivity.manova_variants(votes)
    variants.to_csv(tables / "sensitivity_manova_variants.csv", index=False)
    n_perm = 1_000 if args.quick else args.n_perm
    sensitivity.permutation_pillai(votes, n_perm=n_perm).to_csv(tables / "sensitivity_permutation.csv", index=False)
    sensitivity.pooled_with_round(votes).to_csv(tables / "sensitivity_pooled_round_effect.csv", index=False)
    unspent = sensitivity.unspent_summary(votes)
    unspent.to_csv(tables / "unspent_tokens.csv", index=False)
    sizes = sensitivity.sample_sizes(votes, gov, value)
    sizes.to_csv(tables / "sample_sizes.csv", index=False)
    outcomes.outcomes(votes).to_csv(tables / "outcomes_by_condition.csv", index=False)

    # ---- figures
    fig_dir = out / "figures"
    fig_dir.mkdir(exist_ok=True)
    figures.fig4_interaction(votes, fig_dir / "fig4_interaction.png").to_csv(tables / "fig4_data.csv", index=False)
    figures.fig5_fig6(gov, texts, fig_dir).to_csv(tables / "fig5_fig6_data.csv", index=False)
    figures.fig_sensitivity(variants, fig_dir / "sensitivity_pvalues.png")

    cmp = compare.build_all(votes, gov, texts, table1(votes), fig_dir, tables)
    compare.vdem_text_check(tables).to_csv(tables / "vdem_text_check.csv", index=False)

    # ---- Figs 3, 8, 9 (see docs/FIGURE_COMPARISON.md, sections 7-9)
    long3, sum3 = fig3.consistency_table()
    long3.to_csv(tables / "fig3_caption_vs_figure.csv", index=False)
    sum3.to_csv(tables / "fig3_summary.csv", index=False)
    fig3.fig3_pair(fig_dir / "fig3_paper_layout_pair.png")
    diag8, ours8 = fig8.diagnostics(gov, value, n_null=100 if args.quick else 500)
    diag8.to_csv(tables / "fig8_diagnostics.csv", index=False)
    ours8.to_csv(tables / "fig8_our_matrix_row_index_pairing.csv")
    fig8.fig8_pair(gov, value, fig_dir / "fig8_paper_vs_replication.png")
    if fig9.spacy_available():
        m9, elbow9, stab9, summ9 = fig9.analyse()
        m9[["x", "y", "cluster", "count"]].to_csv(tables / "fig9_points.csv", index=False)  # no message text
        elbow9.to_csv(tables / "fig9_elbow.csv", index=False)
        stab9.to_csv(tables / "fig9_stability.csv", index=False)
        summ9.to_csv(tables / "fig9_cluster_summary.csv", index=False)
        fig9.fig9_paper_layout(m9, summ9, fig_dir / "fig9_tsne_substitute_embedding.png")
        fig9.fig_elbow(elbow9, fig_dir / "fig9_elbow.png")
    else:
        print("Fig. 9 skipped: install scikit-learn, spacy and en_core_web_md (see README).")

    # ---- verification report
    checks = verify.run_checks(votes, gov)
    md = verify.to_markdown(
        checks,
        {
            "Survey statistics quoted in the text but not reproduced": verify.computed_mismatch_details(gov),
            "Sample sizes in the released files": sizes,
            "Rows that leave part of the budget unallocated": unspent,
        },
    )
    (out / "verification_report.md").write_text(md, encoding="utf-8")

    ok = sum(c.ok for c in checks)
    explained = sum(c.explained for c in checks)
    unexplained = len(checks) - ok - explained
    print(f"{ok}/{len(checks)} numbers match the paper; {explained} documented mismatches; {unexplained} unexplained.")
    print(f"Outputs in {out}")
    return 0 if unexplained == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
