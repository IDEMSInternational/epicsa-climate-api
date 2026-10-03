# Database Variable Auditing & Drift Detection Guide

This guide explains how to use the automated audit tooling in `epicsa-climate-api` to monitor, detect, and resolve climate variable drift in the analytical PostgreSQL database.

---

## 1. Overview & Purpose

The E-PICSA analytical database stores climate summaries in an **Entity-Attribute-Value (EAV)** structure (`summary` table). Because the underlying PostgreSQL columns (`summary_element`, `summary_name`, `summary_type`) are unconstrained `VARCHAR(255)` without database-level enums or check constraints, data ingestion scripts created by R-Instat or national meteorological teams can introduce new naming variations, typos, or casing discrepancies at any time.

The **Audit Tool** (`app/scripts/audit_variables.py` / `./scripts/audit_variables.py`) performs an exhaustive scan of all records in the live database, cross-referencing each distinct `(summary_element, summary_name)` pair against the declarative mappings in [`app/services/variable_mappings.py`](../app/services/variable_mappings.py).

### Key Capabilities
- **Drift Detection**: Identifies any newly ingested variables that the API does not recognize or map.
- **Categorization**: Segregates variables into **Mapped** (canonical metrics), **Auxiliary** (sub-seasonal blocks, dry spells), and **Unmapped** (discrepancies).
- **CI/CD Enforcement**: The `--strict` flag exits with code `1` if any unmapped variable is found, allowing it to act as an automated build/deployment gate.
- **Multi-Format Export**: Generates human-readable terminal summaries, machine-readable JSON (`--json`), or GitHub-flavored Markdown (`--markdown`).

---

## 2. Prerequisites & Environment Setup

The audit script connects to the PostgreSQL database using the credentials specified in your `postgres-secret.json` file (or the path set in the `POSTGRES_SECRET_FILE` environment variable).

### Local Setup
Ensure your local Python virtual environment is activated and `postgres-secret.json` is present in the repository root:
```bash
# Verify credentials exist
ls -la postgres-secret.json

# If not, create from example:
cp postgres-secret-example.json postgres-secret.json
# (Edit postgres-secret.json with your host, user, password, and dbname)
```

---

## 3. How to Run the Audit Tool

### Option A: Using the Host Script Wrapper (Recommended)
```bash
# Standard terminal report
./scripts/audit_variables.py

# Strict mode (fails if unmapped variables exist)
./scripts/audit_variables.py --strict
```

### Option B: Running as a Python Module
```bash
# Standard report
python -m app.scripts.audit_variables

# Strict mode
python -m app.scripts.audit_variables --strict
```

### Option C: Running Inside Docker Container
If local Python or database network access is restricted:
```bash
docker compose exec app python -m app.scripts.audit_variables --strict
```

---

## 4. Command-Line Options & Flags

| Flag | Type | Description | Example |
|---|---|---|---|
| `--strict` | Flag | Exit with code `1` if any unmapped variables exist; exit `0` only if 100% mapped. | `./scripts/audit_variables.py --strict` |
| `--summary-type` | String | Restrict audit to a specific summary type (e.g., `'Annual Rain'`, `'Annual Temperature'`). | `./scripts/audit_variables.py --summary-type "Annual Rain"` |
| `--markdown` | Flag | Output results formatted as GitHub-flavored Markdown tables. | `./scripts/audit_variables.py --markdown > audit.md` |
| `--json` | Flag | Output results formatted as JSON. | `./scripts/audit_variables.py --json > audit.json` |
| `--help` | Flag | Display CLI options and usage documentation. | `./scripts/audit_variables.py --help` |

---

## 5. Interpreting the Audit Report

### Sample Output (Clean State)
```text
======================================================================
 E-PICSA DATABASE VARIABLE AUDIT REPORT
======================================================================
Total Variable Pairs Checked: 123
Total Data Rows Represented:  2,175,940
  - Fully Mapped to Schema:   99
  - Auxiliary / Sub-seasonal: 24
  - Unmapped / Discrepancies: 0
----------------------------------------------------------------------

[✓] All database variables are 100% accounted for in variable mappings!
======================================================================
```

### Categorization Logic
1. **Fully Mapped (`mapped`)**:
   - The variable matches an entry in `ANNUAL_RAIN_EXACT_MAP` or satisfies a canonical standard metric (e.g. `tmax_mean`, `monthly_rain`).
   - The API successfully pivots this into the correct Pydantic response field.
2. **Auxiliary / Sub-seasonal (`auxiliary`)**:
   - The variable is recognized as valid domain data, but is **intentionally excluded** from annual summaries (e.g. 3-month blocks like `OND_rainfall`, dry spells, crop metrics).
   - These are prevented from accidentally overwriting annual totals.
3. **Unmapped / Discrepancies (`unmapped`)**:
   - The variable is unknown to the mapping layer.
   - It will either be dropped or could cause erroneous fallbacks. Requires investigation and registration.

---

## 6. Resolution Workflow: When Drift Is Detected

When the audit tool reports unmapped variables (or CI fails on `--strict`):

```
[!] 2 UNMAPPED VARIABLE DISCREPANCIES DETECTED:
----------------------------------------------------------------------------------------------------
Type                 Element              Name                 Rows       Stations   Sample Value   
----------------------------------------------------------------------------------------------------
Annual Rain          total_rain           Rain_Total_2025      150        3          842.1          
Annual Rain          dry_spell            midseason_dry        45         3          12             
----------------------------------------------------------------------------------------------------
```

### Step-by-Step Fix:
1. **Identify the Semantic Meaning**:
   - Inspect the `summary_element`, `summary_name`, and sample values.
   - Is `Rain_Total_2025` an annual rainfall total, seasonal total, or sub-seasonal block?
2. **Register in [`app/services/variable_mappings.py`](../app/services/variable_mappings.py)**:
   - If it represents a canonical metric, add it to `ANNUAL_RAIN_EXACT_MAP`:
     ```python
     ("total_rain", "rain_total_2025"): ("annual_rain", _safe_float),
     ```
   - If it represents an auxiliary or sub-seasonal block, add it to `ANNUAL_RAIN_AUXILIARY_SET`:
     ```python
     ("dry_spell", "midseason_dry"),
     ```
3. **Add Unit Tests**:
   - Open [`app/tests/test_v2_endpoints.py`](../app/tests/test_v2_endpoints.py) and add test assertions in `test_variable_mappings_exact_matches` or `test_variable_mappings_subseasonal_and_auxiliary_exclusion`.
4. **Update Documentation**:
   - Add the new variable to the inventory in [`docs/CLIMATE_VARIABLE_NAMING_AND_DISCREPANCIES.md`](./CLIMATE_VARIABLE_NAMING_AND_DISCREPANCIES.md).
5. **Verify with Strict Audit**:
   ```bash
   ./scripts/audit_variables.py --strict
   ```
   Ensure the exit code is `0` and unmapped count is `0`.

---

## 7. CI/CD & Ingestion Pipeline Integration

To prevent untested variable drift from reaching production releases, include the strict audit in GitHub Actions workflows or post-ingestion cron jobs:

```yaml
# Example CI Step in .github/workflows/tests.yml
- name: Audit Climate Database Variables
  run: |
    python -m app.scripts.audit_variables --strict
  env:
    POSTGRES_SECRET_FILE: ${{ secrets.POSTGRES_SECRET_FILE }}
```

---

## 8. Station & Data Integrity Audit Tool (`audit_stations.py`)

In addition to variable naming drift, the database can experience **station identity duplication, unpurged batch accumulation, and metadata corruption**.

The Station Audit Tool (`app/scripts/audit_stations.py` / `./scripts/audit_stations.py`) inspects the database for:
1. **Dual-Identity Station Duplications**:
   - Detects stations stored under both numeric WMO IDs (e.g. `67991020`) and text names (e.g. `BEITBRIDGE (MET)`).
   - Detects stations stored under both 8-character codes (e.g. `CHIPAT01`) and full names (e.g. `CHIPATA MET`).
2. **Exact Duplicate Metadata Rows**:
   - Identifies identical rows repeated in the `station` table due to re-ingestion without constraints (e.g., 6 duplicate copies of Eastern Province stations in Zambia).
3. **Inconsistent or NULL Country Codes**:
   - Finds rows with `country_code IS NULL` or non-standard values (e.g. `zim` instead of `zw`, or test codes like `TZ`).
4. **Multi-Batch Accumulation in `summary`**:
   - Flags stations where multiple unpurged `definition_id` batches have accumulated (e.g. Beitbridge with 26 batches), warning of stale unoverwritten data.
5. **Seasonal Rainfall Coverage Gaps**:
   - Lists stations that have `Annual Rain` rows but zero seasonal rainfall totals (e.g. Magoye Agromet).

### Running the Station Audit Tool:
```bash
# Standard report
./scripts/audit_stations.py

# Python module execution
python -m app.scripts.audit_stations

# Strict mode (fails if duplicate stations or metadata issues exist)
python -m app.scripts.audit_stations --strict

# Via Docker:
docker compose exec app python -m app.scripts.audit_stations

# Export as Markdown table
python -m app.scripts.audit_stations --markdown > station_audit.md
```

