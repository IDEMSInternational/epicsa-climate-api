# E-PICSA Climate Api

API for accessing E-PICSA climate services

Build with [FastAPI](https://fastapi.tiangolo.com/)

## Pre-Requisites

The api requires Python 3.13.

- Python (3.13)  
  [https://www.python.org/downloads](https://www.python.org/downloads)

## Configuration

**Environment**

Create an environment file from the sample. These will be populated using [Pydantic](https://docs.pydantic.dev/usage/settings/)

```
cp .env.sample .env
```

**Python**

The scripts below will create a python [virtual environment](https://docs.python.org/3/library/venv.html), activate, install required python dependencies and start local server

=== "Windows (powershell)"

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install --upgrade -r requirements.txt
    uvicorn app.main:app --reload

=== "Linux (bash)"

    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade -r requirements.txt
    uvicorn app.main:app --reload

**Authorization File**

In order to run the package, you will need to add the following service account file to the main repository folder (i.e. the folder where this `README.md` file is stored):

```
service-account.json
```

**Postgres Secret File**

The select query endpoint reads database credentials from a separate JSON secret file.

Copy the example file and then update the placeholder values:

Windows (powershell)

```powershell
Copy-Item postgres-secret-example.json postgres-secret.json
```

Linux / Mac (bash)

```bash
cp postgres-secret-example.json postgres-secret.json
```

The file location is controlled by `POSTGRES_SECRET_FILE` (defaults to `./postgres-secret.json` when running locally; the container entrypoint defaults it to `/tmp/postgres-secret.json`).

**Select Query Endpoint**

The `/v2/select_query/` endpoint queries data from allowed tables using a structured request body. It is **not** a generic SQL endpoint — it builds parameterized queries from a whitelist of tables and columns.

Request schema:

| Field | Type | Required | Description |
|---|---|---|---|
| `table_name` | string | Yes | One of: `crop`, `definition`, `station`, `summary`, `summary_station_metadata` |
| `station_id` | string | Yes | Station identifier to filter results by |
| `columns` | list[string] | No | Columns to return. Omit to return all available columns for the table. |
| `order_by` | string | No | Column to sort by. Must be an orderable column for the selected table. |
| `order_direction` | `"asc"` or `"desc"` | No | Sort direction. Defaults to `"desc"`. |
| `max_rows` | integer | No | Maximum rows to return (1–1000). Defaults to 100. |

Example request body for the `crop` table:

```json
{
  "table_name": "crop",
  "station_id": "dodoma",
  "columns": ["station_id", "year", "plant_day", "plant_length", "rain_total", "summary_type", "summary_element", "summary_value", "status", "time_stamp"],
  "order_by": "time_stamp",
  "order_direction": "desc",
  "max_rows": 100
}
```

Example request body for the `station` table:

```json
{
  "table_name": "station",
  "station_id": "dodoma",
  "max_rows": 100
}
```

## Running locally

Once installed, subsequent server starts can skip installation steps

=== "Windows (powershell)"

    .\.venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload

=== "Linux (bash)"

    source .venv/bin/activate
    uvicorn app.main:app --reload

The server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Running Tests

```py
pytest
```

## Running locally (docker)

### Initial Run / Dependency Updates
Build the container image and start the service:

```sh
docker compose up --build
```

### Day-to-Day Development
For subsequent runs, simply start the container:

```sh
docker compose up
```

- **Live Hot-Reloading**: The `./app` directory is bind-mounted directly into the container and Uvicorn runs with `--reload`. Any changes made to Python files in `./app/` take effect immediately without needing to restart the container or rebuild the image.
- **When is `--build` needed?**: You only need to run `docker compose up --build` if you change dependencies (`requirements.txt`) or container configurations (`Dockerfile`, `entrypoint.sh`).


## Database Schema & OpenAPI Tooling

This repository provides built-in CLI scripts for database schema introspection, Pydantic model verification, and OpenAPI specification export.

### 1. Export OpenAPI Schema (`openapi.json`)
Exports the complete OpenAPI 3.1 specification (including database record schemas) to disk for AI agents or client SDK generators:

```bash
# Via Docker (recommended):
docker compose exec app python -m app.scripts.export_openapi --stdout > openapi.json

# Local Python environment:
python -m app.scripts.export_openapi
# or
python scripts/export_openapi.py
```

### 2. Introspect Database Schema (`db_schema.json`)
Connects to PostgreSQL using `postgres-secret.json` and dumps complete table metadata, column data types, nullability, defaults, and keys to a machine-readable JSON file:

```bash
# Via Docker (recommended):
docker compose exec app python -m app.scripts.introspect_schema --stdout > db_schema.json

# Local Python environment:
python -m app.scripts.introspect_schema
# or
python scripts/introspect_schema.py
```

### 3. Verify Database Schema against Pydantic Models
Checks for schema drift between the live PostgreSQL database and the models defined in `app/schemas/database.py`:

```bash
# Via Docker (recommended):
docker compose exec app python -m app.scripts.introspect_schema --verify

# Local Python environment:
python -m app.scripts.introspect_schema --verify
```

### 4. Generate Markdown Schema Documentation
Outputs formatted Markdown tables describing tables and columns:

```bash
# Via Docker:
docker compose exec app python -m app.scripts.introspect_schema --format markdown

# Local Python environment:
python -m app.scripts.introspect_schema --format markdown
```

### 5. Generate TypeScript Types (for `openapi-fetch`)
To generate fully typed TypeScript definitions for frontend/client consumption from `openapi.json`:

```bash
npx openapi-typescript openapi.json -o api-types.ts
```


## Deployment

This repo contains example workflow to build as a docker image and deploy to google cloud run. See action yaml for details

For cloud deploy, store the contents of `postgres-secret.json` as a base64 encoded GitHub secret named `POSTGRES_SECRET_JSON_B64`.

## Troubleshooting

**Pip won't install dependencies**
Depending on local versions of python (as well as operating system) there may be issues when installing certain packages. Recommend attempting install using the `requirements_dev.txt` file which pins exact versions of packages shown to be compatible with each other, i.e.

```sh
pip install --upgrade -r requirements_dev.txt
```

Any issues should be raised on GitHub

## License

This project is licensed under the terms of the MIT license.
