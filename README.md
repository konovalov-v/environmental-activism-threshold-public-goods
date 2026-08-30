# Replication package

**Understanding Mechanisms Behind Different Environmental Activism Levels via a Model of Individual Contributions to Public Goods**

Vladimir Konovalov · Marina Sandomirskaia

This repository contains everything needed to reproduce the figures, tables and
reported numbers of the paper, apart from the survey microdata, which cannot be
redistributed (see [`data/README.md`](data/README.md)).

---

## Quick start

```bash
git clone <this repository>
cd environmental-activism-threshold-public-goods
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Theoretical figures need no data at all:
python run_all.py --theory

# Everything else needs the EVS file (see data/README.md), then:
python run_all.py
```

The required Python packages are listed in `requirements.txt`.

---

## Layout

```
code/
  config.py                 paths and analysis constants (no absolute paths)
  01_prepare_data.py        EVS .sav  ->  analysis sample + country aggregates
  02_descriptives.py        Table 12, chi-squared test, Cramer's V
  03_ordered_logit.py       Table 5 (both ordered logits)
  04_marginal_effects.py    Tables 6, 7, 9, 10 and the trust effects in the text
  05_figures_theory.py      Figures 1-4   (no data required)
  06_figures_empirical.py   Figures 5-6
data/
  README.md                 EVS acquisition instructions and expected structure
  raw/                      put ZA7500_v5-0-0.sav here (git-ignored)
  interim/                  derived analysis file (git-ignored)
notebooks/original/         interactive guides to the empirical analysis and
                            theoretical figures
output/
  figures/                  Figures 1-6
  tables/                   all tables, as CSV and plain text
run_all.py                  runs the pipeline in order
```

## What reproduces what

| Paper object | Script | Needs EVS data |
|---|---|---|
| Figure 1 — $q(p)$, known threshold, varying $k$ and $n$ | `05_figures_theory.py` | no |
| Figure 2 — $G^{-1}(p)$ vs $q(p)$, three cost distributions | `05_figures_theory.py` | no |
| Figure 3 — $G^{-1}(p)$ vs $\omega(p)$, varying $z$ | `05_figures_theory.py` | no |
| Figure 4 — $G^{-1}(p)$ vs $\omega(p)$, varying $\alpha$ | `05_figures_theory.py` | no |
| Figure 5 — trust vs certainty degree | `06_figures_empirical.py` | yes |
| Figure 6 — average income vs certainty degree | `06_figures_empirical.py` | yes |
| Figure 7 — Bicchieri decision tree | drawn in LaTeX in the manuscript | — |
| Figure 8 — stacked bar chart (Appendix) | drawn in LaTeX (pgfplots) in the manuscript | — |
| Table 5 — ordered logit estimates | `03_ordered_logit.py` | yes |
| Tables 6, 7 — AMEs, size of town | `04_marginal_effects.py` | yes |
| Tables 9, 10 — AMEs, income decile | `04_marginal_effects.py` | yes |
| Table 11 — variable definitions | none (documentation table) | — |
| Table 12 — contingency table, Cramér's V | `02_descriptives.py` | yes |

Figures 1–4 are deterministic evaluations of closed-form expressions on a
100-point grid; no random numbers are used anywhere in the paper, so no seed is
required. The empirical steps are likewise deterministic given the input file
(maximum likelihood by BFGS from statsmodels' default start values).

## Notebooks

`notebooks/original/` contains two interactive guides to the analysis. Each
notebook explains the relevant methods, runs the corresponding scripts in
`code/`, and displays the main results:

* `01_empirical_analysis_as_run.ipynb` covers data preparation, descriptive
  results, the ordered-response models, changes in predicted probabilities,
  and Figures 5–6. It requires the EVS data described in `data/README.md`.
* `02_theoretical_figures_as_run.ipynb` presents the model calculations behind
  Figures 1–4. It does not require external data.

Paths are resolved from the repository root. When running the scripts
directly, the EVS file location can also be supplied through the `EVS_SAV`
environment variable.

## Data availability

No EVS data — raw or respondent-level derived — is included in this
repository. See [`data/README.md`](data/README.md) for the citation, the DOI,
registration and download instructions, the expected file structure and the
sample sizes the pipeline should reproduce.

## Citing

If you use this code, please cite the paper and the underlying data:

> Konovalov, V. and M. Sandomirskaia. *Understanding Mechanisms Behind
> Different Environmental Activism Levels via a Model of Individual
> Contributions to Public Goods.*

> EVS (2022): *European Values Study 2017: Integrated Dataset (EVS 2017).*
> GESIS Data Archive, Cologne. ZA7500 Data file Version 5.0.0.
> <https://doi.org/10.4232/1.13897>

## Licence

Code: MIT (see [`LICENSE`](LICENSE)). The licence does not extend to the EVS
microdata, which remain subject to the GESIS terms of use.
