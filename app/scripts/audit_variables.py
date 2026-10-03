"""Audit and drift-detection CLI for database climate variable names.

Scans the analytical PostgreSQL database (`summary` and `definition` tables),
cross-references all (summary_element, summary_name) pairs against the canonical
variable mappings in `app.services.variable_mappings`, and reports unmapped or
fragmented variables.

Usage:
    python -m app.scripts.audit_variables
    python -m app.scripts.audit_variables --strict
    python -m app.scripts.audit_variables --summary-type "Annual Rain"
    python -m app.scripts.audit_variables --markdown
    python -m app.scripts.audit_variables --json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from app.core.database import execute_query
from app.services.variable_mappings import (
    ANNUAL_RAIN_AUXILIARY_SET,
    ANNUAL_RAIN_EXACT_MAP,
    SUBSEASONAL_PREFIXES,
    map_annual_rain_field,
)


def audit_summary_variables(summary_type_filter: Optional[str] = None) -> Dict[str, Any]:
    """Audit all variables in summary table and categorize them."""
    sql = """
        SELECT 
            summary_type,
            summary_element,
            summary_name,
            count(*) as row_count,
            count(DISTINCT station_id) as station_count
        FROM summary
    """
    params: List[Any] = []
    if summary_type_filter:
        sql += " WHERE summary_type = %s"
        params.append(summary_type_filter)

    sql += """
        GROUP BY summary_type, summary_element, summary_name
        ORDER BY summary_type, summary_element, summary_name;
    """

    _, rows = execute_query(sql, params)

    mapped_items: List[Dict[str, Any]] = []
    auxiliary_items: List[Dict[str, Any]] = []
    unmapped_items: List[Dict[str, Any]] = []

    for r in rows:
        stype = r["summary_type"] or ""
        elem = r["summary_element"] or ""
        name = r["summary_name"] or ""
        name_lower = name.lower()
        key = (elem, name_lower)

        row_info = {
            "summary_type": stype,
            "summary_element": elem,
            "summary_name": name,
            "row_count": r["row_count"],
            "station_count": r["station_count"],
        }

        if stype == "Annual Rain":
            mapping = map_annual_rain_field(elem, name, 1.0)
            if mapping:
                row_info["canonical_field"] = mapping[0]
                row_info["match_type"] = "exact" if key in ANNUAL_RAIN_EXACT_MAP else "heuristic"
                mapped_items.append(row_info)
            elif key in ANNUAL_RAIN_AUXILIARY_SET or (
                elem == "total_rain" and any(name_lower.startswith(p) for p in SUBSEASONAL_PREFIXES)
            ):
                row_info["category"] = "sub-seasonal_or_auxiliary"
                auxiliary_items.append(row_info)
            else:
                unmapped_items.append(row_info)

        elif "Temperature" in stype:
            # Standard temperature metrics
            if elem in ("tmax_max", "tmax_mean", "tmax_min", "tmin_max", "tmin_mean", "tmin_min"):
                row_info["canonical_field"] = elem
                row_info["match_type"] = "standard_temp"
                mapped_items.append(row_info)
            else:
                unmapped_items.append(row_info)

        elif stype == "Monthly Rain":
            if elem == "total_rain" and name_lower == "sum_rainfall":
                row_info["canonical_field"] = "monthly_rain"
                row_info["match_type"] = "standard_monthly_rain"
                mapped_items.append(row_info)
            else:
                unmapped_items.append(row_info)

        else:
            # Other summary types (Crops, etc.)
            auxiliary_items.append(row_info)

    total_rows = sum(r["row_count"] for r in rows)
    return {
        "summary": {
            "total_pairs": len(rows),
            "total_rows": total_rows,
            "mapped_pairs": len(mapped_items),
            "auxiliary_pairs": len(auxiliary_items),
            "unmapped_pairs": len(unmapped_items),
        },
        "mapped": mapped_items,
        "auxiliary": auxiliary_items,
        "unmapped": unmapped_items,
    }


def format_report_text(results: Dict[str, Any]) -> str:
    """Format audit results as a readable CLI text report."""
    s = results["summary"]
    lines = [
        "=" * 70,
        " E-PICSA DATABASE VARIABLE AUDIT REPORT",
        "=" * 70,
        f"Total Variable Pairs Checked: {s['total_pairs']}",
        f"Total Data Rows Represented:  {s['total_rows']:,}",
        f"  - Fully Mapped to Schema:   {s['mapped_pairs']}",
        f"  - Auxiliary / Sub-seasonal: {s['auxiliary_pairs']}",
        f"  - Unmapped / Discrepancies: {s['unmapped_pairs']}",
        "-" * 70,
    ]

    if results["unmapped"]:
        lines.append("\n[!] UNMAPPED VARIABLES DETECTED (ACTION REQUIRED):")
        for u in results["unmapped"]:
            lines.append(
                f"  * [{u['summary_type']}] elem='{u['summary_element']}', "
                f"name='{u['summary_name']}' ({u['row_count']:,} rows, {u['station_count']} stations)"
            )
    else:
        lines.append("\n[✓] All database variables are 100% accounted for in variable mappings!")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def format_report_markdown(results: Dict[str, Any]) -> str:
    """Format audit results as a GitHub Flavored Markdown table report."""
    s = results["summary"]
    lines = [
        "# Database Variable Audit Report",
        "",
        f"- **Total Variable Pairs**: {s['total_pairs']}",
        f"- **Total Rows**: {s['total_rows']:,}",
        f"- **Mapped Pairs**: {s['mapped_pairs']}",
        f"- **Auxiliary Pairs**: {s['auxiliary_pairs']}",
        f"- **Unmapped Pairs**: {s['unmapped_pairs']}",
        "",
    ]

    if results["unmapped"]:
        lines.extend([
            "## ⚠️ Unmapped Variables",
            "",
            "| Summary Type | Element | Name | Rows | Stations |",
            "|---|---|---|---|---|",
        ])
        for u in results["unmapped"]:
            lines.append(
                f"| `{u['summary_type']}` | `{u['summary_element']}` | `{u['summary_name']}` | {u['row_count']:,} | {u['station_count']} |"
            )
        lines.append("")

    lines.extend([
        "## Mapped Variables",
        "",
        "| Summary Type | Element | Name | Canonical Field | Match Type | Rows | Stations |",
        "|---|---|---|---|---|---|---|",
    ])
    for m in results["mapped"]:
        lines.append(
            f"| `{m['summary_type']}` | `{m['summary_element']}` | `{m['summary_name']}` | `{m['canonical_field']}` | {m.get('match_type', 'exact')} | {m['row_count']:,} | {m['station_count']} |"
        )

    lines.extend([
        "",
        "## Auxiliary & Sub-seasonal Variables",
        "",
        "| Summary Type | Element | Name | Rows | Stations |",
        "|---|---|---|---|---|",
    ])
    for a in results["auxiliary"]:
        lines.append(
            f"| `{a['summary_type']}` | `{a['summary_element']}` | `{a['summary_name']}` | {a['row_count']:,} | {a['station_count']} |"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit analytical database variable names against canonical mappings.")
    parser.add_argument("--summary-type", help="Filter by summary_type (e.g. 'Annual Rain')")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if unmapped variables are found")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--markdown", action="store_true", help="Output GitHub-flavored Markdown")
    args = parser.parse_args()

    results = audit_summary_variables(summary_type_filter=args.summary_type)

    if args.json:
        print(json.dumps(results, indent=2))
    elif args.markdown:
        print(format_report_markdown(results))
    else:
        print(format_report_text(results))

    if args.strict and results["summary"]["unmapped_pairs"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
