#!/usr/bin/env python3
"""
Dump a snapshot of the PostgreSQL database locally to assist with planning,
offline testing, and verifying data structures across tables.

Usage:
    # Export summary report and sample JSON data to data_snapshot/:
    python -m app.scripts.dump_db_snapshot

    # Export all rows for specific stations:
    python -m app.scripts.dump_db_snapshot --stations Kasungu Choma

    # Dump full database tables to SQLite database file:
    python -m app.scripts.dump_db_snapshot --to-sqlite data_snapshot/epicsa_local.db
"""

import argparse
import datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any, Dict, List, Optional

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None

from app.scripts.introspect_schema import find_secret_file, get_db_connection, load_secret


class JSONEncoderWithTypes(json.JSONEncoder):
    """JSON encoder handling datetime and Decimal objects."""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def get_table_counts(conn) -> Dict[str, int]:
    tables = ["station", "definition", "summary_station_metadata", "summary", "crop"]
    counts = {}
    with conn.cursor() as cur:
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                counts[t] = cur.fetchone()[0]
            except Exception as e:
                counts[t] = -1
                conn.rollback()
    return counts


def get_schema_summary(conn) -> Dict[str, Any]:
    summary_info: Dict[str, Any] = {}
    with conn.cursor(row_factory=dict_row) as cur:
        # 1. Distinct countries and station counts
        cur.execute("""
            SELECT country_code, COUNT(*) as station_count
            FROM station
            GROUP BY country_code
            ORDER BY country_code;
        """)
        summary_info["countries"] = cur.fetchall()

        # 2. Distinct time_types in summary
        cur.execute("""
            SELECT time_type, COUNT(*) as count
            FROM summary
            GROUP BY time_type
            ORDER BY count DESC;
        """)
        summary_info["summary_time_types"] = cur.fetchall()

        # 3. Distinct summary_types and summary_elements in summary
        cur.execute("""
            SELECT summary_type, summary_element, COUNT(*) as count
            FROM summary
            GROUP BY summary_type, summary_element
            ORDER BY summary_type, summary_element;
        """)
        summary_info["summary_categories"] = cur.fetchall()

        # 4. Distinct summary_names in summary
        cur.execute("""
            SELECT summary_name, COUNT(*) as count
            FROM summary
            GROUP BY summary_name
            ORDER BY count DESC;
        """)
        summary_info["summary_names"] = cur.fetchall()

        # 5. Distinct summary_types in summary_station_metadata
        cur.execute("""
            SELECT summary_type, COUNT(*) as count
            FROM summary_station_metadata
            GROUP BY summary_type
            ORDER BY count DESC;
        """)
        summary_info["metadata_summary_types"] = cur.fetchall()

        # 6. Distinct crop summary types and elements
        cur.execute("""
            SELECT summary_type, summary_element, COUNT(*) as count
            FROM crop
            GROUP BY summary_type, summary_element
            ORDER BY summary_type;
        """)
        summary_info["crop_categories"] = cur.fetchall()

    return summary_info


def dump_station_data(conn, station_id: str, max_rows: int = 500) -> Dict[str, Any]:
    station_dump: Dict[str, Any] = {"station_id": station_id}
    with conn.cursor(row_factory=dict_row) as cur:
        # Station info
        cur.execute("SELECT * FROM station WHERE station_id = %s;", [station_id])
        station_dump["station"] = cur.fetchall()

        # Definitions linked to this station
        cur.execute("""
            SELECT ssm.summary_type, d.definition_id, d.summary_element, d.definition_value, d.accreditation
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s;
        """, [station_id])
        station_dump["definitions"] = cur.fetchall()

        # Sample annual summaries
        cur.execute("""
            SELECT time_type, time_value, summary_type, summary_element, summary_name, summary_value
            FROM summary
            WHERE station_id = %s AND time_type = 'year'
            ORDER BY time_value ASC
            LIMIT %s;
        """, [station_id, max_rows])
        station_dump["annual_summaries_sample"] = cur.fetchall()

        # Sample monthly summaries
        cur.execute("""
            SELECT time_type, time_value, summary_type, summary_element, summary_name, summary_value
            FROM summary
            WHERE station_id = %s AND time_type = 'month'
            ORDER BY time_value ASC
            LIMIT %s;
        """, [station_id, max_rows])
        station_dump["monthly_summaries_sample"] = cur.fetchall()

        # Sample crop summaries
        cur.execute("""
            SELECT year, plant_day, plant_length, rain_total, include_start_condition, summary_type, summary_element, summary_value
            FROM crop
            WHERE station_id = %s
            ORDER BY year, plant_day, plant_length
            LIMIT %s;
        """, [station_id, max_rows])
        station_dump["crop_sample"] = cur.fetchall()

    return station_dump


def dump_to_sqlite(conn, sqlite_path: Path, max_rows_per_table: Optional[int] = None):
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if sqlite_path.exists():
        sqlite_path.unlink()

    sconn = sqlite3.connect(str(sqlite_path))
    tables = ["station", "definition", "summary_station_metadata", "summary", "crop"]

    with conn.cursor(row_factory=dict_row) as cur:
        for table in tables:
            print(f"Exporting table '{table}' to SQLite...")
            query = f"SELECT * FROM {table}"
            if max_rows_per_table:
                query += f" LIMIT {max_rows_per_table}"
            cur.execute(query)
            rows = cur.fetchall()

            if not rows:
                print(f"  Table '{table}' has no rows to export.")
                continue

            # Create table
            cols = list(rows[0].keys())
            col_defs = ", ".join(f'"{c}" TEXT' for c in cols)
            sconn.execute(f'CREATE TABLE "{table}" ({col_defs});')

            placeholders = ", ".join("?" for _ in cols)
            insert_sql = f'INSERT INTO "{table}" ({", ".join(f"{c}" for c in cols)}) VALUES ({placeholders})'

            formatted_rows = []
            for r in rows:
                row_vals = []
                for c in cols:
                    val = r[c]
                    if isinstance(val, (dict, list)):
                        val = json.dumps(val, cls=JSONEncoderWithTypes)
                    elif isinstance(val, (datetime.date, datetime.datetime)):
                        val = val.isoformat()
                    elif isinstance(val, Decimal):
                        val = float(val)
                    row_vals.append(val)
                formatted_rows.append(row_vals)

            sconn.executemany(insert_sql, formatted_rows)
            sconn.commit()
            print(f"  Exported {len(rows)} rows to SQLite '{table}'.")

    sconn.close()
    print(f"✅ SQLite export complete: {sqlite_path}")


def main():
    parser = argparse.ArgumentParser(description="Export snapshot of PostgreSQL climate data locally.")
    parser.add_argument("--secret-file", "-s", help="Path to postgres-secret.json")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("data_snapshot"),
        help="Directory to save snapshot files (default: data_snapshot)",
    )
    parser.add_argument(
        "--stations",
        nargs="*",
        default=["Kasungu", "Choma", "dodoma"],
        help="Specific station IDs to dump detailed samples for",
    )
    parser.add_argument(
        "--to-sqlite",
        type=Path,
        help="Export tables to a local SQLite database file (e.g. data_snapshot/epicsa_local.db)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=1000,
        help="Max rows to export per table/category in samples",
    )
    args = parser.parse_args()

    secret_file = find_secret_file(args.secret_file)
    secret = load_secret(secret_file)

    print(f"Connecting to PostgreSQL database '{secret.get('dbname')}' at {secret.get('host')}...")
    conn = get_db_connection(secret)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Table row counts
        counts = get_table_counts(conn)
        print("\n=== Table Row Counts ===")
        for t, c in counts.items():
            print(f"  {t:25}: {c:,} rows")

        # 2. Schema breakdown
        print("\nAnalyzing database statistics...")
        stats = get_schema_summary(conn)
        stats["row_counts"] = counts

        stats_file = args.output_dir / "database_summary.json"
        stats_file.write_text(json.dumps(stats, indent=2, cls=JSONEncoderWithTypes), encoding="utf-8")
        print(f"Saved database summary to {stats_file}")

        # 3. Station samples
        for stn in args.stations:
            print(f"Extracting sample data for station '{stn}'...")
            stn_data = dump_station_data(conn, stn, max_rows=args.max_rows)
            stn_file = args.output_dir / f"station_{stn}_sample.json"
            stn_file.write_text(json.dumps(stn_data, indent=2, cls=JSONEncoderWithTypes), encoding="utf-8")
            print(f"  Saved station sample to {stn_file}")

        # 4. Optional SQLite dump
        if args.to_sqlite:
            dump_to_sqlite(conn, args.to_sqlite)

        print(f"\n✅ Snapshot successfully created in: {args.output_dir.resolve()}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
