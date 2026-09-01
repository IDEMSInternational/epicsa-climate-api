# Table Definitions and select_query JSON Examples

This document lists the current table definitions and provides a pasteable JSON payload example for the `select_query` endpoint for each table.

Constraints used in all examples:
- Uses `"station_id": "dodoma"`.
- Uses `"max_rows": 100`.
- Uses `order_by` as `time_value` or `time_stamp` where possible.
- Uses only allowlisted table and column names.

## crop

| Column | Type |
|---|---|
| station_id | character varying(255) |
| year | character varying(255) |
| plant_day | numeric |
| plant_length | numeric |
| rain_total | numeric |
| include_start_condition | boolean |
| summary_type | character varying(255) |
| summary_element | character varying(255) |
| summary_value | character varying(255) |
| definition_id | character varying(255) |
| status | character varying(10) |
| time_stamp | timestamp with time zone |

### Endpoint JSON example

```json
{
  "table_name": "crop",
  "columns": [
    "station_id",
    "year",
    "plant_day",
    "plant_length",
    "rain_total",
    "summary_type",
    "summary_element",
    "summary_value",
    "status",
    "time_stamp"
  ],
  "station_id": "dodoma",
  "order_by": "time_stamp",
  "order_direction": "desc",
  "max_rows": 100
}
```

## definition

| Column | Type |
|---|---|
| definition_id | character varying(255) |
| time_stamp | timestamp with time zone |
| summary_element | character varying(255) |
| summary_type | character varying(255) |
| definition_value | jsonb |
| accreditation | character varying(255) |

### Endpoint JSON example

Note: `definition` does not contain `station_id`, so the endpoint applies a predefined join through `summary` internally.

```json
{
  "table_name": "definition",
  "columns": [
    "definition_id",
    "time_stamp",
    "summary_element",
    "summary_type",
    "definition_value",
    "accreditation"
  ],
  "station_id": "dodoma",
  "order_by": "time_value",
  "order_direction": "desc",
  "max_rows": 100
}
```

## station

| Column | Type |
|---|---|
| station_id | character varying(255) |
| station_name | character varying(255) |
| latitude | numeric |
| longitude | numeric |
| elevation | numeric |
| district | character varying(255) |
| country_code | character varying(10) |
| time_stamp | timestamp with time zone |
| status | character varying(10) |

### Endpoint JSON example

```json
{
  "table_name": "station",
  "columns": [
    "station_id",
    "station_name",
    "latitude",
    "longitude",
    "elevation",
    "district",
    "country_code",
    "status",
    "time_stamp"
  ],
  "station_id": "dodoma",
  "order_by": "time_stamp",
  "order_direction": "desc",
  "max_rows": 100
}
```

## summary

| Column | Type |
|---|---|
| station_id | character varying(255) |
| definition_id | character varying(255) |
| time_type | character varying(255) |
| time_value | character varying(255) |
| summary_type | character varying(255) |
| summary_element | character varying(255) |
| summary_name | character varying(255) |
| summary_value | character varying(255) |
| time_stamp | timestamp with time zone |
| status | character varying(10) |

### Endpoint JSON example

```json
{
  "table_name": "summary",
  "columns": [
    "station_id",
    "definition_id",
    "time_type",
    "time_value",
    "summary_type",
    "summary_element",
    "summary_name",
    "summary_value",
    "status",
    "time_stamp"
  ],
  "station_id": "dodoma",
  "order_by": "time_value",
  "order_direction": "desc",
  "max_rows": 100
}
```

## summary_station_metadata

| Column | Type |
|---|---|
| station_id | character varying(255) |
| summary_type | character varying(255) |
| definition_id | character varying(255) |
| time_stamp | timestamp with time zone |

### Endpoint JSON example

```json
{
  "table_name": "summary_station_metadata",
  "columns": [
    "station_id",
    "summary_type",
    "definition_id",
    "time_stamp"
  ],
  "station_id": "dodoma",
  "order_by": "time_stamp",
  "order_direction": "desc",
  "max_rows": 100
}
```
