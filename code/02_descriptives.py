"""
Step 2 -- descriptive statistics.

Input   data/interim/analysis_sample.csv
Output  output/tables/table12_contingency_v199_v202.csv
        output/tables/chi2_cramersv.txt

Reproduces:
  * Table 12 in the Appendix -- the v199 x v202 contingency table
    (rows = v199, columns = v202) and its margins;
  * the chi-squared test of independence and Cramer's V reported in
    Section 3.2 (V = 0.16 in the paper).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from config import DATA_INTERIM, TABLES


def main() -> None:
    df = pd.read_csv(DATA_INTERIM / "analysis_sample.csv")

    # rows = v199 ("I would give part of my income ...")
    # cols = v202 ("There is no point ... unless others do the same")
    table = pd.crosstab(df["v199"], df["v202"])
    table.index = table.index.astype(int)
    table.columns = table.columns.astype(int)

    with_margins = table.copy()
    with_margins["Total"] = with_margins.sum(axis=1)
    with_margins.loc["Total"] = with_margins.sum(axis=0)
    with_margins.to_csv(TABLES / "table12_contingency_v199_v202.csv")

    stat, p, dof, expected = chi2_contingency(table)
    n = int(table.values.sum())
    min_dim = min(table.shape) - 1
    cramers_v = np.sqrt((stat / n) / min_dim)

    lines = [
        "Chi-squared test of independence, v199 x v202",
        f"  N                 = {n:,}",
        f"  chi2              = {stat:.4f}",
        f"  degrees of freedom= {dof}",
        f"  p-value           = {p:.4g}",
        f"  Cramer's V        = {cramers_v:.5f}",
        "",
        "Contingency table (rows = v199, columns = v202), with margins:",
        with_margins.to_string(),
    ]
    text = "\n".join(lines)
    (TABLES / "chi2_cramersv.txt").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
