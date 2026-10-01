# AGENTS.md — AI Developer & Agent Guide for E-PICSA Climate API

Welcome to the **E-PICSA Climate API** repository (`IDEMSInternational/epicsa-climate-api`).
This document provides AI coding agents and developers with an exhaustive operational and architectural guide to the codebase, design patterns, runtime constraints, folder structure, testing paradigms, and extension workflows.

---

## 1. System Overview & Technology Stack

The E-PICSA (Enhanced Participatory Integrated Climate Services for Agriculture) Climate API provides programmatic access to agricultural and historical climate statistics, station metadata, station definitions, downloadable documents, and structured queries against an analytical PostgreSQL database.

### Core Architectural Pillars
1. **Python API Layer**: Built on **FastAPI** running under **Uvicorn**, utilizing **Pydantic v1** (`<2.0.0`) for request/response validation and settings management.
2. **R Computation Engine**: Integrates with the custom R package [`IDEMSInternational/epicsawrap`](https://github.com/IDEMSInternational/epicsawrap) (and `terra`, `rlang`) via **`rpy2`** to perform domain-specific statistical climate computations.
3. **Database Query Engine**: A parameterized, whitelist-driven SQL engine using **`psycopg2`** connection pooling to execute read-only queries against PostgreSQL climate tables.
4. **Cloud Storage**: Google Cloud Storage (`google-cloud-storage`) integration for document listing and streamed file delivery (e.g. PDF/HTML reports).
5. **Containerized Deployment**: Multi-stage Docker build running under Google Cloud Run with secret decoding and mounting handled via `entrypoint.sh`.

### Key Technologies & Versions
- **Python**: `3.13`
- **R Runtime**: `4.4.3` (`r-base`, `r-base-dev`)
- **FastAPI**: `~0.100+`
- **Pydantic**: `>=1.8.0, <2.0.0` (**Strict v1!** See Gotchas section)
- **rpy2**: `==3.5.12` (Pinned specifically to prevent Windows C-extension issues)
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
├── Dockerfile                            # Multi-stage Docker build (builder with R-dev -> prod slim)
├── docker-compose.yaml                   # Local orchestration with secret bindings & volume mounts
├── docker-compose.test.yaml              # Docker Compose override for CI (secret injection via env)
├── entrypoint.sh                         # Container startup script (decodes base64 secrets, symlinks keys)
├── install_packages.R                    # Installs CRAN packages (rlang)
├── install_packages_picsa.R              # Installs pak, pins terra, installs epicsawrap from GitHub
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
    ├── test_main.py                      # Smoke tests for root docs endpoint
    ├── conftest.py                       # Pytest module-scoped TestClient fixture
    ├── definitions.py                    # Shared literal types (country_code, language_code)
    ├── epicsawrap_link.py                # Python wrapper invoking R functions via rpy2
    │
    ├── schemas/                          # High-level Pydantic models for DB tables and shared schemas
    │   ├── __init__.py
    │   └── database.py                   # CropRecord, DefinitionRecord, StationRecord, SummaryRecord, etc.
    │
    ├── scripts/                          # Container-compatible maintenance and export scripts
    │   ├── __init__.py
    │   ├── export_openapi.py             # Dumps OpenAPI schema to openapi.json
    │   └── introspect_schema.py          # Introspects live DB into db_schema.json and verifies models
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py                     # Pydantic BaseSettings (EPICSA_DATA_AUTH_TOKEN, POSTGRES_SECRET_FILE, etc.)
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
    │   └── v1/
    │       ├── __init__.py
    │       ├── router.py                 # Central v1 router registering all endpoints under /v1
    │       └── endpoints/
    │           ├── epicsa_data.py        # Central execution wrapper for R: _r_lock, error logging, dependency injection
    │           ├── annual_rainfall_summaries/
    │           │   ├── router.py
    │           │   └── schema.py
    │           ├── annual_temperature_summaries/
    │           │   ├── router.py
    │           │   └── schema.py
    │           ├── monthly_temperature_summaries/
    │           │   ├── router.py
    │           │   └── schema.py
    │           ├── crop_success_probabilities/
    │           │   ├── router.py
    │           │   └── schema.py
    │           ├── season_start_probabilities/
    │           │   ├── router.py
    │           │   └── schema.py
    │           ├── extremes_summaries/
    │           │   ├── router.py
    │           │   └── schema.py
    │           ├── station/
    │           │   └── router.py
    │           ├── documents/
    │           │   ├── router.py         # Google Cloud Storage bucket listing and file streaming
    │           │   └── schema.py
    │           ├── select_query/
    │           │   ├── router.py         # Parameterized PostgreSQL query runner & connection pool
    │           │   ├── schema.py
    │           │   └── test_router.py    # Unit tests for select_query logic and validation
    │           └── status/
    │               └── router.py         # Health check endpoint (/v1/status/)
    │
    └── tests/                            # API integration & validation tests
        ├── results/                      # Reference JSON fixture files
        ├── test_all_stations.py          # Station integration test suite across countries
        ├── test_error_response.py        # Validates response model validation failure handling (HTTP 500)
        ├── test_get_documents.py         # Tests for GCS document retrieval
        └── test_get_status.py            # Health check tests
```

---

## 3. Architecture & Subsystems Deep Dive

### Subsystem A: The Python-to-R Bridge (`epicsawrap` via `rpy2`)
R is fundamentally single-threaded and not thread-safe. Multiple simultaneous requests entering R will crash or corrupt process memory.
- **The Global Lock**: In `app/api/v1/endpoints/epicsa_data.py`, a module-level lock `_r_lock = threading.Lock()` guarantees that **only one thread** executes R code at any instant.
- **Error Interception**: `epicsa_data.py` redirects `rpy2` log output into an in-memory `StringIO` buffer (`rpy2_logger.addHandler(stream_handler)`), appending R error diagnostics to Python exceptions if execution fails.
- **Data Conversion & Sanitization**:
  - `app/epicsawrap_link.py` translates Python types into R types (`StrVector`, `FloatVector`, `r_NULL`).
  - Results from R (`ListVector`, `RDataFrame`) are recursively converted back to Python dicts, lists, and `pandas.DataFrame`s.
  - Missing integers in `rpy2` default to signed 32-bit minimum (`-2147483648`), which are replaced with `None`.
  - Categorical DataFrame columns are cast to `str`.
  - `NaN` values are converted to `None` via `app/utils/response.py:get_dataframe_response()` to ensure strict JSON compatibility.
- **Initialization**: `__init_data_env()` in `app/epicsawrap_link.py` runs once per session to pass `service-account.json` to R's `r_epicsawrap.gcs_auth_file()` and sets up local working directory storage `working_data/`.

### Subsystem B: Parameterized Database Query Engine (`select_query`)
Located in `app/api/v1/endpoints/select_query/`.
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
Located in `app/api/v1/endpoints/documents/`.
- Connects to Google Cloud Storage bucket `epicsa-documents` using `google.cloud.storage.Client.from_service_account_json('service-account.json')`.
- Enforces country isolation: all blob lookups are scoped by prefix `${country}/`.
- Streamed responses via FastAPI `StreamingResponse` with appropriate `media_type` (`application/html` or `application/pdf`).

### Subsystem D: Configuration Management
Defined in `app/core/config.py`:
- Inherits from `pydantic.BaseSettings`.
- `EPICSA_DATA_AUTH_TOKEN`: String auth token (legacy).
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

All endpoints are registered under the `/v1` prefix.

| Method | Route | Tag | Request Model / Parameters | Response Model | Description |
|---|---|---|---|---|---|
| `GET` | `/v1/status/` | Testing | None | `str` (`"Server Up"`) | Health check |
| `POST` | `/v1/annual_rainfall_summaries/` | Climate | `AnnualRainfallSummariesParameters` | `AnnualRainfallSummariesResponce` | Annual rainfall metrics (totals, start/end of rains, season length) |
| `POST` | `/v1/annual_temperature_summaries/` | Climate | `AnnualTemperatureSummariesParameters` | `AnnualTemperatureSummariesResponce` | Annual temperature summaries (tmin/tmax means, mins, maxs) |
| `POST` | `/v1/monthly_temperature_summaries/` | Climate | `MonthlyTemperatureSummariesParameters` | `MonthlyTemperatureSummariesResponce` | Monthly aggregated temperature summaries |
| `POST` | `/v1/crop_success_probabilities/` | Climate | `CropSuccessProbabilitiesParameters` | `CropSuccessProbabilitiesResponce` | Crop success probabilities based on planting day & length |
| `POST` | `/v1/season_start_probabilities/` | Climate | `SeasonStartProbabilitiesParameters` | `SeasonStartProbabilitiesResponce` | Probabilities of season starting by given day-of-year |
| `POST` | `/v1/extremes_summaries/` | Climate | `ExtremesSummariesParameters` | `OrderedDict` (raw JSON) | Extremes rainfall & temperature summaries (work in progress) |
| `GET` | `/v1/station/{country}` | Metadata | `country: country_code` | `StationListResponce` | List all stations for a country |
| `GET` | `/v1/station/{country}/{station_id}` | Metadata | `country: country_code`, `station_id: str` | `StationAndDefintionResponce` | Station details & statistical definitions |
| `GET` | `/v1/documents/{country}` | Documents | `country: country_code`, query params | `list[DocumentMetadata]` | List documents available in GCS for a country |
| `GET` | `/v1/documents/{country}/{filepath:path}` | Documents | `country: country_code`, `filepath: str` | `StreamingResponse` | Stream PDF or HTML document from bucket |
| `POST` | `/v1/select_query/` | Database | `SelectQueryRequest` | `SelectQueryResponse` | Whitelisted parameterized query on PostgreSQL tables |

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

### ⚠️ Gotcha 3: Single-Threaded R Concurrency (`_r_lock`)
Never invoke functions in `app/epicsawrap_link.py` directly from an endpoint without wrapping them in `handle_epicsa_request` or `run_epicsa_function_and_get_dataframe` from `app/api/v1/endpoints/epicsa_data.py`. Doing so bypasses `_r_lock` and can crash the process in a multi-threaded server.

### ⚠️ Gotcha 4: R Missing Values & Null Strings
- R representations of null strings can arrive via `rpy2` as empty objects or `"NA_character_"`.
- In `app/core/responce_models/rainfall_summaries_responce_model.py`, date fields use `Optional[str] | object` to prevent validation failures on R null strings.
- In `station_responce_model.py`, custom validators check `_is_missing()` to normalize `"NA_character_"` and empty dicts to `None`. Always replicate this pattern when parsing raw R data structures.

### ⚠️ Gotcha 5: Extremes Summaries Status
`extremes_summaries` is partially implemented:
- In `app/core/responce_models/extremes_summaries_responce_model.py`, imports for `ExtremesRain` and `ExtremesTemp` do not exist in `definitions_responce_model.py`.
- Because of this, `app/api/v1/endpoints/extremes_summaries/router.py` does not apply `response_model=ExtremesSummariesResponce` and returns raw `OrderedDict`.
- In `app/tests/test_all_stations.py`, `assert_extremes_summaries` is bypassed. Be mindful when modifying this endpoint.

### ⚠️ Gotcha 6: GCS Client Module-Level Initialization
`app/api/v1/endpoints/documents/router.py` initializes:
```python
client = storage.Client.from_service_account_json('service-account.json')
```
at the module level. If running in an environment without `service-account.json`, importing this module will raise an exception unless patched or a dummy file exists.

### ⚠️ Gotcha 7: Git Workflow Rules
Per project rules:
- **NEVER** run `git add`, `git commit`, or `git push` via shell tools.
- The user handles all staging, commits, and branch management manually.

### ⚠️ Gotcha 8: Always Bump Version on Code Changes
Whenever proposing code changes, always bump the API version string in `app/main.py`:
```python
_app = FastAPI(title="E-PICSA Climate API", version="x.y.z", docs_url="/")
```

---

## 6. Dependency Injection & Testing Patterns

### Dependency Override Pattern for R Endpoints
All climate endpoints accept the runner function as a FastAPI dependency:
```python
run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
```
This enables unit testing **without requiring R, R packages, or GCS credentials installed**.

In `app/tests/test_error_response.py`:
```python
from app.api.v1.endpoints.epicsa_data import get_run_epicsa_function

def mock_run_epicsa_function_and_get_dataframe(endpoint_function, has_dataframe=True, **kwargs):
    return OrderedDict({'metadata': OrderedDict({'wrongfield': 'wrongvalue'}),
                        'data': [{'nodata': 'empty'}]})

def get_mock_run_epicsa_function():
    return mock_run_epicsa_function_and_get_dataframe

app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
# Make requests...
app.dependency_overrides = {}
```

### Mocking Pattern for Database (`select_query`) Tests
In `app/api/v1/endpoints/select_query/test_router.py`:
```python
from app.api.v1.endpoints.select_query import router as select_router

def test_select_query_success(monkeypatch):
    monkeypatch.setattr(select_router, "_load_db_secret", lambda _: {
        "host": "localhost", "port": 5432, "dbname": "example", "user": "example", "password": "example"
    })
    monkeypatch.setattr(select_router, "execute_select_query",
        lambda sql, params, secret: (["station_id"], [{"station_id": "dodoma"}])
    )
    # Test router response...
```

---

## 7. How-To Recipes for Common Agent Tasks

### Recipe 1: Adding a New Climate Summary Endpoint
1. **Define Schema**: Create `schema.py` in `app/api/v1/endpoints/<feature>/` specifying input parameters inheriting from `BaseModel`.
2. **Define Response Model**: Add metadata and data schemas in `app/core/responce_models/<feature>_responce_model.py`.
3. **Add R Wrapper**: In `app/epicsawrap_link.py`, declare the Python wrapper function converting input params with `__get_r_params()`, calling the R function via `r_epicsawrap.<function_name>`, and converting with `__get_list_vector_as_ordered_dict()`.
4. **Create Router**: Implement `router.py` using `handle_epicsa_request()`:
   ```python
   @router.post("/", response_model=MyFeatureResponce)
   def get_my_feature(
       params: MyFeatureParameters,
       run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
   ) -> MyFeatureResponce:
       return handle_epicsa_request(
           epicsa_function=my_feature_function,
           response_model=MyFeatureResponce,
           run_epicsa_function=run_epicsa_function,
           country=params.country,
           station_id=params.station_id,
           override=params.override,
       )
   ```
5. **Register Router**: Include in `app/api/v1/router.py`.
6. **Add Tests**: Add test cases to `app/tests/test_error_response.py` overriding `get_run_epicsa_function`.

### Recipe 2: Adding a Table or Column to `select_query`
1. Review [`TABLE_DEFINITIONS_AND_SELECT_QUERY_EXAMPLES.md`](TABLE_DEFINITIONS_AND_SELECT_QUERY_EXAMPLES.md).
2. In `app/api/v1/endpoints/select_query/router.py`:
   - Add/update the table entry in `_TABLE_CONFIG`.
   - Specify `"from"`, `"station_filter"`, allowed `"columns"` mapping, `"orderable"` columns, and `"default_order"`.
3. In `app/api/v1/endpoints/select_query/schema.py`:
   - If adding a new table, add the table name string to `SelectQueryRequest.table_name`'s `Literal[...]`.
4. In `app/api/v1/endpoints/select_query/test_router.py`:
   - Add unit test coverage verifying column filtering, ordering, and validation errors.

### Recipe 3: Introspecting Database Schema & Exporting OpenAPI
1. **Introspect & update `db_schema.json`**:
   - Host: `python -m app.scripts.introspect_schema`
   - Docker: `docker compose exec app python -m app.scripts.introspect_schema --stdout > db_schema.json`
2. **Verify live database columns against Pydantic models**:
   - Docker: `docker compose exec app python -m app.scripts.introspect_schema --verify`
3. **Export OpenAPI specification (`openapi.json`)**:
   - Host: `python -m app.scripts.export_openapi`
   - Docker: `docker compose exec app python -m app.scripts.export_openapi --stdout > openapi.json`

---

## 8. Local Setup & Execution Commands

### Prerequisites
- Python 3.13
- R 4.4.3 (with `Rtools` on Windows)
- Service account file: `service-account.json` in project root
- PostgreSQL secrets: `postgres-secret.json` in project root

### Environment Configuration
```bash
cp .env.sample .env
cp postgres-secret-example.json postgres-secret.json
```

### Local Python & R Setup
```bash
# Python
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt

# R Dependencies
Rscript install_packages.R
Rscript install_packages_picsa.R
```

### Running the Server Locally
```bash
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be accessible at: `http://localhost:8000/`

### Running with Docker Compose
```bash
# Initial run or after updating dependencies/Dockerfile (builds image)
docker compose up --build

# Day-to-day development (uses mounted ./app with Uvicorn --reload)
docker compose up

# Run tests in Docker container (recommended if local R is not installed)
docker compose -f docker-compose.yaml -f docker-compose.test.yaml run app pytest -v
```
*Note: `./app` is live-mounted into `/app/app` and Uvicorn runs with `--reload` in `docker-compose.yaml`. Python edits take effect immediately without rebuilding.*


### Running Tests Locally
```bash
pytest
# Or with coverage
./test.sh
```

### Schema Management & OpenAPI Export Commands
```bash
# Export OpenAPI specification to openapi.json
docker compose exec app python -m app.scripts.export_openapi --stdout > openapi.json
# (Local alternative: python -m app.scripts.export_openapi)

# Introspect PostgreSQL database into db_schema.json
docker compose exec app python -m app.scripts.introspect_schema --stdout > db_schema.json
# (Local alternative: python -m app.scripts.introspect_schema)

# Verify live DB schema against Pydantic models in app/schemas/database.py
docker compose exec app python -m app.scripts.introspect_schema --verify

# Generate TypeScript types for frontend / client applications
npx openapi-typescript openapi.json -o api-types.ts
```

---

## 9. Deployment & CI/CD Context

- **Continuous Integration (`.github/workflows/tests.yml`)**:
  - Triggers on push and pull request.
  - Builds Docker image using buildx.
  - Injects `SERVICE_ACCOUNT_JSON` and `POSTGRES_SECRET_JSON` secrets.
  - Runs `pytest -v` via `docker-compose.yaml` + `docker-compose.test.yaml`.
- **Cloud Run Deployment (`.github/workflows/cloud_deploy_buildx.yml`)**:
  - Builds and tags image to Google Artifact Registry.
  - Deploys container image to Google Cloud Run.
  - Secrets mounted:
    - `/run/secrets/service_account_key` (mounted from GCP secret).
    - `POSTGRES_SECRET_JSON_B64` (base64 decoded by `entrypoint.sh` into `/tmp/postgres-secret.json`).
- **Entrypoint Logic (`entrypoint.sh`)**:
  - Symlinks `/run/secrets/service_account_key` to `/app/service-account.json`.
  - Automatically decodes `POSTGRES_SECRET_JSON_B64` or writes `POSTGRES_SECRET_JSON` to `$POSTGRES_SECRET_FILE`.
