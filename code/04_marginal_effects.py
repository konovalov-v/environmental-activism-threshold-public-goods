"""
Step 4 -- average marginal effects (Tables 6, 7, 9, 10 and the trust effects
quoted in the text of Section 3.3).

Input   data/interim/analysis_sample.csv, output/models/*.pkl
Output  output/tables/table6_ame_population_uncertainty.csv
        output/tables/table7_ame_population_involvement.csv
        output/tables/table9_ame_income_uncertainty.csv
        output/tables/table10_ame_income_involvement.csv
        output/tables/ame_trust.txt

Definition used in the paper (its equation for the average marginal effect):

    AME(k; a, b) = (1/N) sum_i [ Pr(y_i = k | x_i = a) - Pr(y_i = k | x_i = b) ]

i.e. the whole sample is evaluated twice, once with the categorical regressor
counterfactually set to level ``a`` for everyone and once with it set to level
``b``, holding all other covariates at their observed values.  In the paper's
tables the COLUMN gives level ``a`` (the "first component") and the ROW gives
level ``b`` (the "second component").

"""

from __future__ import annotations

import pickle

import numpy as np
import pandas as pd
from scipy.special import expit

from config import DATA_INTERIM, OUTPUT, TABLES, TOWN_LABELS

MODELS = OUTPUT / "models"


def build_design(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    X = pd.DataFrame(0, index=df.index, columns=columns, dtype=float)
    for col in columns:
        if col.startswith("country_"):
            X[col] = (df["c_abrv"] == col.removeprefix("country_")).astype(float)
        elif col.startswith("v261_"):
            X[col] = (df["v261"] == float(col.removeprefix("v261_"))).astype(float)
        elif col.startswith("v276_r_"):
            X[col] = (df["v276_r"] == float(col.removeprefix("v276_r_"))).astype(float)
        elif col == "v31":
            X[col] = df["v31"].astype(float)
        else:
            raise ValueError(f"unrecognised design column {col!r}")
    return X


def probabilities(Xb: np.ndarray, tau1: float, tau2: float) -> np.ndarray:
    """Return an (N, 3) array of P(y = 1), P(y = 2), P(y = 3)."""
    p1 = expit(tau1 - Xb)
    p2 = expit(tau2 - Xb) - expit(tau1 - Xb)
    p3 = 1.0 - expit(tau2 - Xb)
    return np.column_stack([p1, p2, p3])


def counterfactual_probs(X: pd.DataFrame, beta: np.ndarray, tau1: float, tau2: float,
                         prefix: str, levels: list[float], omitted: float) -> dict:
    """Predicted probabilities with the ``prefix`` dummy block set to each level."""
    out = {}
    block = [c for c in X.columns if c.startswith(prefix)]
    for lev in levels + [omitted]:
        Xc = X.copy()
        for c in block:
            Xc[c] = 0.0
        col = f"{prefix}{lev}"
        if col in block:                       # the omitted level leaves the block at 0
            Xc[col] = 1.0
        out[lev] = probabilities(Xc.to_numpy() @ beta, tau1, tau2)
    return out


def ame_matrix(probs: dict, levels: list[float], labels: dict) -> pd.DataFrame:
    """AME(k; a, b) for every ordered pair, in percentage points, long format."""
    rows = []
    for a in levels:
        for b in levels:
            if a >= b:
                continue
            diff = (probs[a] - probs[b]).mean(axis=0) * 100.0
            rows.append({"column_level_a": labels.get(a, a),
                         "row_level_b": labels.get(b, b),
                         "y1_Agree": diff[0],
                         "y2_Neither": diff[1],
                         "y3_Disagree": diff[2],
                         "sum_check": diff.sum()})
    return pd.DataFrame(rows)


def run(model_label: str, outcome_col: str, table_pop: str, table_inc: str) -> None:
    df = pd.read_csv(DATA_INTERIM / "analysis_sample.csv").dropna(subset=[outcome_col])
    with open(MODELS / f"{model_label}.pkl", "rb") as fh:
        m = pickle.load(fh)

    columns = m["columns"]
    beta = m["params"].to_numpy()[: len(columns)]
    tau1, tau2 = m["tau1"], m["tau2"]
    X = build_design(df, columns)

    # ---- size of town (Tables 6 and 7) ------------------------------------
    town_levels = [1.0, 2.0, 3.0, 4.0]
    probs = counterfactual_probs(X, beta, tau1, tau2, "v276_r_", town_levels, 5.0)
    tab = ame_matrix(probs, town_levels + [5.0], TOWN_LABELS)
    tab.to_csv(TABLES / table_pop, index=False)
    print(f"wrote {TABLES/table_pop}")

    # ---- income decile (Tables 9 and 10) ----------------------------------
    inc_levels = [float(i) for i in range(1, 10)]
    probs = counterfactual_probs(X, beta, tau1, tau2, "v261_", inc_levels, 10.0)
    tab = ame_matrix(probs, inc_levels + [10.0], {float(i): f"decile {i}" for i in range(1, 11)})
    tab.to_csv(TABLES / table_inc, index=False)
    print(f"wrote {TABLES/table_inc}")

    # ---- trust (quoted in the text, not tabulated) ------------------------
    Xa, Xb = X.copy(), X.copy()
    Xa["v31"] = 1.0    # "most people can be trusted"
    Xb["v31"] = 2.0    # "can't be too careful"
    pa = probabilities(Xa.to_numpy() @ beta, tau1, tau2)
    pb = probabilities(Xb.to_numpy() @ beta, tau1, tau2)
    d = (pa - pb).mean(axis=0) * 100.0
    lines = [f"Average marginal effect of trust ({model_label}, {outcome_col})",
             "  trusting (v31 = 1) minus distrusting (v31 = 2), percentage points",
             f"    P(y = 1, Agree)    : {d[0]:+.4f}",
             f"    P(y = 2, Neither)  : {d[1]:+.4f}",
             f"    P(y = 3, Disagree) : {d[2]:+.4f}",
             f"    sum (should be 0)  : {d.sum():+.6f}"]
    text = "\n".join(lines)
    with open(TABLES / "ame_trust.txt", "a", encoding="utf-8") as fh:
        fh.write(text + "\n\n")
    print(text, "\n")


def main() -> None:
    (TABLES / "ame_trust.txt").write_text("", encoding="utf-8")
    run("uncertainty_degree", "v202_decoded",
        "table6_ame_population_uncertainty.csv", "table9_ame_income_uncertainty.csv")
    run("actual_involvement", "v199_decoded",
        "table7_ame_population_involvement.csv", "table10_ame_income_involvement.csv")


if __name__ == "__main__":
    main()
