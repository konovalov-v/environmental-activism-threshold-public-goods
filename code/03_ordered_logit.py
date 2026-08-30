"""
Step 3 -- ordered logit estimation (Table 5).

Input   data/interim/analysis_sample.csv
Output  output/tables/table5_ordered_logit_uncertainty.txt
        output/tables/table5_ordered_logit_involvement.txt
        output/tables/table5_ordered_logit_combined.csv
        output/models/*.pkl   (fitted results, consumed by 04_marginal_effects.py)

Specification (identical in both columns of Table 5):
    y_i in {1, 2, 3}   (1 = Agree, 2 = Neither, 3 = Disagree)
    latent index  X_i'beta  with
        * country fixed effects   (one dummy per country, last one omitted)
        * income decile dummies   v261 = 1..9   (10th decile omitted)
        * size-of-town dummies    v276_r = 1..4 (500,000+ omitted)
        * trust                   v31 entered in its original 1/2 coding,
                                  where 1 = "most people can be trusted"
                                  and   2 = "can't be too careful"
    Column (1) "Uncertainty degree" : y from v202
    Column (2) "Actual involvement" : y from v199

NOTE ON THE CUT-POINTS.  statsmodels' OrderedModel reports the first cut-point
directly and the SECOND as log(tau_2 - tau_1).  Table 5 of the paper reports
the raw parameters; this script prints both the raw parameters and the
transformed cut-points so the two can be compared unambiguously.
"""

from __future__ import annotations

import pickle

import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

from config import DATA_INTERIM, OUTCOMES, OUTPUT, TABLES

MODELS = OUTPUT / "models"
MODELS.mkdir(parents=True, exist_ok=True)


def build_design(df: pd.DataFrame) -> pd.DataFrame:
    """Country / income / town dummies plus trust, with the last level omitted."""
    X = pd.DataFrame(index=df.index)

    for country in sorted(df["c_abrv"].unique())[:-1]:
        X[f"country_{country}"] = (df["c_abrv"] == country).astype(int)
    for dec in sorted(df["v261"].unique())[:-1]:
        X[f"v261_{dec}"] = (df["v261"] == dec).astype(int)
    for town in sorted(df["v276_r"].unique())[:-1]:
        X[f"v276_r_{town}"] = (df["v276_r"] == town).astype(int)

    X["v31"] = df["v31"].to_numpy()
    return X


def fit_one(df: pd.DataFrame, outcome_col: str, label: str):
    sub = df.dropna(subset=[outcome_col]).copy()
    X = build_design(sub)
    y = sub[outcome_col].astype(int)

    model = OrderedModel(y, X, distr="logit")
    res = model.fit(method="bfgs", disp=False)

    _, tau1, tau2, _ = model.transform_threshold_params(res.params)

    txt = [
        f"=== {label}  (dependent variable: {outcome_col}) ===",
        res.summary().as_text(),
        "",
        f"Pseudo R-squared            : {res.prsquared:.6f}",
        f"Number of observations      : {int(res.nobs):,}",
        "",
        "Cut-points",
        f"  raw parameter '1/2'       : {res.params.iloc[-2]:.6f}   (= tau_1)",
        f"  raw parameter '2/3'       : {res.params.iloc[-1]:.6f}   (= log(tau_2 - tau_1))",
        f"  transformed tau_1         : {tau1:.6f}",
        f"  transformed tau_2         : {tau2:.6f}",
    ]
    out = "\n".join(txt)
    (TABLES / f"table5_ordered_logit_{label}.txt").write_text(out + "\n", encoding="utf-8")
    print(out)
    print()

    with open(MODELS / f"{label}.pkl", "wb") as fh:
        pickle.dump({"params": res.params, "bse": res.bse, "pvalues": res.pvalues,
                     "tau1": tau1, "tau2": tau2, "nobs": int(res.nobs),
                     "prsquared": float(res.prsquared),
                     "columns": list(X.columns)}, fh)
    return res, X, tau1, tau2


def main() -> None:
    df = pd.read_csv(DATA_INTERIM / "analysis_sample.csv")

    res_v202, _, _, _ = fit_one(df, "v202_decoded", "uncertainty_degree")
    res_v199, _, _, _ = fit_one(df, "v199_decoded", "actual_involvement")

    combined = pd.DataFrame({
        "coef_uncertainty_degree": res_v202.params,
        "se_uncertainty_degree": res_v202.bse,
        "coef_actual_involvement": res_v199.params,
        "se_actual_involvement": res_v199.bse,
    })
    combined.to_csv(TABLES / "table5_ordered_logit_combined.csv")
    print(f"wrote {TABLES/'table5_ordered_logit_combined.csv'}")


if __name__ == "__main__":
    main()
