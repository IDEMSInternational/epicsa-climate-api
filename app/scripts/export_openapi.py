#!/usr/bin/env python3
"""
Export FastAPI OpenAPI specification.

Usage:
    # Print to stdout:
    python -m app.scripts.export_openapi --stdout > openapi.json

    # Write to a file (default: ./openapi.json or specified path):
    python -m app.scripts.export_openapi [--output path/to/openapi.json]
"""

import argparse
import json
from pathlib import Path
import sys

from app.main import app


def get_openapi_json(indent: int = 2) -> str:
    return json.dumps(app.openapi(), indent=indent)


def export_openapi(output_path: Path) -> Path:
    openapi_content = get_openapi_json()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(openapi_content, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Export OpenAPI schema to a JSON file or stdout.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Target output path for openapi.json",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the OpenAPI JSON to stdout instead of writing to a file",
    )
    args = parser.parse_args()

    if args.stdout:
        sys.stdout.write(get_openapi_json())
        sys.stdout.flush()
        return

    # Determine default path if not explicitly provided
    target_path = args.output
    if target_path is None:
        # Default to repo root (parent of app/)
        target_path = Path(__file__).resolve().parent.parent.parent / "openapi.json"

    out_file = export_openapi(target_path)
    print(f"Successfully exported OpenAPI schema ({app.title} v{app.version}) to:")
    print(f"  {out_file.resolve()}")


if __name__ == "__main__":
    main()
