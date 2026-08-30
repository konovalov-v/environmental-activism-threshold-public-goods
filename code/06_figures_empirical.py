"""
Step 6 -- empirical figures (Figures 5 and 6 of the paper).

Input   data/interim/country_aggregates.csv
Output  output/figures/Fig5_trust_vs_certainty.png
        output/figures/Fig6_income_vs_certainty.png

Country-level bubble charts:
  * x-axis  "certainty degree" -- the share of respondents in a country who
    DISAGREE (answer 4 or 5) with v202, "There is no point in doing what I can
    for the environment unless others do the same";
  * y-axis  the country share answering 1 to v31 ("most people can be trusted")
    in Figure 5, and the country mean of the income-decile variable v261 in
    Figure 6;
  * bubble area   proportional to the EVS population weight ``pweight``;
  * colour        European sub-region.

The published figures were produced with plotly; this script reproduces them
with plotly and writes static PNGs via kaleido.  The published files use the
Palatino font, which must be installed locally for an exact visual match;
the data plotted are unaffected by the font.
"""

from __future__ import annotations

import sys

import pandas as pd

from config import DATA_INTERIM, FIGURES

try:
    import plotly.express as px
except ImportError:  # pragma: no cover
    sys.exit("plotly is required for this step:  pip install plotly kaleido")


def bubble(df: pd.DataFrame, ycol: str, ylab: str, fname: str) -> None:
    fig = px.scatter(
        df, x="certainty_degree", y=ycol,
        size="pweight", color="europe_part",
        hover_name="c_abrv", size_max=100, text="c_abrv",
        labels={"certainty_degree": "Certainty degree", ycol: ylab,
                "pweight": "Population size", "europe_part": "Europe region",
                "c_abrv": "Country"},
    )
    fig.update_layout(xaxis_title="Certainty degree", yaxis_title=ylab,
                      legend_title="Europe region",
                      legend=dict(title_font=dict(size=25), itemsizing="constant"),
                      font=dict(family="Palatino", size=25))
    fig.update_traces(textfont=dict(size=14))
    fig.write_image(str(FIGURES / fname), width=2790, height=964, scale=1)
    print("wrote", FIGURES / fname)


def main() -> None:
    path = DATA_INTERIM / "country_aggregates.csv"
    if not path.exists():
        sys.exit(f"{path} not found -- run 01_prepare_data.py first.")
    df = pd.read_csv(path)
    bubble(df, "trust", "Trust", "Fig5_trust_vs_certainty.png")
    bubble(df, "average_income", "Average income", "Fig6_income_vs_certainty.png")


if __name__ == "__main__":
    main()
