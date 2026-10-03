"""Station metadata and data integrity audit CLI.

Scans the analytical PostgreSQL database to detect:
1. Exact duplicate rows in the `station` table.
2. Dual-identity station duplications (numeric WMO IDs vs. text names, short codes vs. full names).
3. Inconsistent or NULL country codes (e.g. 'zim' vs 'zw').
4. Multi-batch accumulation (stations with multiple unpurged definition_id runs in `summary`).
5. Seasonal rainfall coverage gaps (stations with annual rain but 0 seasonal rain).

Usage:
    python -m app.scripts.audit_stations
    python -m app.scripts.audit_stations --strict
    python -m app.scripts.audit_stations --markdown
    python -m app.scripts.audit_stations --json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from app.core.database import execute_query


def audit_station_integrity() -> Dict[str, Any]:
    """Run all station metadata and data integrity audits against the database."""

    # 1. Exact duplicate rows in station table
    sql_dupes = """
        SELECT station_id, station_name, country_code, count(*) as count
        FROM station
        GROUP BY station_id, station_name, country_code
        HAVING count(*) > 1
        ORDER BY count DESC, station_name;
    """
    _, dupe_rows = execute_query(sql_dupes)

    # 2. Inconsistent or NULL country codes
    sql_country = """
        SELECT station_id, station_name, country_code
        FROM station
        WHERE country_code IS NULL OR country_code NOT IN ('zm', 'zw', 'mw')
        ORDER BY country_code NULLS FIRST, station_name;
    """
    _, country_rows = execute_query(sql_country)

    # 3. Dual-identity duplication: numeric WMO IDs & short code IDs
    sql_all_stations = """
        SELECT DISTINCT station_id, station_name, country_code
        FROM station
        ORDER BY station_name, station_id;
    """
    _, all_stations = execute_query(sql_all_stations)

    # Group by normalized station name to find dual identities
    from collections import defaultdict
    by_name = defaultdict(list)
    for st in all_stations:
        name = (st["station_name"] or "").strip()
        if name:
            by_name[name.upper()].append(st)

    dual_identity_stations: List[Dict[str, Any]] = []
    for name, entries in by_name.items():
        if len(entries) > 1:
            numeric_ids = [e["station_id"] for e in entries if e["station_id"].isdigit()]
            code_ids = [e["station_id"] for e in entries if not e["station_id"].isdigit() and len(e["station_id"]) <= 8 and e["station_id"] != name]
            text_ids = [e["station_id"] for e in entries if not e["station_id"].isdigit() and e["station_id"] not in code_ids]
            
            dual_identity_stations.append({
                "station_name": name,
                "text_ids": text_ids,
                "numeric_ids": numeric_ids,
                "code_ids": code_ids,
                "total_representations": len(entries),
            })

    # 4. Multi-batch accumulation (stations with multiple definition_id runs in summary)
    sql_batches = """
        SELECT station_id, summary_type, count(DISTINCT definition_id) as batch_count, count(*) as row_count
        FROM summary
        GROUP BY station_id, summary_type
        HAVING count(DISTINCT definition_id) > 1
        ORDER BY batch_count DESC, station_id;
    """
    _, batch_rows = execute_query(sql_batches)

    # 5. Seasonal rainfall coverage gaps
    # Stations that have Annual Rain rows but 0 rows for seasonal_total_rain / seasonal_rain
    sql_seasonal_gaps = """
        WITH annual_stations AS (
            SELECT DISTINCT station_id
            FROM summary
            WHERE summary_type = 'Annual Rain'
        ),
        seasonal_stations AS (
            SELECT DISTINCT station_id
            FROM summary
            WHERE summary_type = 'Annual Rain'
              AND (
                  summary_element = 'seasonal_total_rain' 
                  OR (summary_element = 'total_rain' AND lower(summary_name) IN ('seasonal_rain', 'seasonal_rainfall'))
              )
        )
        SELECT a.station_id, s.station_name, s.country_code
        FROM annual_stations a
        LEFT JOIN seasonal_stations ss ON a.station_id = ss.station_id
        LEFT JOIN (SELECT DISTINCT station_id, station_name, country_code FROM station) s ON a.station_id = s.station_id
        WHERE ss.station_id IS NULL
        ORDER BY s.country_code, a.station_id;
    """
    _, gap_rows = execute_query(sql_seasonal_gaps)

    # 6. Duplicate data rows in summary table (same station, year, element, name across batches)
    sql_data_dupes = """
        SELECT 
            count(*) as total_duplicate_groups,
            COALESCE(sum(cnt), 0) as total_rows_in_duplicate_groups,
            COALESCE(sum(cnt - 1), 0) as excess_duplicate_rows
        FROM (
            SELECT station_id, summary_type, time_value, summary_element, summary_name, count(*) as cnt
            FROM summary
            GROUP BY station_id, summary_type, time_value, summary_element, summary_name
            HAVING count(*) > 1
        ) sub;
    """
    _, data_dupe_stats = execute_query(sql_data_dupes)
    data_dupe_summary = data_dupe_stats[0] if data_dupe_stats else {
        "total_duplicate_groups": 0,
        "total_rows_in_duplicate_groups": 0,
        "excess_duplicate_rows": 0,
    }

    sql_top_data_dupes = """
        SELECT station_id, summary_type, sum(cnt - 1) as excess_duplicates
        FROM (
            SELECT station_id, summary_type, time_value, summary_element, summary_name, count(*) as cnt
            FROM summary
            GROUP BY station_id, summary_type, time_value, summary_element, summary_name
            HAVING count(*) > 1
        ) sub
        GROUP BY station_id, summary_type
        ORDER BY excess_duplicates DESC
        LIMIT 10;
    """
    _, top_data_dupe_stations = execute_query(sql_top_data_dupes)

    excess_dupes = int(data_dupe_summary.get("excess_duplicate_rows") or 0)
    total_dupe_groups = int(data_dupe_summary.get("total_duplicate_groups") or 0)
    total_in_groups = int(data_dupe_summary.get("total_rows_in_duplicate_groups") or 0)

    return {
        "summary": {
            "duplicate_row_groups": len(dupe_rows),
            "inconsistent_country_codes": len(country_rows),
            "dual_identity_stations": len(dual_identity_stations),
            "multi_batch_stations": len(batch_rows),
            "stations_missing_seasonal_rain": len(gap_rows),
            "excess_duplicate_data_rows": excess_dupes,
            "duplicate_data_groups": total_dupe_groups,
            "total_rows_in_duplicate_groups": total_in_groups,
        },
        "duplicate_rows": dupe_rows,
        "country_code_issues": country_rows,
        "dual_identity_stations": dual_identity_stations,
        "multi_batch_stations": batch_rows,
        "stations_missing_seasonal_rain": gap_rows,
        "top_duplicate_data_stations": top_data_dupe_stations,
    }


def print_text_report(results: Dict[str, Any]):
    """Print formatted terminal report."""
    summary = results["summary"]
    print("=" * 76)
    print(" E-PICSA DATABASE STATION & DATA INTEGRITY AUDIT REPORT")
    print("=" * 76)
    print(f"Duplicate Metadata Row Groups in 'station':  {summary['duplicate_row_groups']}")
    print(f"Dual-Identity Station Discrepancies:        {summary['dual_identity_stations']}")
    print(f"Inconsistent / NULL Country Codes:          {summary['inconsistent_country_codes']}")
    print(f"Stations with Multiple Ingestion Batches:   {summary['multi_batch_stations']}")
    print(f"Stations with Annual Rain but No Season:    {summary['stations_missing_seasonal_rain']}")
    print(f"Excess Duplicate Data Rows in 'summary':    {summary['excess_duplicate_data_rows']:,}")
    print("-" * 76)

    # 1. Dual Identity Duplications
    if results["dual_identity_stations"]:
        print("\n[!] DUAL-IDENTITY STATION DUPLICATIONS DETECTED:")
        print(f"{'Station Name':<32} {'Text ID':<22} {'Numeric/Code ID':<18}")
        print("-" * 76)
        for st in results["dual_identity_stations"]:
            name = st["station_name"][:30]
            txt = ", ".join(st["text_ids"])[:20] or "-"
            alt = ", ".join(st["numeric_ids"] + st["code_ids"])[:16] or "-"
            print(f"{name:<32} {txt:<22} {alt:<18}")

    # 2. Duplicate Metadata Rows
    if results["duplicate_rows"]:
        print(f"\n[!] EXACT DUPLICATE ROWS IN 'station' TABLE ({len(results['duplicate_rows'])} groups):")
        print(f"{'Station ID':<24} {'Station Name':<30} {'Country':<8} {'Copies':<6}")
        print("-" * 76)
        for r in results["duplicate_rows"][:10]:
            print(f"{r['station_id']:<24} {(r['station_name'] or ''):<30} {(r['country_code'] or 'NULL'):<8} {r['count']:<6}")
        if len(results["duplicate_rows"]) > 10:
            print(f"  ... and {len(results['duplicate_rows']) - 10} more duplicate groups.")

    # 3. Country Code Discrepancies
    if results["country_code_issues"]:
        print(f"\n[!] INCONSISTENT OR NULL COUNTRY CODES ({len(results['country_code_issues'])} rows):")
        for r in results["country_code_issues"][:10]:
            print(f"  - {r['station_id']}: name='{r['station_name']}', country_code='{r['country_code']}'")
        if len(results["country_code_issues"]) > 10:
            print(f"  ... and {len(results['country_code_issues']) - 10} more rows.")

    # 4. Multi-Batch Accumulation
    if results["multi_batch_stations"]:
        print(f"\n[!] MULTI-BATCH ACCUMULATION IN 'summary' ({len(results['multi_batch_stations'])} instances):")
        print(f"{'Station ID':<30} {'Summary Type':<20} {'Batches':<8} {'Rows':<8}")
        print("-" * 76)
        for b in results["multi_batch_stations"][:10]:
            print(f"{b['station_id']:<30} {b['summary_type']:<20} {b['batch_count']:<8} {b['row_count']:<8}")
        if len(results["multi_batch_stations"]) > 10:
            print(f"  ... and {len(results['multi_batch_stations']) - 10} more station summaries.")

    # 5. Top Stations with Duplicate Data Rows
    if results.get("top_duplicate_data_stations"):
        print(f"\n[!] TOP STATIONS WITH DUPLICATE DATA ROWS IN 'summary' (Total Excess: {summary['excess_duplicate_data_rows']:,} rows):")
        print(f"{'Station ID':<30} {'Summary Type':<25} {'Excess Duplicates':<16}")
        print("-" * 76)
        for d in results["top_duplicate_data_stations"][:10]:
            print(f"{d['station_id']:<30} {d['summary_type']:<25} {int(d['excess_duplicates']):<16,}")

    print("\n" + "=" * 76)


def print_markdown_report(results: Dict[str, Any]):
    """Print results formatted as Markdown tables."""
    summary = results["summary"]
    print("# E-PICSA Database Station & Data Integrity Audit Report\n")
    print("## Summary Statistics\n")
    print(f"- **Duplicate Metadata Row Groups in `station`**: {summary['duplicate_row_groups']}")
    print(f"- **Dual-Identity Station Discrepancies**: {summary['dual_identity_stations']}")
    print(f"- **Inconsistent / NULL Country Codes**: {summary['inconsistent_country_codes']}")
    print(f"- **Stations with Multiple Ingestion Batches**: {summary['multi_batch_stations']}")
    print(f"- **Stations Missing Seasonal Rainfall**: {summary['stations_missing_seasonal_rain']}")
    print(f"- **Excess Duplicate Data Rows in `summary`**: {summary['excess_duplicate_data_rows']:,} (in {summary['duplicate_data_groups']:,} groups)\n")

    if results["dual_identity_stations"]:
        print("## Dual-Identity Station Duplications\n")
        print("| Station Name | Text ID | Numeric/Code Alternative ID | Total Representations |")
        print("|---|---|---|---|")
        for st in results["dual_identity_stations"]:
            txt = ", ".join(st["text_ids"]) or "-"
            alt = ", ".join(st["numeric_ids"] + st["code_ids"]) or "-"
            print(f"| {st['station_name']} | `{txt}` | `{alt}` | {st['total_representations']} |")
        print()

    if results["duplicate_rows"]:
        print("## Exact Duplicate Rows in `station`\n")
        print("| Station ID | Station Name | Country Code | Duplicate Row Count |")
        print("|---|---|---|---|")
        for r in results["duplicate_rows"]:
            print(f"| `{r['station_id']}` | {r['station_name']} | `{r['country_code']}` | {r['count']} |")
        print()

    if results.get("top_duplicate_data_stations"):
        print("## Top Stations with Excess Duplicate Data Rows in `summary`\n")
        print("| Station ID | Summary Type | Excess Duplicate Rows |")
        print("|---|---|---|")
        for d in results["top_duplicate_data_stations"]:
            print(f"| `{d['station_id']}` | {d['summary_type']} | {int(d['excess_duplicates']):,} |")
        print()


def main():
    parser = argparse.ArgumentParser(description="Audit database station identities, duplications, and data integrity.")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if duplicates or integrity issues exist.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    parser.add_argument("--markdown", action="store_true", help="Output GitHub-flavored Markdown.")

    args = parser.parse_args()
    results = audit_station_integrity()

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    elif args.markdown:
        print_markdown_report(results)
    else:
        print_text_report(results)

    if args.strict:
        has_issues = (
            results["summary"]["duplicate_row_groups"] > 0
            or results["summary"]["dual_identity_stations"] > 0
            or results["summary"]["inconsistent_country_codes"] > 0
        )
        if has_issues:
            sys.exit(1)


if __name__ == "__main__":
    main()
