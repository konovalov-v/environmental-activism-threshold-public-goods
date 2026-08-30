# Data

## What the paper uses

The empirical section of the paper uses **one** dataset:

> EVS (2022): *European Values Study 2017: Integrated Dataset (EVS 2017)*.
> GESIS Data Archive, Cologne. **ZA7500 Data file Version 5.0.0.**
> <https://doi.org/10.4232/1.13897>

The analysis requires `ZA7500_v5-0-0.sav`, the EVS 2017 fifth-wave data file,
version **5.0.0**. Earlier releases of ZA7500 carry different DOIs and differ
in country coverage and variable derivation, so they are not interchangeable
with this version.

The theoretical part of the paper (Sections 2 and Figures 1–4) uses no data at all; it evaluates closed-form expressions.

## Why the data are not in this repository

The EVS Integrated Dataset is distributed by the GESIS Data Archive under
terms that require each user to register and accept the data-use conditions
before download. Redistribution by third parties is not permitted, so **no EVS
data — raw or derived at the respondent level — is included here.** The
`data/raw/` and `data/interim/` directories are created empty by the code and
are excluded from version control.

## How to obtain it

1. Go to the GESIS study page for ZA7500:
   <https://search.gesis.org/research_data/ZA7500>
   (or resolve the DOI <https://doi.org/10.4232/1.13897>).
2. Register for a free GESIS account and accept the EVS data-use conditions.
3. Download the **SPSS** distribution of **Data file Version 5.0.0**
   (`ZA7500_v5-0-0.sav`, roughly 100 MB).
4. Place the file at `data/raw/ZA7500_v5-0-0.sav`, or point the pipeline at it:

   ```bash
   export EVS_SAV=/path/to/ZA7500_v5-0-0.sav
   ```

Study documentation, including the full variable report and the method report,
is linked from the same GESIS page.

## Expected input structure

`code/01_prepare_data.py` reads the `.sav` with `pyreadstat` and expects a
respondent-level file with **59,438 rows** and the following columns:

| Column    | Type | Meaning in the paper |
|-----------|------|----------------------|
| `c_abrv`  | str  | ISO country abbreviation (`AL`, `AM`, …) |
| `country` | num  | numeric country code |
| `year`    | num  | fieldwork year |
| `v31`     | 1/2  | Q7 generalised trust. 1 = "most people can be trusted", 2 = "can't be too careful". Enters the index function in this original coding, so a **positive** coefficient means the *less* trusting are more likely to be in higher categories |
| `v199`    | 1–5  | Q56 "I would give part of my income if I were certain that the money would be used to prevent environmental pollution" — the paper's **"actual involvement"** outcome, column (2) of Table 5 |
| `v202`    | 1–5  | Q56 "There is no point in doing what I can for the environment unless others do the same" — the paper's **"uncertainty degree"** outcome, column (1) of Table 5 |
| `v261`    | 1–10 | Q98 household income decile |
| `v276_r`  | 1–5  | Q106 size of town, recoded: 1 = under 5,000 … 5 = 500,000 and more |
| `pweight` | num  | EVS population-size weight; used only for bubble area in Figures 5–6 |

Both 5-point items are collapsed to three ordered categories
(1 + 2 → 1 "Agree"; 3 → 2 "Neither"; 4 + 5 → 3 "Disagree").

## Sample sizes the pipeline should reproduce

| Step | N | Where it appears |
|---|---|---|
| File as distributed | 59,438 | — |
| After listwise deletion on `v31, v202, v261, v199, v276_r` | **48,123** | Table 12 (contingency table), Figures 5–6, Cramér's V |
| Estimation sample | **43,001** | Table 5, Tables 6–7 and 9–10 |

If your run does not hit 48,123 and 43,001, you are almost certainly using a
different data file version.

