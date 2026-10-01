# AGENTS.md — AI Developer & Agent Guide for E-PICSA Climate API

Welcome to the **E-PICSA Climate API** repository (`IDEMSInternational/epicsa-climate-api`).
This document provides AI coding agents and developers with an exhaustive operational and architectural guide to the codebase, design patterns, runtime constraints, folder structure, testing paradigms, and extension workflows.

---

## 1. System Overview & Technology Stack

The E-PICSA (Enhanced Participatory Integrated Climate Services for Agriculture) Climate API provides programmatic access to agricultural and historical climate statistics, station metadata, station definitions, downloadable documents, and structured queries against an analytical PostgreSQL database.

### Core Architectural Pillars
1. **Python API Layer**: Built on **FastAPI** running under **Uvicorn**, utilizing **Pydantic v1** (`<2.0.0`) for request/response validation and settings management.
2. **PostgreSQL Analytical Engine**: High-performance SQL queries against analytical climate tables via `app/services/climate_repository.py` and `app/core/database.py`.
3. **Database Query Engine**: A parameterized, whitelist-driven SQL engine using **`psycopg2`** connection pooling to execute read-only queries against PostgreSQL climate tables (`/v2/select_query/`).
4. **Cloud Storage**: Google Cloud Storage (`google-cloud-storage`) integration for document listing and streamed file delivery (e.g. PDF/HTML reports).
5. **Containerized Deployment**: Multi-stage Docker build running under Google Cloud Run with secret decoding and mounting handled via `entrypoint.sh`.

### Key Technologies & Versions
- **Python**: `3.13`
- **FastAPI**: `~0.100+`
- **Pydantic**: `>=1.8.0, <2.0.0` (**Strict v1!** See Gotchas section)
- **PostgreSQL Driver**: `psycopg2-binary`
- **Container Base**: `python:3.13-bookworm` (builder), `python:3.13-slim-bookworm` (prod)

---

## 2. Repository & Folder Layout

```
.
├── .env.sample                           # Sample environment configuration for local dev
├── .github/
│   └── workflows/
│       ├── cloud_deploy_buildx.yml       # GitHub Actions: buildx Docker build & Google Cloud Run deploy
│       └── tests.yml                     # GitHub Actions: CI test runner inside Docker Compose
├── Dockerfile                            # Multi-stage Docker build (clean Python builder -> prod slim)
├── docker-compose.yaml                   # Local orchestration with secret bindings & volume mounts
├── docker-compose.test.yaml              # Docker Compose override for CI (secret injection via env)
├── entrypoint.sh                         # Container startup script (decodes base64 secrets, symlinks keys)
├── db_schema.json                        # Auto-generated database schema metadata for AI agents and tooling
├── openapi.json                          # Exported OpenAPI 3.1 schema for agents and type generation
├── postgres-secret-example.json          # Template for PostgreSQL credentials
├── pytest.ini                            # Pytest configuration, env files, testpaths
├── requirements.txt                      # Production Python dependencies (includes pydantic v1 pin)
├── requirements_dev.txt                  # Pinned Python dependencies for reproducible dev setup
├── scripts/                              # Host CLI script wrappers (export_openapi, introspect_schema)
├── TABLE_DEFINITIONS_AND_SELECT_QUERY_EXAMPLES.md # Schema documentation for select_query endpoint
├── test.sh                               # Helper script running pytest with coverage
│
└── app/
    ├── __init__.py
    ├── main.py                           # FastAPI application entrypoint, CORS, GZip, shutdown handlers
    ├── test_main.py                      # Smoke tests for root docs endpoint and OpenAPI specs
    ├── conftest.py                       # Pytest module-scoped TestClient fixture
    ├── definitions.py                    # Shared literal types (country_code, language_code)
    │
    ├── schemas/                          # High-level Pydantic models for DB tables and shared schemas
    │   ├── __init__.py
    │   └── database.py                   # CropRecord, DefinitionRecord, StationRecord, SummaryRecord, etc.
    │
    ├── services/                         # Database repository services
    │   ├── __init__.py
    │   └── climate_repository.py         # Pure Python PostgreSQL repository for all climate statistics
    │
    ├── scripts/                          # Container-compatible maintenance and export scripts
    │   ├── __init__.py
    │   ├── export_openapi.py             # Dumps OpenAPI schema to openapi.json
    │   └── introspect_schema.py          # Introspects live DB into db_schema.json and verifies models
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py                     # Pydantic BaseSettings (POSTGRES_SECRET_FILE, etc.)
    │   ├── database.py                   # PostgreSQL connection pool and query executor
    │   └── responce_models/              # Pydantic response models (Note: historic typo 'responce')
    │       ├── crop_success_probabilities_model.py
    │       ├── definitions_responce_model.py
    │       ├── extremes_summaries_responce_model.py
    │       ├── rainfall_summaries_responce_model.py
    │       ├── season_start_probabilities.py
    │       ├── station_responce_model.py
    │       └── temperature_responce_model.py
    │
    ├── utils/
    │   ├── model.py                      # Literal validation helper `with_fallback`
    │   └── response.py                   # Dataframe JSON preparation (`get_dataframe_response`, NaN -> None)
    │
    ├── api/
    │   └── v2/
    │       ├── __init__.py
    │       ├── router.py                 # Central v2 router registering all endpoints under /v2
    │       └── endpoints/
    │           ├── annual_rainfall_summaries/
    │           ├── annual_temperature_summaries/
    │           ├── monthly_temperature_summaries/
    │           ├── crop_success_probabilities/
    │           ├── season_start_probabilities/
    │           ├── station/
    │           ├── documents/            # Google Cloud Storage bucket listing and file streaming
    │           ├── select_query/         # Parameterized PostgreSQL query runner & connection pool
    │           │   ├── router.py
    │           │   ├── schema.py
    │           │   └── test_router.py
    │           └── status/               # Health check endpoint (/v2/status/)
    │
    └── tests/                            # API integration & validation tests
        ├── data/                         # SQLite test fixtures for local testing
        │   └── test_epicsa.sql
        ├── results/                      # Reference JSON fixture files
        ├── test_v2_endpoints.py          # Comprehensive test suite for all v2 endpoints
        ├── test_get_documents.py         # Tests for GCS document retrieval
        └── test_get_status.py            # Health check tests
```

---

## 3. Architecture & Subsystems Deep Dive

### Subsystem A: The PostgreSQL Climate Repository (`app/services/climate_repository.py`)
All climate calculations and summaries query PostgreSQL directly in pure Python:
- `get_annual_rainfall_summaries`
- `get_annual_temperature_summaries`
- `get_monthly_temperature_summaries`
- `get_crop_success_probabilities`
- `get_season_start_probabilities`
- `get_station_list`
- `get_station_and_definition`
Results are validated directly against typed Pydantic models in `app/core/responce_models/`.

### Subsystem B: Parameterized Database Query Engine (`select_query`)
Located in `app/api/v2/endpoints/select_query/`.
- **Security Philosophy**: Disallows raw SQL input completely. Queries are strictly constructed from a white-listed configuration table `_TABLE_CONFIG`.
- **Supported Tables**:
  - `crop`
  - `definition` (joins `summary` internally on `definition_id` to enforce mandatory `station_id` filtering)
  - `station`
  - `summary`
  - `summary_station_metadata`
- **Features**:
  - Column whitelisting per table.
  - Orderable column whitelisting and direction (`asc` / `desc`).
  - Row limiting (1–1000, default 100).
  - Parameterized statement execution using `%s` placeholders.
  - Connection pooling via `psycopg2.pool.ThreadedConnectionPool` (1–10 connections).
  - Read-only transaction enforcement (`connection.set_session(readonly=True, autocommit=False)`).
  - Statement timeout enforced per query (`SET LOCAL statement_timeout = 5000` ms).
  - Explicit rollback and connection return in `finally` blocks.
  - Lifespan cleanup: `close_connection_pool()` hooked to FastAPI's `"shutdown"` event in `app/main.py`.

### Subsystem C: Document Retrieval (`documents`)
Located in `app/api/v2/endpoints/documents/`.
- Connects to Google Cloud Storage bucket `epicsa-documents` using `google.cloud.storage.Client.from_service_account_json('service-account.json')`.
- Enforces country isolation: all blob lookups are scoped by prefix `${country}/`.
- Streamed responses via FastAPI `StreamingResponse` with appropriate `media_type` (`application/html` or `application/pdf`).

### Subsystem D: Configuration Management
Defined in `app/core/config.py`:
- Inherits from `pydantic.BaseSettings`.
- `POSTGRES_SECRET_FILE`: Path to JSON file with DB credentials (`host`, `port`, `dbname`, `user`, `password`, `sslmode`). Defaults to `./postgres-secret.json`.
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins. A Pydantic validator parses comma-separated strings or JSON arrays.

### Subsystem E: Database Schemas, Introspection & OpenAPI Export
Located in `app/schemas/`, `app/scripts/`, `scripts/`, `openapi.json`, and `db_schema.json`.
- **Pydantic Database Models (`app/schemas/database.py`)**:
  - Defines typed models for PostgreSQL tables: `CropRecord`, `DefinitionRecord`, `StationRecord`, `SummaryRecord`, `SummaryStationMetadataRecord`.
  - Reusable across any endpoint or module (e.g. `select_query` or future dedicated table endpoints).
  - Automatically registered into OpenAPI `components.schemas` via `custom_openapi()` in `app/main.py`.
- **Database Introspection (`app/scripts/introspect_schema.py`)**:
  - Introspects live PostgreSQL database tables and columns using `psycopg2` and `postgres-secret.json`.
  - Dumps machine-readable schema metadata to `db_schema.json` for AI agents and local tools.
  - Verifies live database columns against Pydantic models via `--verify`.
- **OpenAPI Schema Export (`app/scripts/export_openapi.py`)**:
  - Exports the current FastAPI OpenAPI 3.1 specification to `openapi.json` at the repo root.
  - Used by AI agents for offline context and by client generators (e.g. TypeScript `openapi-typescript` + `openapi-fetch`).

---

## 4. API Endpoints Reference

All endpoints are registered under the `/v2` prefix.

| Method | Route | Tag | Request Model / Parameters | Response Model | Description |
|---|---|---|---|---|---|
| `GET` | `/v2/status/` | v2: Testing | None | `str` (`"Server Up (/v2)"`) | Health check |
| `POST` | `/v2/annual_rainfall_summaries/` | v2: Climate | `AnnualRainfallSummariesParameters` | `AnnualRainfallSummariesResponce` | Annual rainfall metrics (totals, start/end of rains, season length) |
| `POST` | `/v2/annual_temperature_summaries/` | v2: Climate | `AnnualTemperatureSummariesParameters` | `AnnualTemperatureSummariesResponce` | Annual temperature summaries (tmin/tmax means, mins, maxs) |
| `POST` | `/v2/monthly_temperature_summaries/` | v2: Climate | `MonthlyTemperatureSummariesParameters` | `MonthlyTemperatureSummariesResponce` | Monthly aggregated temperature summaries |
| `POST` | `/v2/crop_success_probabilities/` | v2: Climate | `CropSuccessProbabilitiesParameters` | `CropSuccessProbabilitiesResponce` | Crop success probabilities based on planting day & length |
| `POST` | `/v2/season_start_probabilities/` | v2: Climate | `SeasonStartProbabilitiesParameters` | `SeasonStartProbabilitiesResponce` | Probabilities of season starting by given day-of-year |
| `GET` | `/v2/station/{country}` | v2: Metadata | `country: country_code` | `StationListResponce` | List all stations for a country |
| `GET` | `/v2/station/{country}/{station_id}` | v2: Metadata | `country: country_code`, `station_id: str` | `StationAndDefintionResponce` | Station details & statistical definitions |
| `GET` | `/v2/documents/{country}` | v2: Documents | `country: country_code`, query params | `list[DocumentMetadata]` | List documents available in GCS for a country |
| `GET` | `/v2/documents/{country}/{filepath:path}` | v2: Documents | `country: country_code`, `filepath: str` | `StreamingResponse` | Stream PDF or HTML document from bucket |
| `POST` | `/v2/select_query/` | v2: Database | `SelectQueryRequest` | `SelectQueryResponse` | Whitelisted parameterized query on PostgreSQL tables |

### Supported Country Codes (`app/definitions.py`)
`'zm'` (Zambia), `'mw'` (Malawi), `'zw'` (Zimbabwe), `'zm_test'`, `'mw_test'`, `'zw_test'`, `'zm_workshops'`, `'mw_workshops'`, `'zw_workshops'`, `'internal_tests'`.

---

## 5. Critical Architectural Rules & Agent "Gotchas"

### ⚠️ Gotcha 1: Strict Pydantic v1 Requirement
The project pins `pydantic>=1.8.0,<2.0.0`.
- **DO NOT** use Pydantic v2 methods: `model_dump()`, `model_validate()`, `model_validate_json()`, `field_validator`.
- **USE** Pydantic v1 methods: `.dict()`, `.parse_obj()`, `BaseSettings`, `@validator`.
- Models inherit from `pydantic.BaseModel`.

### ⚠️ Gotcha 2: Historical Typo Retention (`responce_models`)
The response models directory is spelled `app/core/responce_models/` (with a `c`).
The class names inside use `Responce`:
- `AnnualRainfallSummariesResponce`
- `AnnualTemperatureSummariesResponce`
- `MonthlyTemperatureSummariesResponce`
- `CropSuccessProbabilitiesResponce`
- `SeasonStartProbabilitiesResponce`
- `StationListResponce`
- `StationAndDefintionResponce`
- In temperature models: `AnnualTempartureSummariesdata` (missing 'e' in temperature).
**DO NOT** unilaterally rename these classes or the directory. All routers, imports, and tests rely on these exact symbol names.

### ⚠️ Gotcha 3: GCS Client Module-Level Initialization
`app/api/v2/endpoints/documents/router.py` initializes:
```python
client = storage.Client.from_service_account_json('service-account.json')
```
with fallback handling if `service-account.json` is missing.

### ⚠️ Gotcha 4: Git Workflow Rules
Per project rules:
- **NEVER** run `git add`, `git commit`, or `git push` via shell tools.
- The user handles all staging, commits, and branch management manually.

### ⚠️ Gotcha 5: Always Bump Version on Code Changes
Whenever proposing code changes, always bump the API version string in `app/main.py`:
```python
_app = FastAPI(title="E-PICSA Climate API", version="x.y.z", docs_url="/")
```

---

## 6. Local Setup & Execution Commands

### Prerequisites
- Python 3.13
- Service account file: `service-account.json` in project root
- PostgreSQL secrets: `postgres-secret.json` in project root

### Environment Configuration
```bash
cp .env.sample .env
cp postgres-secret-example.json postgres-secret.json
```

### Local Python Setup
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
```

### Running the Server Locally
```bash
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be accessible at: `http://localhost:8000/`

### Running with Docker Compose
```bash
# Build and run container
docker compose up --build

# Run tests in Docker container
docker compose -f docker-compose.yaml -f docker-compose.test.yaml run app pytest -v
```

### Running Tests Locally
```bash
pytest
# Or with coverage
./test.sh
```
