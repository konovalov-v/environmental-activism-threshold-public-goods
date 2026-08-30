"""
Project configuration: paths and analysis constants.

All paths are resolved relative to the repository root, so the package runs
unchanged on any machine.  Nothing here depends on the original authors'
directory layout.

The location of the EVS microdata file can be overridden with the environment
variable EVS_SAV, e.g.

    EVS_SAV=/path/to/ZA7500_v5-0-0.sav python code/01_prepare_data.py
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw"          # the EVS .sav file goes here (not redistributed)
DATA_INTERIM = ROOT / "data" / "interim"  # derived analysis file (created by 01_prepare_data.py)
OUTPUT = ROOT / "output"
FIGURES = OUTPUT / "figures"
TABLES = OUTPUT / "tables"

for _d in (DATA_RAW, DATA_INTERIM, OUTPUT, FIGURES, TABLES):
    _d.mkdir(parents=True, exist_ok=True)

#: Default name of the EVS file.  The authors analysed ZA7500 data file
#: version 5.0.0; the file as distributed by GESIS is named ``ZA7500_v5-0-0.sav``.
EVS_FILENAME = "ZA7500_v5-0-0.sav"


def evs_path() -> Path:
    """Return the path to the EVS .sav file, honouring $EVS_SAV."""
    override = os.environ.get("EVS_SAV")
    if override:
        return Path(override).expanduser().resolve()
    return DATA_RAW / EVS_FILENAME


# --------------------------------------------------------------------------
# Analysis constants
# --------------------------------------------------------------------------

#: Variables required by the analysis; observations missing any of them are
#: dropped (this defines the 48,123-observation working sample).
REQUIRED_VARS = ["v31", "v202", "v261", "v199", "v276_r"]

#: 5-point Likert -> 3 ordered categories.
#: 1 "agree strongly" + 2 "agree"            -> 1 (Agree)
#: 3 "neither agree nor disagree"            -> 2 (Neither)
#: 4 "disagree"       + 5 "disagree strongly"-> 3 (Disagree)
LIKERT_TO_3 = {1: 1, 2: 1, 3: 2, 4: 3, 5: 3}

#: Country -> European sub-region, used for the colour grouping of Figures 5 and 6.
COUNTRY_TO_REGION = {
    "AL": "Southern Europe", "AZ": "Eastern Europe",  "AT": "Western Europe",
    "AM": "Eastern Europe",  "BA": "Southern Europe", "BG": "Eastern Europe",
    "BY": "Eastern Europe",  "HR": "Southern Europe", "CZ": "Central Europe",
    "DK": "Northern Europe", "EE": "Northern Europe", "FI": "Northern Europe",
    "FR": "Western Europe",  "GE": "Eastern Europe",  "DE": "Western Europe",
    "HU": "Central Europe",  "IS": "Northern Europe", "IT": "Southern Europe",
    "LV": "Northern Europe", "LT": "Northern Europe", "ME": "Southern Europe",
    "NL": "Western Europe",  "NO": "Northern Europe", "PL": "Central Europe",
    "PT": "Southern Europe", "RO": "Eastern Europe",  "RU": "Eastern Europe",
    "RS": "Central Europe",  "SK": "Central Europe",  "SI": "Central Europe",
    "ES": "Southern Europe", "SE": "Northern Europe", "CH": "Western Europe",
    "UA": "Eastern Europe",  "MK": "Southern Europe", "GB": "Western Europe",
}

#: Labels for the recoded size-of-town variable v276_r.
TOWN_LABELS = {
    1.0: "under 5,000",
    2.0: "5,000--20,000",
    3.0: "20,000--100,000",
    4.0: "100,000--500,000",
    5.0: "500,000 and more",
}

#: The two dependent variables of the paper.
#: Column (1) of Table 5, "Uncertainty degree"  -> v202
#: Column (2) of Table 5, "Actual involvement"  -> v199
OUTCOMES = {
    "uncertainty_degree": "v202",
    "actual_involvement": "v199",
}
