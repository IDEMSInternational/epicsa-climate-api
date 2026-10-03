# Climate Variable Naming Discrepancies & Standardization Guide

This document provides a comprehensive analysis of the variable naming architecture, fragmentation, historical causes, and standardized conventions for the E-PICSA analytical PostgreSQL database (`summary` and `definition` tables).

---

## 1. Overview & Database Architecture

The E-PICSA analytical database stores climate summaries produced by **R-Instat** and [`epicsawrap`](https://github.com/IDEMSInternational/epicsawrap) using an **Entity-Attribute-Value (EAV)** design:

```
summary table:
  ├── station_id       VARCHAR(255)  -- e.g. 'MAGOYE AGROMET', 'BEITBRIDGE (MET)'
  ├── definition_id    VARCHAR(255)  -- Batch session ID linking metadata in definition table
  ├── time_type        VARCHAR(255)  -- 'annual', 'monthly'
  ├── time_value       VARCHAR(255)  -- Year ('1981') or Year-Month ('1981-Jul')
  ├── summary_type     VARCHAR(255)  -- 'Annual Rain', 'Annual Temperature', etc.
  ├── summary_element  VARCHAR(255)  -- Conceptual metric type (e.g. 'total_rain', 'start_rain')
  ├── summary_name     VARCHAR(255)  -- R column name or variant (e.g. 'Annual_rainfall', 'OND_rainfall')
  └── summary_value    VARCHAR(255)  -- Metric value (numeric or string)
```

### Why Both `summary_element` and `summary_name` Exist
1. **1-to-Many Metrics**: For a single year, a station can measure multiple variations of the same general concept. For example, under `summary_element = 'total_rain'`, a station may have full-year rainfall (`Annual_rainfall`) and 3-month quarterly blocks (`OND_rainfall`). Without `summary_name`, these rows would collide.
2. **R Calculation Outputs**: Multi-column calculation outputs from R (e.g. Day-of-Year, Calendar Date, Boolean Status for start of rains) share a semantic element (`start_rain`, `start_rain_date`, `start_rain_status`) while preserving their R dataframe column names in `summary_name` (`start`, `start_d`, `start_s`).
3. **Where They Are Redundant**: For 1:1 metrics like `end_season` or `end_rains`, `summary_name` is merely a duplicate copy of `summary_element`.

### The Core Problem: Zero Database-Level Constraints
Inspecting PostgreSQL system catalogs (`information_schema.columns`, `pg_constraint`, `pg_trigger`):
* `summary_element`, `summary_name`, and `summary_type` are completely unconstrained `character varying(255) NULL`.
* There are **no CHECK constraints**, **no ENUM types**, and **no foreign key validations** on variable names.
* Any ingestion script or R code can write arbitrary strings, resulting in wide naming fragmentation across national datasets.

---

## 2. Root Causes of Naming Inconsistencies

1. **Disparate National Ingestion Pipelines**:
   * **Zimbabwe** scripts generated `Oct_Apr_PRECIP` for annual totals and `seasonal_total_rain` / `seasonal_PRECIP` for seasonal totals.
   * **Zambia** scripts generated `Annual_rainfall` for annual totals, and dumped seasonal totals under generic `total_rain` with names like `Seasonal_Rain` or `seasonal_Rainfall`.
   * **Malawi** scripts generated `sum_PRECIP` and `sum_rain_day`.
2. **Category Overloading**:
   * `summary_element = 'total_rain'` was overloaded to hold annual totals, seasonal totals, and 3-month quarterly blocks (OND, DJF, JFM, FMA, NDJ).
   * `summary_element = 'rain_day'` was overloaded to hold both annual rain days and seasonal rain days.
3. **Spelling, Casing, and Ingestion Typos**:
   * Same variable with multiple casings: `Oct_Apr_rainday` vs `oct_apr_rainday` vs `Oct_Apr_RainyDay` vs `Oct_apr_rainday`.
   * Typos in scripts: `star_dry_d` (missing the 't' in `start_dry_d`).
4. **Disconnect between Data and Definition Tables**:
   * The `definition` metadata table defines `summary_element = 'seasonal_rain'`.
   * The data table (`summary`) uses `seasonal_total_rain` (Zimbabwe) or `total_rain` (Zambia). Neither matches the definition table's element.

---

## 3. Station Duplication & The Seasonal Rainfall Coverage Reality

A naive count of the database shows 136 rows in `station` and 131 distinct `(station_id, country_code)` combinations referenced historically. However, **a significant portion of these rows are duplicates caused by dual numeric vs. text station IDs and repeated metadata ingestion**.

### A. Zimbabwe Station Duplication (Numeric vs. Text IDs)
In Zimbabwe (`country_code = 'zim'` in the database):
- The `station` table contains **48 rows**, but there are **only 16 physical meteorological stations**.
- Each of the 16 physical stations is stored under **two different identity paradigms**:
  1. **Text Name**: e.g., `'BEITBRIDGE (MET)'` (16 stations)
  2. **8-Digit Numeric WMO ID**: e.g., `'67991020'` (16 stations, with each numeric row repeated twice in `station` = 32 numeric rows)
- **Data Fragmentation in `summary` Table**:
  - Rainfall summaries (`Annual Rain`, `Annual Temperature`, `Monthly Temperature`) were ingested exclusively under the **text IDs** (e.g., `BEITBRIDGE (MET)` has 196,396 rows).
  - A separate, partial ingestion run wrote `Annual-Monthly Temperature` summaries under the **numeric IDs** (e.g., `67991020` has 2,678 rows).
- **Physical Reality of Seasonal Rainfall**:
  - Because all 16 text stations have seasonal rainfall totals, **16 of 16 (100%) physical stations in Zimbabwe have seasonal total rainfall**.
  - The apparent "16 of 48 stations" was purely a statistical artifact of the 32 numeric duplicate rows in the `station` table.

| Physical Station Name | Text `station_id` (Rainfall Summaries) | Numeric WMO `station_id` (Partial Temp Summaries) | Has Seasonal Rain? |
|---|---|---|---|
| Beitbridge | `BEITBRIDGE (MET)` | `67991020` | Yes |
| Buffalo Range | `BUFFALO RANGE (MET)` | `67977040` | Yes |
| Buhera | `BUHERA (MET)` | `67875010` | Yes |
| Chipinge | `CHIPINGE (MET)` | `67983030` | Yes |
| Chisengu | `CHISENGU (MET)` | `67897020` | Yes |
| Chisumbanje | `CHISUMBANJE (MET)` | `67985020` | Yes |
| Kezi | `KEZI (MET)` | `67961020` | Yes |
| Makoholi Exp. Station | `MAKOHOLI EXP. STATION (MET)` | `67879020` | Yes |
| Masvingo Airport | `MASVINGO AIRPORT (MET)` | `67975040` | Yes |
| Matopos Res. Station | `MATOPOS RES. STN. (MET)` | `67963040` | Yes |
| Nyanga Exp. Station | `NYANGA EXP. STN. (MET)` | `67889030` | Yes |
| Plumtree | `PLUMTREE (MET)` | `67951020` | Yes |
| Rupike Irrigation Scheme | `RUPIKE IRRIGATION SCHEME (MET)` | `67976010` | Yes |
| Rusape | `RUSAPE (MET)` | `67881040` | Yes |
| West Nicholson | `WEST NICHOLSON (MET)` | `67969020` | Yes |
| Zaka | `ZAKA (MET)` | `67979020` | Yes |

*Note: The API's v2 station endpoint intentionally filters out numeric IDs (`not sid.isdigit()`) to prevent exposing duplicate stations to frontend applications.*

---

### B. Zambia Station Duplication (Text Names vs. 8-Char Codes)
In Zambia (`country_code = 'zm'`):
- The `station` table contains **82 rows**, but 5 stations are duplicated **7 times each**:
  - `CHIPATA MET`, `LUNDAZI MET`, `MFUWE MET`, `MSEKERA AGROMET`, and `PETAUKE MET` (35 rows for just 5 stations).
- An additional 5 rows exist with `country_code IS NULL` using **8-character codes**:
  - `CHIPAT01`, `LUNDAZ01`, `MFUWE001`, `MSEKER01`, `PETAUK01`.
- In the `summary` table:
  - There are **53 distinct station IDs**: 48 text stations (e.g. `MAGOYE AGROMET`, `CHOMA MET`) and the 5 duplicate 8-character codes (`CHIPAT01`, etc.).
  - Out of the 48 true physical stations, **only 8 have seasonal total rainfall**; 40 have **none**.

### Physical Station Seasonal Rain Summary
- **Zimbabwe**: **16 of 16 (100%)** physical stations have seasonal rain.
- **Zambia**: **8 of 48 (~17%)** physical stations have seasonal rain:
  - Stations with seasonal rain: `CHINSALI FTC`, `ISOKA MET`, `KALABO MET`, `KAOMA MET`, `MONGU MET`, `MPIKA MET`, `SENANGA MET`, `SESHEKE MET` (typical range: 420 to 1,501 mm).
  - Stations without seasonal rain (40 stations): `MAGOYE AGROMET`, `CHOMA MET`, `KABWE MET`, `LIVINGSTONE MET`, `LUSAKA INT. AIRPOR`, `NDOLA MET`, etc.
  - For these stations, the R-Instat team only calculated full-year rainfall (`Annual_rainfall`) and quarterly sub-seasonal blocks (e.g. `OND_rainfall`). They never calculated rainfall accumulation between `start_rains` and `end_season`.
- **Malawi**: 0 stations in the analytical database currently.

---

## 4. Full Census of Rainfall Variables in Production

Across the **863,205 rainfall rows** in the production database, there are **92 distinct combinations**:

### A. Annual Rainfall Total (10 variants · 50,507 rows)
Stored under `summary_element = 'total_rain'`:
* `Oct_Apr_PRECIP` (22,672 rows, 16 stations)
* `oct_apr_PRECIP` (11,241 rows, 16 stations)
* `sum_PRECIP` (6,465 rows, 21 stations)
* `Oct_apr_PRECIP` (3,774 rows, 16 stations)
* `Annual_rainfall` (2,843 rows, 48 stations)
* `annual_rainfall` (1,357 rows, 16 stations)
* `sum_rain` (1,304 rows, 9 stations)
* `annual_Rainfall` (540 rows, 5 stations)
* `Annual_Rain` (159 rows, 3 stations)
* `sum_rainfall` (152 rows, 3 stations)

### B. Seasonal Rainfall Total (4 variants · 38,466 rows)
* `[seasonal_total_rain] "seasonal_PRECIP"` (25,837 rows, 16 stations)
* `[seasonal_total_rain] "season_PRECIP"` (11,930 rows, 16 stations)
* `[total_rain] "seasonal_Rainfall"` (540 rows, 5 stations)
* `[total_rain] "Seasonal_Rain"` (159 rows, 3 stations)

### C. Sub-seasonal 3-Month Blocks (15 variants · 10,983 rows)
Stored under `summary_element = 'total_rain'` alongside annual totals:
* **OND** (Oct–Dec): `OND_rainfall` (3,147), `OND_rain` (785), `OND_Rainfall` (539)
* **DJF** (Dec–Feb): `DJF_rainfall` (304), `DJF_rain` (785), `DJF_Rainfall` (539)
* **JFM** (Jan–Mar): `JFM_rainfall` (304), `JFM_rain` (785), `JFM_Rainfall` (539)
* **FMA** (Feb–Apr): `FMA_rainfall` (304), `FMA_rain` (785), `FMA_Rainfall` (539)
* **NDJ** (Nov–Jan): `NDJ_rainfall` (304), `NDJ_rain` (785), `NDJ_Rainfall` (539)

### D. Annual Rain Days (14 variants · 50,503 rows)
Stored under `summary_element = 'rain_day'`:
* `Oct_Apr_rainday` (13,103 rows), `oct_apr_rainday` (11,241 rows), `Oct_Apr_RainyDay` (8,156 rows)
* `sum_rain_day` (5,442 rows), `No_of_raindays` (2,843 rows), `sum_rainday` (2,655 rows)
* `Oct_apr_rainday` (1,887 rows), `Oct_apr_rainyday` (1,887 rows), `Oct_Apr_Rainday` (1,413 rows)
* `sum_rainy` (769 rows), `annual_rainday` (540 rows), `annual_rainy` (328 rows)
* `Annual_Raindays` (159 rows), `sum_count` (80 rows)

### E. Seasonal Rain Days (6 variants · 38,466 rows)
* `[seasonal_rain_day] "seasonal_rainday"` (24,424 rows, 16 stations)
* `[seasonal_rain_day] "season_RainyDay"` (8,156 rows, 16 stations)
* `[seasonal_rain_day] "seasonal_Rainday"` (3,300 rows, 16 stations)
* `[seasonal_rain_day] "season_rainyday"` (1,887 rows, 16 stations)
* `[rain_day] "seasonal_rainday"` (540 rows, 5 stations)
* `[rain_day] "Seasonal_Raindays"` (159 rows, 3 stations)

### F. Start of Rains (25 variants · 247,465 rows)
* **DOY (`start_rain`)**: `start` (40k), `start_dry` (18k), `start_rains` (11k), `start_season` (11k), `start_Dry` (8k), `start_dryspell`, `start_drySpell`, `DrySpell`.
* **Date (`start_rain_date`)**: `start_d` (40k), `start_dry_d` (18k), `start_rains_date` (11k), `start_season_date` (11k), `start_Dry_d` (8k), `star_dry_d` (*typo*), `start_d_dryspell`, `start_d_drySpell`, `DrySpell_d`.
* **Status (`start_rain_status`)**: `start_dry_s` (18k), `start_rains_status` (11k), `start_season_status` (11k), `start_s` (10k), `start_Dry_s` (8k), `start_s_dryspell`, `start_s_drySpell`, `DrySpell_s`.

### G. End of Rains, End of Season, Season Length, & Dry Spells
* **End of Rains** (3 variants · 137k rows): `end_rains`, `end_rains_date`, `end_rains_status`.
* **End of Season** (3 variants · 129k rows): `end_season`, `end_season_date`, `end_season_status`.
* **Season Length** (3 variants · 58k rows): `length` (35k), `length_rains` (11k), `length_season` (11k).
* **Dry Spells** (3 variants · 60k rows): `spells` (39k), `spells_90` (20k), `spells_DJFM` (538).

---

## 5. API Anti-Corruption Layer Architecture

To isolate downstream consumers from this database mess:
1. **Module**: [`app/services/variable_mappings.py`](app/services/variable_mappings.py) defines a centralized `ANNUAL_RAIN_EXACT_MAP` dictionary.
2. **Precedence Rules**:
   - Seasonal totals are matched **before** generic `total_rain`.
   - Sub-seasonal 3-month blocks (`ond_`, `djf_`, `jfm_`, `fma_`, `ndj_`) are explicitly excluded so they never overwrite full-year annual totals.
   - Seasonal rain days are matched **before** generic `rain_day`.
3. **Clean Consumption**:
   In [`app/services/climate_repository.py`](app/services/climate_repository.py), the pivoting loop delegates directly to:
   ```python
   field_mapping = map_annual_rain_field(elem, name, val)
   if field_mapping:
       canonical_field, parsed_val = field_mapping
       entry[canonical_field] = parsed_val
   ```

---

## 6. Target Standardization Specification for R-Instat Team

When coordinating with the R-Instat / `epicsawrap` team to standardize future data exports, provide them with this specification:

### A. Canonical Identifiers (Lowercase snake_case only)
| Metric Concept | `summary_type` | `summary_element` | `summary_name` |
|---|---|---|---|
| Annual Total Rainfall | `Annual Rain` | `total_rain` | `annual_rain` |
| Seasonal Total Rainfall | `Annual Rain` | `seasonal_total_rain` | `seasonal_rain` |
| Annual Rainy Days Count | `Annual Rain` | `rain_day` | `annual_rain_days` |
| Seasonal Rainy Days Count | `Annual Rain` | `seasonal_rain_day` | `seasonal_rain_days` |
| Start of Rains DOY | `Annual Rain` | `start_rain` | `start_rains` |
| Start of Rains Date | `Annual Rain` | `start_rain_date` | `start_rains_date` |
| Start of Rains Status | `Annual Rain` | `start_rain_status` | `start_rains_status` |
| End of Rains DOY | `Annual Rain` | `end_rain` | `end_rains` |
| End of Rains Date | `Annual Rain` | `end_rain_date` | `end_rains_date` |
| End of Rains Status | `Annual Rain` | `end_rain_status` | `end_rains_status` |
| End of Season DOY | `Annual Rain` | `end_season` | `end_season` |
| End of Season Date | `Annual Rain` | `end_season_date` | `end_season_date` |
| End of Season Status | `Annual Rain` | `end_season_status` | `end_season_status` |
| Season Duration | `Annual Rain` | `season_length` | `season_length` |

### B. Structural Segregation of Sub-seasonal (Quarterly) Rainfall
* **Do NOT** dump 3-month blocks (`OND`, `DJF`, etc.) into `summary_type = 'Annual Rain'` under `summary_element = 'total_rain'`.
* **DO** use a distinct summary type: `summary_type = 'Quarterly Rain'` with `summary_element = 'total_rain'` and `summary_name = 'ond_rain'`.

### C. Missing Computations for Zambia
* Ensure the seasonal rainfall accumulation routine (rainfall accumulated between `start_rains` and `end_season`) is executed for all 82 Zambian stations.

---

## 7. Running the Audit & Drift-Detection Tool

To scan the database for new or unmapped variable names:

```bash
# Human-readable summary
python -m app.scripts.audit_variables

# Strict CI check (exits with code 1 if unmapped variables are found)
python -m app.scripts.audit_variables --strict

# Generate markdown table for reporting
python -m app.scripts.audit_variables --markdown

# Output JSON
python -m app.scripts.audit_variables --json
```
