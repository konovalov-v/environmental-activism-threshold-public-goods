"""
Step 1 -- build the analysis sample from the EVS 2017 Integrated Dataset.

Input   data/raw/ZA7500_v5-0-0.sav   (NOT redistributed -- see data/README.md)
Output  data/interim/analysis_sample.csv
        data/interim/country_aggregates.csv
        output/tables/sample_construction.txt

Only the handful of variables the paper actually uses is written out, so the
derived file is small and contains no information beyond what the published
tables already report.  It is still a derivative of the EVS microdata and is
therefore *not* committed to the repository.

Reproduces the sample-construction step behind:
  * the 48,123-observation working sample (Table 12, Figures 5-6);
  * the 43,001-observation estimation sample (Table 5).
"""

from __future__ import annotations

import sys

import pandas as pd
import pyreadstat

from config import (COUNTRY_TO_REGION, DATA_INTERIM, LIKERT_TO_3, REQUIRED_VARS,
                    TABLES, evs_path)

KEEP = ["country", "c_abrv", "year", "v31", "v199", "v202", "v261", "v276_r", "pweight"]


def main() -> None:
    path = evs_path()
    if not path.exists():
        sys.exit(
            f"EVS file not found at {path}.\n"
            "The EVS microdata cannot be redistributed with this repository.\n"
            "See data/README.md for download instructions, then place the .sav\n"
            "file in data/raw/ or set the EVS_SAV environment variable."
        )

    df, meta = pyreadstat.read_sav(str(path))
    log = [f"EVS file                    : {path.name}",
           f"rows as distributed         : {len(df):,}",
           f"columns as distributed      : {df.shape[1]:,}"]

    missing = [v for v in KEEP if v not in df.columns]
    if missing:
        sys.exit(f"Expected variables absent from the file: {missing}. "
                 "Check that this is the EVS 2017 Integrated Dataset (ZA7500).")

    # ---- listwise deletion on the variables the analysis uses ---------------
    df = df.dropna(subset=REQUIRED_VARS).copy()
    log.append(f"after dropping missing on {REQUIRED_VARS}: {len(df):,}")

    df = df[KEEP].copy()

    # ---- recodes -----------------------------------------------------------
    # 5-point Likert -> 3 ordered categories.  Codes outside 1..5 (EVS reserves
    # negative codes for "don't know" / "no answer") map to NaN and are dropped
    # by the estimation step; this is what produces the 43,001-observation
    # estimation sample.
    df["v202_decoded"] = df["v202"].map(LIKERT_TO_3)
    df["v199_decoded"] = df["v199"].map(LIKERT_TO_3)
    log.append(f"non-missing v202_decoded    : {df['v202_decoded'].notna().sum():,}")
    log.append(f"non-missing v199_decoded    : {df['v199_decoded'].notna().sum():,}")

    df["europe_part"] = df["c_abrv"].map(COUNTRY_TO_REGION)

    # ---- country-level aggregates used by Figures 5 and 6 ------------------
    # "trust"            : share answering 1 ("most people can be trusted") to v31
    # "certainty_degree" : share answering 4 or 5 to v202, i.e. share DISAGREEING
    #                      with "there is no point in doing what I can for the
    #                      environment unless others do the same"
    # "average_income"   : country mean of the income-decile variable v261
    agg = (df.groupby("c_abrv")
             .agg(trust=("v31", lambda s: (s == 1).mean()),
                  certainty_degree=("v202", lambda s: s.isin([4, 5]).mean()),
                  average_income=("v261", "mean"),
                  pweight=("pweight", "first"),
                  n_obs=("v31", "size"))
             .reset_index())
    agg["europe_part"] = agg["c_abrv"].map(COUNTRY_TO_REGION)

    df = df.merge(agg[["c_abrv", "trust", "certainty_degree", "average_income"]],
                  on="c_abrv", how="left")

    log.append(f"countries in working sample : {df['c_abrv'].nunique()}")
    log.append("countries                   : " + ", ".join(sorted(df["c_abrv"].unique())))

    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_INTERIM / "analysis_sample.csv", index=False)
    agg.to_csv(DATA_INTERIM / "country_aggregates.csv", index=False)

    # ---- diagnostic on the estimation sample -------------------------------
    n_work = len(df)
    n_est = int(df["v202_decoded"].notna().sum())
    log.append("")
    log.append(f"working sample               : {n_work:,}")
    log.append(f"estimation sample            : {n_est:,}")

    text = "\n".join(log)
    (TABLES / "sample_construction.txt").write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nwrote {DATA_INTERIM/'analysis_sample.csv'}")
    print(f"wrote {DATA_INTERIM/'country_aggregates.csv'}")


if __name__ == "__main__":
    main()
