"""Canonical climate variable mappings for E-PICSA API.

This module provides a centralized, declarative dictionary of known variable
mappings from the analytical PostgreSQL database (populated by R-Instat / epicsawrap)
to canonical Pydantic model fields.

Historical Context:
-------------------
The analytical PostgreSQL database (`summary` table) uses an Entity-Attribute-Value (EAV)
structure with `summary_element` and `summary_name` columns. Due to unconstrained VARCHAR(255)
columns and disparate national ingestion scripts across Zambia, Zimbabwe, and Malawi, there are
over 90 spelling, casing, and category variations for rainfall variables.

This module provides an Anti-Corruption Layer (ACL) that shields the FastAPI application
from naming discrepancies and ensures deterministic, type-safe pivoting.
"""

from typing import Any, Callable, Dict, Optional, Set, Tuple


def _safe_float(val: Any) -> Optional[float]:
    """Parse a float value safely, returning None on failure or missing sentinels."""
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() in ("", "na", "null", "none"):
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _safe_int(val: Any) -> Optional[int]:
    """Parse an integer value safely, returning None on failure or missing sentinels."""
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() in ("", "na", "null", "none"):
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def _safe_bool(val: Any) -> Optional[bool]:
    """Parse a boolean value safely, returning None on failure or missing sentinels."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    s = str(val).strip().upper()
    if s in ("TRUE", "1", "T"):
        return True
    if s in ("FALSE", "0", "F"):
        return False
    return None


def _safe_str(val: Any) -> Optional[str]:
    """Parse a non-empty string safely, returning None on missing sentinels."""
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() in ("", "na", "null", "none"):
        return None
    return s


# ---------------------------------------------------------------------------
# Exact Lookups: (summary_element, summary_name_lower) -> (canonical_field, caster)
# ---------------------------------------------------------------------------
ANNUAL_RAIN_EXACT_MAP: Dict[Tuple[str, str], Tuple[str, Callable[[Any], Any]]] = {
    # 1. Seasonal Total Rainfall (amount in mm)
    # Zimbabwe convention: seasonal_total_rain with seasonal_PRECIP / season_PRECIP
    ("seasonal_total_rain", "seasonal_precip"): ("seasonal_rain", _safe_float),
    ("seasonal_total_rain", "season_precip"): ("seasonal_rain", _safe_float),
    ("seasonal_total_rain", "seasonal_rain"): ("seasonal_rain", _safe_float),
    ("seasonal_total_rain", "seasonal_rainfall"): ("seasonal_rain", _safe_float),
    # Zambia convention: stored under generic total_rain with seasonal names
    ("total_rain", "seasonal_rain"): ("seasonal_rain", _safe_float),
    ("total_rain", "seasonal_rainfall"): ("seasonal_rain", _safe_float),
    ("total_rain", "seasonal_precip"): ("seasonal_rain", _safe_float),
    ("total_rain", "season_precip"): ("seasonal_rain", _safe_float),

    # 2. Seasonal Rain Days (count of rainy days in season)
    # Zimbabwe convention: seasonal_rain_day with seasonal_rainday / season_RainyDay
    ("seasonal_rain_day", "seasonal_rainday"): ("n_seasonal_rain", _safe_int),
    ("seasonal_rain_day", "seasonal_raindays"): ("n_seasonal_rain", _safe_int),
    ("seasonal_rain_day", "season_rainyday"): ("n_seasonal_rain", _safe_int),
    ("seasonal_rain_day", "n_seasonal_rain"): ("n_seasonal_rain", _safe_int),
    # Zambia convention: stored under generic rain_day with seasonal names
    ("rain_day", "seasonal_rainday"): ("n_seasonal_rain", _safe_int),
    ("rain_day", "seasonal_raindays"): ("n_seasonal_rain", _safe_int),

    # 3. Annual Rainfall Total (amount in mm for full year / agricultural year)
    ("total_rain", "annual_rain"): ("annual_rain", _safe_float),
    ("total_rain", "annual_rainfall"): ("annual_rain", _safe_float),
    ("total_rain", "total_rain"): ("annual_rain", _safe_float),
    ("total_rain", "oct_apr_precip"): ("annual_rain", _safe_float),
    ("total_rain", "sum_precip"): ("annual_rain", _safe_float),
    ("total_rain", "sum_rain"): ("annual_rain", _safe_float),
    ("total_rain", "sum_rainfall"): ("annual_rain", _safe_float),

    # 4. Annual Rain Days (count of rainy days across the year)
    ("rain_day", "no_of_raindays"): ("n_rain", _safe_int),
    ("rain_day", "annual_rainday"): ("n_rain", _safe_int),
    ("rain_day", "annual_raindays"): ("n_rain", _safe_int),
    ("rain_day", "annual_rainy"): ("n_rain", _safe_int),
    ("rain_day", "oct_apr_rainday"): ("n_rain", _safe_int),
    ("rain_day", "oct_apr_rainyday"): ("n_rain", _safe_int),
    ("rain_day", "sum_rain_day"): ("n_rain", _safe_int),
    ("rain_day", "sum_rainday"): ("n_rain", _safe_int),
    ("rain_day", "sum_rainy"): ("n_rain", _safe_int),
    ("rain_day", "sum_count"): ("n_rain", _safe_int),
    ("rain_day", "n_rain"): ("n_rain", _safe_int),
    ("rain_day", "rain_day"): ("n_rain", _safe_int),

    # 5. Start of Rains DOY (Day of Year)
    ("start_rain", "start"): ("start_rains_doy", _safe_int),
    ("start_rain", "start_rains"): ("start_rains_doy", _safe_int),
    ("start_rain", "start_season"): ("start_rains_doy", _safe_int),
    ("start_rain", "start_dry"): ("start_rains_doy", _safe_int),
    ("start_rain", "start_dryspell"): ("start_rains_doy", _safe_int),
    ("start_rain", "dryspell"): ("start_rains_doy", _safe_int),

    # 6. Start of Rains Date (YYYY-MM-DD string)
    ("start_rain_date", "start_d"): ("start_rains_date", _safe_str),
    ("start_rain_date", "start_rains_date"): ("start_rains_date", _safe_str),
    ("start_rain_date", "start_season_date"): ("start_rains_date", _safe_str),
    ("start_rain_date", "start_dry_d"): ("start_rains_date", _safe_str),
    ("start_rain_date", "star_dry_d"): ("start_rains_date", _safe_str),  # Ingestion typo
    ("start_rain_date", "start_d_dryspell"): ("start_rains_date", _safe_str),
    ("start_rain_date", "dryspell_d"): ("start_rains_date", _safe_str),

    # 7. Start of Rains Status (Boolean flag)
    ("start_rain_status", "start_s"): ("start_rains_status", _safe_bool),
    ("start_rain_status", "start_rains_status"): ("start_rains_status", _safe_bool),
    ("start_rain_status", "start_season_status"): ("start_rains_status", _safe_bool),
    ("start_rain_status", "start_dry_s"): ("start_rains_status", _safe_bool),
    ("start_rain_status", "start_s_dryspell"): ("start_rains_status", _safe_bool),
    ("start_rain_status", "dryspell_s"): ("start_rains_status", _safe_bool),

    # 8. End of Rains (DOY, Date, Status)
    ("end_rain", "end_rains"): ("end_rains_doy", _safe_int),
    ("end_rain", "end_rain"): ("end_rains_doy", _safe_int),
    ("end_rain_date", "end_rains_date"): ("end_rains_date", _safe_str),
    ("end_rain_date", "end_rain_date"): ("end_rains_date", _safe_str),
    ("end_rain_status", "end_rains_status"): ("end_rains_status", _safe_bool),
    ("end_rain_status", "end_rain_status"): ("end_rains_status", _safe_bool),

    # 9. End of Season (Water-balance DOY, Date, Status)
    ("end_season", "end_season"): ("end_season_doy", _safe_int),
    ("end_season_date", "end_season_date"): ("end_season_date", _safe_str),
    ("end_season_status", "end_season_status"): ("end_season_status", _safe_bool),

    # 10. Season Length (Duration in days)
    ("season_length", "length"): ("season_length", _safe_float),
    ("season_length", "length_rains"): ("season_length", _safe_float),
    ("season_length", "length_season"): ("season_length", _safe_float),
    ("season_length", "season_length"): ("season_length", _safe_float),
}


# ---------------------------------------------------------------------------
# Auxiliary / Ignored Variables: Known in DB but not mapped to annual model
# ---------------------------------------------------------------------------
ANNUAL_RAIN_AUXILIARY_SET: Set[Tuple[str, str]] = {
    # 3-Month sub-seasonal totals (OND, DJF, JFM, FMA, NDJ) stored under total_rain
    ("total_rain", "ond_rainfall"),
    ("total_rain", "ond_rain"),
    ("total_rain", "djf_rainfall"),
    ("total_rain", "djf_rain"),
    ("total_rain", "jfm_rainfall"),
    ("total_rain", "jfm_rain"),
    ("total_rain", "fma_rainfall"),
    ("total_rain", "fma_rain"),
    ("total_rain", "ndj_rainfall"),
    ("total_rain", "ndj_rain"),

    # Dry spells (handled by separate dry spell summaries)
    ("dry_spell", "spells"),
    ("dry_spell", "spells_90"),
    ("dry_spell", "spells_djfm"),
    ("total_rain", "max_dry_spell"),
    ("total_rain", "longest_dry_spell"),

    # Temperature extremes recorded in rain summaries
    ("tmax_max", "max_tmpmax"),
    ("tmax_mean", "mean_tmpmax"),
    ("tmax_min", "min_tmpmax"),
    ("tmin_max", "max_tmpmin"),
    ("tmin_mean", "mean_tmpmin"),
    ("tmin_min", "min_tmpmin"),
}


# Prefixes of all 12 climatological 3-month sub-seasonal windows to never assign to annual_rain
SUBSEASONAL_PREFIXES: Tuple[str, ...] = (
    "djf_", "jfm_", "fma_", "mam_", "amj_", "mjj_",
    "jja_", "jas_", "aso_", "son_", "ond_", "ndj_",
)


def map_annual_rain_field(
    summary_element: Optional[str],
    summary_name: Optional[str],
    value: Any,
) -> Optional[Tuple[str, Any]]:
    """
    Map a raw database (summary_element, summary_name) pair to a canonical field.

    Returns:
        (canonical_field_name, parsed_value) if mapped and valid.
        None if the variable is recognized as auxiliary/sub-seasonal or unmapped.
    """
    if not summary_element:
        return None

    elem = summary_element.strip()
    name = (summary_name or "").strip().lower()
    key = (elem, name)

    # 1. Exact match lookup (fastest & deterministic)
    if key in ANNUAL_RAIN_EXACT_MAP:
        field_name, caster = ANNUAL_RAIN_EXACT_MAP[key]
        return field_name, caster(value)

    # 2. Known auxiliary check (sub-seasonal 3-month blocks, dry spells, etc.)
    if key in ANNUAL_RAIN_AUXILIARY_SET:
        return None

    # Guard against any unlisted sub-seasonal 3-month block polluting annual totals
    if elem == "total_rain" and any(name.startswith(p) for p in SUBSEASONAL_PREFIXES):
        return None

    # 3. Fallback heuristics for newly introduced variants conforming to standard patterns
    if elem in ("seasonal_total_rain", "seasonal_rain") or ("season" in name and ("precip" in name or "rain" in name)):
        return "seasonal_rain", _safe_float(value)
    if elem in ("seasonal_rain_day", "seasonal_rainday") or ("season" in name and "rainday" in name):
        return "n_seasonal_rain", _safe_int(value)
    if elem == "total_rain" and not any(name.startswith(p) for p in SUBSEASONAL_PREFIXES) and not ("dry" in name or "spell" in name):
        return "annual_rain", _safe_float(value)
    if elem == "rain_day":
        return "n_rain", _safe_int(value)
    if elem == "start_rain":
        return "start_rains_doy", _safe_int(value)
    if elem == "start_rain_date":
        return "start_rains_date", _safe_str(value)
    if elem == "start_rain_status":
        return "start_rains_status", _safe_bool(value)
    if elem == "end_rain":
        return "end_rains_doy", _safe_int(value)
    if elem == "end_rain_date":
        return "end_rains_date", _safe_str(value)
    if elem == "end_rain_status":
        return "end_rains_status", _safe_bool(value)
    if elem == "end_season":
        return "end_season_doy", _safe_int(value)
    if elem == "end_season_date":
        return "end_season_date", _safe_str(value)
    if elem == "end_season_status":
        return "end_season_status", _safe_bool(value)
    if elem == "season_length":
        return "season_length", _safe_float(value)

    return None
