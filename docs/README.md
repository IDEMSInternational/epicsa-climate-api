# E-PICSA Climate API Documentation

This directory contains technical guides, schema documentation, and audit references for the E-PICSA Climate API.

---

## Documentation Index

### 1. [Climate Variable Naming, Duplication & Discrepancies Guide](CLIMATE_VARIABLE_NAMING_AND_DISCREPANCIES.md)
- **Scope**: Complete audit of PostgreSQL `summary` and `definition` tables.
- **Key Topics**:
  - Entity-Attribute-Value (EAV) database architecture and why both `summary_element` and `summary_name` exist.
  - Station duplication analysis: Dual numeric WMO IDs vs. text names in Zimbabwe, duplicated station records in Zambia, and true physical station counts.
  - Seasonal rainfall coverage reality (which stations have seasonal total rainfall vs. full-year totals).
  - Full census of all 92 distinct rainfall naming permutations across 2.17M production rows.
  - Upstream standardization specification for the R-Instat development team.

### 2. [Database Variable Auditing & Drift Detection](AUDITING_AND_DRIFT_DETECTION.md)
- **Scope**: Operational manual for the automated auditing CLI tools (`audit_variables.py` and `audit_stations.py`).
- **Key Topics**:
  - Variable drift detection: Cross-referencing database pairs against canonical mapping models.
  - Station identity and duplication detection: Dual-identity stations (numeric WMO IDs vs. text names, codes vs. names), multi-batch accumulation, and country code validation.
  - How to run audits locally, via Docker, or in CI/CD pipelines.
  - Command-line flags (`--strict`, `--summary-type`, `--markdown`, `--json`).
  - Step-by-step resolution workflow when drift or station duplications are detected.

### 3. [Table Definitions & Select Query Examples](TABLE_DEFINITIONS_AND_SELECT_QUERY_EXAMPLES.md)
- **Scope**: Reference documentation for the analytical PostgreSQL tables and the `/v1/select_query/` & `/v2/select_query/` endpoints.
- **Key Topics**:
  - Whitelisted table schemas (`crop`, `definition`, `station`, `summary`, `summary_station_metadata`).
  - Column filtering and sorting parameters.
  - Request and response examples for direct analytical queries.
