#!/usr/bin/env python3
"""
Introspect PostgreSQL database schema and export metadata / verify against Pydantic models.

Usage:
    # Export db_schema.json:
    python -m app.scripts.introspect_schema --output db_schema.json

    # Verify Pydantic models against the live database:
    python -m app.scripts.introspect_schema --verify

    # Print markdown table documentation:
    python -m app.scripts.introspect_schema --format markdown

    # Export both db_schema.json and openapi.json:
    python -m app.scripts.introspect_schema --export-all
"""

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

from app.schemas.database import DATABASE_TABLE_MODELS


def find_secret_file(custom_path: Optional[str] = None) -> Path:
    candidates = [
        custom_path,
        os.environ.get("POSTGRES_SECRET_FILE"),
        "/run/secrets/postgres_secret",
        "./postgres-secret.json",
        "../postgres-secret.json",
    ]
    for candidate in candidates:
        if candidate:
            p = Path(candidate).resolve()
            if p.is_file():
                return p
    raise FileNotFoundError(
        "Could not find postgres-secret.json. Specify with --secret-file or POSTGRES_SECRET_FILE."
    )


def load_secret(secret_path: Path) -> Dict[str, Any]:
    return json.loads(secret_path.read_text(encoding="utf-8"))


def get_db_connection(secret: Dict[str, Any]):
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed. Please run inside the container or install psycopg2-binary.")
    return psycopg2.connect(
        host=secret["host"],
        port=secret.get("port", 5432),
        dbname=secret["dbname"],
        user=secret["user"],
        password=secret["password"],
        sslmode=secret.get("sslmode", "prefer"),
        connect_timeout=10,
    )


def introspect_schema(secret: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection(secret)
    schema_data: Dict[str, Any] = {
        "tables": {},
    }

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Get all public tables
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row["table_name"] for row in cur.fetchall()]

            # 2. Get primary keys
            cur.execute("""
                SELECT
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                  AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.ordinal_position;
            """)
            pk_map: Dict[str, List[str]] = {}
            for row in cur.fetchall():
                pk_map.setdefault(row["table_name"], []).append(row["column_name"])

            # 3. Get columns for each table
            for table_name in tables:
                cur.execute("""
                    SELECT
                        column_name,
                        ordinal_position,
                        column_default,
                        is_nullable,
                        data_type,
                        udt_name,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = %s
                    ORDER BY ordinal_position;
                """, [table_name])
                columns = cur.fetchall()

                schema_data["tables"][table_name] = {
                    "primary_key": pk_map.get(table_name, []),
                    "columns": [
                        {
                            "name": col["column_name"],
                            "position": col["ordinal_position"],
                            "data_type": col["data_type"],
                            "udt_name": col["udt_name"],
                            "nullable": col["is_nullable"] == "YES",
                            "default": col["column_default"],
                            "char_max_length": col["character_maximum_length"],
                            "numeric_precision": col["numeric_precision"],
                            "numeric_scale": col["numeric_scale"],
                        }
                        for col in columns
                    ],
                }
    finally:
        conn.close()

    return schema_data


def verify_against_models(schema_data: Dict[str, Any]) -> bool:
    all_ok = True
    print("\n=== Verifying Database Schema vs. Pydantic Models ===")
    for table_name, model_class in DATABASE_TABLE_MODELS.items():
        if table_name not in schema_data["tables"]:
            print(f"❌ Table '{table_name}' in Pydantic models does NOT exist in the database!")
            all_ok = False
            continue

        db_cols = {c["name"]: c for c in schema_data["tables"][table_name]["columns"]}
        model_fields = model_class.__fields__

        missing_in_model = set(db_cols.keys()) - set(model_fields.keys())
        extra_in_model = set(model_fields.keys()) - set(db_cols.keys())

        if missing_in_model:
            print(f"⚠️  Table '{table_name}': columns in DB missing in {model_class.__name__}: {sorted(missing_in_model)}")
            all_ok = False
        if extra_in_model:
            print(f"⚠️  Table '{table_name}': fields in {model_class.__name__} not in DB: {sorted(extra_in_model)}")
            all_ok = False

        if not missing_in_model and not extra_in_model:
            print(f"✅ Table '{table_name}' matches {model_class.__name__} ({len(model_fields)} columns)")

    # Check for any tables in DB not defined in models
    unmapped_tables = set(schema_data["tables"].keys()) - set(DATABASE_TABLE_MODELS.keys())
    if unmapped_tables:
        print(f"ℹ️  Tables in DB without Pydantic models: {sorted(unmapped_tables)}")

    return all_ok


def format_markdown(schema_data: Dict[str, Any]) -> str:
    lines = ["# PostgreSQL Database Schema\n"]
    for table_name, info in schema_data["tables"].items():
        lines.append(f"## `{table_name}`\n")
        if info["primary_key"]:
            lines.append(f"**Primary Key:** `{', '.join(info['primary_key'])}`\n")
        lines.append("| Column | Type | Nullable | Default |")
        lines.append("|---|---|---|---|")
        for col in info["columns"]:
            type_str = col["data_type"]
            if col["char_max_length"]:
                type_str += f"({col['char_max_length']})"
            nullable_str = "YES" if col["nullable"] else "**NO**"
            default_str = f"`{col['default']}`" if col["default"] is not None else "-"
            lines.append(f"| {col['name']} | {type_str} | {nullable_str} | {default_str} |")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Introspect PostgreSQL schema for AI agents and code layers.")
    parser.add_argument("--secret-file", "-s", help="Path to postgres-secret.json")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("db_schema.json"),
        help="Output path for db_schema.json (default: ./db_schema.json)",
    )
    parser.add_argument("--verify", "-v", action="store_true", help="Verify DB schema against Pydantic models")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--stdout", action="store_true", help="Print output to stdout instead of writing to file")
    parser.add_argument("--export-all", action="store_true", help="Export both db_schema.json and openapi.json")
    args = parser.parse_args()

    secret_file = find_secret_file(args.secret_file)
    secret = load_secret(secret_file)
    schema_data = introspect_schema(secret)

    if args.verify:
        success = verify_against_models(schema_data)
        if not success:
            sys.exit(1)
        return

    if args.format == "markdown":
        md = format_markdown(schema_data)
        if args.stdout:
            print(md)
        else:
            args.output.write_text(md, encoding="utf-8")
            print(f"Exported schema markdown to {args.output.resolve()}")
        return

    # JSON export
    json_str = json.dumps(schema_data, indent=2)
    if args.stdout:
        print(json_str)
    else:
        args.output.write_text(json_str, encoding="utf-8")
        print(f"Exported database schema to {args.output.resolve()}")

    if args.export_all:
        from app.scripts.export_openapi import export_openapi
        openapi_path = args.output.parent / "openapi.json"
        export_openapi(openapi_path)
        print(f"Exported OpenAPI schema to {openapi_path.resolve()}")


if __name__ == "__main__":
    main()
