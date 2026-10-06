import json
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException

from app.core.database import execute_query
from app.definitions import country_code
from app.services.variable_mappings import map_annual_rain_field
from app.utils.data import trim_empty_records
from app.core.responce_models.station_responce_model import (
    StationDataResponce,
    StationAndDefintionResponce,
    StationDefinitionDataResponce,
    StationListResponce,
)
from app.core.responce_models.definitions_responce_model import (
    AnnualRain,
    CropsSuccess,
    EndRains,
    EndSeason,
    SeasonStartProbabilities,
    SeasonalLength,
    SeasonalRain,
    SeasonalTotalRainfall,
    StartRains,
    Temp,
)
from app.core.responce_models.rainfall_summaries_responce_model import (
    AnnualRainfallSummariesResponce,
    AnnualRainfallSummariesMetadata,
    AnnualRainfallSummariesdata,
)
from app.core.responce_models.temperature_responce_model import (
    AnnualTemperatureSummariesResponce,
    MonthlyTemperatureSummariesResponce,
    TemperatureSummariesMetadata,
    AnnualTempartureSummariesdata,
    MonthlyTempartureSummariesdata,
)
from app.core.responce_models.crop_success_probabilities_model import (
    CropSuccessProbabilitiesResponce,
    CropSuccessProbabilitiesMetadata,
    CropSuccessProbabilitiesdata,
)
from app.core.responce_models.season_start_probabilities import (
    SeasonStartProbabilitiesResponce,
    SeasonStartProbabilitiesMetadata,
    SeasonStartProbabilitiesdata,
)

# Month mapping for annual-monthly format (e.g. "1951-Jul")
MONTH_NAME_TO_INT = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def _safe_float(val: Any) -> Optional[float]:
    if val is None or val == "" or val == "NA" or val == "NA_character_":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_int(val: Any) -> Optional[int]:
    if val is None or val == "" or val == "NA" or val == "NA_character_":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _safe_bool(val: Any) -> Optional[bool]:
    if val is None or val == "" or val == "NA":
        return None
    if isinstance(val, bool):
        return val
    s = str(val).strip().upper()
    if s in ("TRUE", "1", "T"):
        return True
    if s in ("FALSE", "0", "F"):
        return False
    return None


def _parse_definition_value(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {}


class ClimateRepository:
    """Repository providing climate queries against PostgreSQL for /v2 endpoints."""

    def normalize_country_codes(self, country: str) -> List[str]:
        """Normalize API country codes to database country_code values."""
        c = str(country).lower().strip()
        if c in ("zm", "zm_test", "zm_workshops"):
            return ["zm"]
        if c in ("zw", "zw_test", "zw_workshops", "zim"):
            return ["zim", "zw"]
        if c in ("mw", "mw_test", "mw_workshops"):
            return ["mw"]
        if c == "internal_tests":
            return ["TZ", "zm", "zim", "mw"]
        return [c]

    def map_to_api_country_code(self, db_country_code: Optional[str]) -> country_code:
        """Map database country code string back to valid API country_code literal."""
        if not db_country_code:
            return "zm"
        code = str(db_country_code).strip()
        if code in ("zim", "zw"):
            return "zw"
        if code in ("zm", "mw"):
            return code  # type: ignore
        if code == "TZ":
            return "internal_tests"
        return "zm"

    def get_latest_generation_for_summary(
        self,
        station_id: str,
        summary_type: str,
        generation_id: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Find (definition_id, time_stamp) for a station and summary_type.
        If generation_id is specified, fetch the timestamp for that generation.
        Otherwise, fetch the latest generation by time_stamp.
        """
        if generation_id:
            sql = """
                SELECT definition_id, time_stamp
                FROM summary
                WHERE station_id = %s AND summary_type = %s AND definition_id = %s
                ORDER BY time_stamp DESC
                LIMIT 1;
            """
            _, rows = execute_query(sql, [station_id, summary_type, generation_id])
            if rows:
                return rows[0].get("definition_id"), rows[0].get("time_stamp")
            return generation_id, None

        sql = """
            SELECT definition_id, time_stamp
            FROM summary
            WHERE station_id = %s AND summary_type = %s AND definition_id IS NOT NULL AND definition_id != ''
            ORDER BY time_stamp DESC
            LIMIT 1;
        """
        _, rows = execute_query(sql, [station_id, summary_type])
        if rows and rows[0].get("definition_id"):
            return rows[0].get("definition_id"), rows[0].get("time_stamp")

        sql_meta = """
            SELECT definition_id, time_stamp
            FROM summary_station_metadata
            WHERE station_id = %s AND summary_type = %s AND definition_id IS NOT NULL AND definition_id != ''
            ORDER BY time_stamp DESC
            LIMIT 1;
        """
        _, rows_meta = execute_query(sql_meta, [station_id, summary_type])
        if rows_meta and rows_meta[0].get("definition_id"):
            return rows_meta[0].get("definition_id"), rows_meta[0].get("time_stamp")

        return None, None

    def get_latest_generation_for_crop(
        self,
        station_id: str,
        generation_id: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Find (definition_id, time_stamp) for crop table.
        If generation_id is specified, fetch the timestamp for that generation.
        Otherwise, fetch the latest generation by time_stamp.
        """
        if generation_id:
            sql = """
                SELECT definition_id, time_stamp
                FROM crop
                WHERE station_id = %s AND definition_id = %s
                ORDER BY time_stamp DESC
                LIMIT 1;
            """
            _, rows = execute_query(sql, [station_id, generation_id])
            if rows:
                return rows[0].get("definition_id"), rows[0].get("time_stamp")
            return generation_id, None

        sql = """
            SELECT definition_id, time_stamp
            FROM crop
            WHERE station_id = %s AND definition_id IS NOT NULL AND definition_id != ''
            ORDER BY time_stamp DESC
            LIMIT 1;
        """
        _, rows = execute_query(sql, [station_id])
        if rows and rows[0].get("definition_id"):
            return rows[0].get("definition_id"), rows[0].get("time_stamp")

        sql_meta = """
            SELECT definition_id, time_stamp
            FROM summary_station_metadata
            WHERE station_id = %s AND summary_type = 'Crops' AND definition_id IS NOT NULL AND definition_id != ''
            ORDER BY time_stamp DESC
            LIMIT 1;
        """
        _, rows_meta = execute_query(sql_meta, [station_id])
        if rows_meta and rows_meta[0].get("definition_id"):
            return rows_meta[0].get("definition_id"), rows_meta[0].get("time_stamp")

        return None, None

    def get_stations_by_country(self, country: str) -> List[StationDataResponce]:
        """Retrieve list of stations for a given country code."""
        db_codes = self.normalize_country_codes(country)
        placeholders = ", ".join(["%s"] * len(db_codes))
        sql = f"""
            SELECT station_id, station_name, latitude, longitude, elevation, district, country_code, time_stamp
            FROM station
            WHERE country_code IN ({placeholders})
            ORDER BY time_stamp DESC;
        """
        _, rows = execute_query(sql, db_codes)

        # Deduplicate stations by station_name, prioritizing latest timestamp and name-based station_ids
        seen_names: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            stn_id = str(r["station_id"])
            stn_name = r.get("station_name") or stn_id
            if stn_name not in seen_names:
                seen_names[stn_name] = r
            else:
                # Prefer name ID over numeric ID (e.g. 'BEITBRIDGE (MET)' over '67991020')
                current_id = str(seen_names[stn_name]["station_id"])
                if current_id != stn_name and stn_id == stn_name:
                    seen_names[stn_name] = r

        stations: List[StationDataResponce] = []
        for stn_name, r in sorted(seen_names.items(), key=lambda x: x[0]):
            stn_id = str(r["station_id"])
            api_country = self.map_to_api_country_code(r.get("country_code"))
            stations.append(
                StationDataResponce(
                    station_id=stn_id,
                    station_name=stn_name,
                    latitude=_safe_float(r.get("latitude")),
                    longitude=_safe_float(r.get("longitude")),
                    elevation=_safe_float(r.get("elevation")),
                    district=r.get("district"),
                    country_code=api_country,
                    generation_timestamp=r.get("time_stamp"),
                )
            )
        return stations

    def get_station_detail(self, country: str, station_id: str) -> StationAndDefintionResponce:
        """Retrieve station metadata and climate definitions for a station."""
        sql_stn = """
            SELECT station_id, station_name, latitude, longitude, elevation, district, country_code, time_stamp
            FROM station
            WHERE station_id = %s
            ORDER BY time_stamp DESC
            LIMIT 1;
        """
        _, stn_rows = execute_query(sql_stn, [station_id])
        if not stn_rows:
            raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found.")

        r = stn_rows[0]
        stn_id = str(r["station_id"])
        stn_name = r.get("station_name") or stn_id
        api_country = self.map_to_api_country_code(r.get("country_code"))

        # Fetch definitions linked to station ordered by time_stamp DESC
        sql_defs = """
            SELECT ssm.summary_type, ssm.definition_id, ssm.time_stamp, d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s
            ORDER BY ssm.time_stamp DESC;
        """
        _, def_rows = execute_query(sql_defs, [station_id])

        # Preserve latest definition values per element
        def_map: Dict[str, Any] = {}
        ordered_def_ids: List[str] = []
        seen_def_ids = set()
        latest_gen_id: Optional[str] = None
        latest_gen_time: Optional[Any] = None

        for d in def_rows:
            did = d.get("definition_id")
            if did and did not in seen_def_ids:
                seen_def_ids.add(did)
                ordered_def_ids.append(did)
                if latest_gen_id is None:
                    latest_gen_id = did
                    latest_gen_time = d.get("time_stamp")

            val = _parse_definition_value(d.get("definition_value"))
            elem = d.get("summary_element")
            if elem and elem in StationDefinitionDataResponce.__fields__:
                if elem not in def_map:
                    def_map[elem] = val
            for k in val:
                if k in StationDefinitionDataResponce.__fields__:
                    if k not in def_map:
                        def_map[k] = val[k]

        if latest_gen_time is None:
            latest_gen_time = r.get("time_stamp")

        definition_data = StationDefinitionDataResponce.parse_obj(def_map)

        return StationAndDefintionResponce(
            station_id=stn_id,
            station_name=stn_name,
            latitude=_safe_float(r.get("latitude")),
            longitude=_safe_float(r.get("longitude")),
            elevation=_safe_float(r.get("elevation")),
            district=r.get("district"),
            country_code=api_country,
            generation_id=latest_gen_id,
            generation_timestamp=latest_gen_time,
            definitions_id=ordered_def_ids,
            climsoft_list=None,
            data=definition_data,
        )

    def get_annual_rainfall_summaries(
        self,
        country: str,
        station_id: str,
        summaries: Optional[List[str]] = None,
        trim_start: bool = True,
        trim_end: bool = True,
        generation_id: Optional[str] = None,
    ) -> AnnualRainfallSummariesResponce:
        """Query and pivot annual rainfall summaries from summary table."""
        gen_id, gen_timestamp = self.get_latest_generation_for_summary(
            station_id=station_id,
            summary_type="Annual Rain",
            generation_id=generation_id,
        )

        # 1. Fetch metadata definitions
        meta_dict: Dict[str, Any] = {}
        if gen_id:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM definition d
                WHERE d.definition_id = %s;
            """
            _, def_rows = execute_query(sql_defs, [gen_id])
            if not def_rows:
                sql_defs_fallback = """
                    SELECT d.summary_element, d.definition_value
                    FROM summary_station_metadata ssm
                    JOIN definition d ON d.definition_id = ssm.definition_id
                    WHERE ssm.station_id = %s AND ssm.summary_type = 'Annual Rain';
                """
                _, def_rows = execute_query(sql_defs_fallback, [station_id])
        else:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM summary_station_metadata ssm
                JOIN definition d ON d.definition_id = ssm.definition_id
                WHERE ssm.station_id = %s AND ssm.summary_type = 'Annual Rain';
            """
            _, def_rows = execute_query(sql_defs, [station_id])

        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            elem = d.get("summary_element")
            if elem and elem in AnnualRainfallSummariesMetadata.__fields__:
                meta_dict[elem] = val
            for k in val:
                if k in AnnualRainfallSummariesMetadata.__fields__:
                    meta_dict[k] = val[k]

        metadata = AnnualRainfallSummariesMetadata.parse_obj(meta_dict)

        # 2. Fetch annual summary data
        if gen_id:
            sql_data = """
                SELECT time_value, summary_element, summary_name, summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual'
                  AND summary_type = 'Annual Rain'
                  AND definition_id = %s
                ORDER BY time_value ASC;
            """
            _, data_rows = execute_query(sql_data, [station_id, gen_id])
        else:
            sql_data = """
                SELECT time_value, summary_element, summary_name, summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual'
                  AND summary_type = 'Annual Rain'
                ORDER BY time_value ASC;
            """
            _, data_rows = execute_query(sql_data, [station_id])

        # Pivot rows by year
        year_map: Dict[int, Dict[str, Any]] = defaultdict(dict)
        for row in data_rows:
            yr = _safe_int(row["time_value"])
            if yr is None:
                continue
            name = row.get("summary_name")
            elem = row.get("summary_element")
            val = row.get("summary_value")

            entry = year_map[yr]
            entry["station"] = station_id
            entry["year"] = yr

            field_mapping = map_annual_rain_field(elem, name, val)
            if field_mapping:
                canonical_field, parsed_val = field_mapping
                entry[canonical_field] = parsed_val

        raw_data = [data for yr, data in sorted(year_map.items())]
        trimmed_data = trim_empty_records(raw_data, trim_start=trim_start, trim_end=trim_end)
        records = [AnnualRainfallSummariesdata.parse_obj(data) for data in trimmed_data]
        return AnnualRainfallSummariesResponce(
            generation_id=gen_id,
            generation_timestamp=gen_timestamp,
            metadata=metadata,
            data=records,
        )

    def get_annual_temperature_summaries(
        self,
        country: str,
        station_id: str,
        summaries: Optional[List[str]] = None,
        trim_start: bool = True,
        trim_end: bool = True,
        generation_id: Optional[str] = None,
    ) -> AnnualTemperatureSummariesResponce:
        """Query and pivot annual temperature summaries."""
        gen_id, gen_timestamp = self.get_latest_generation_for_summary(
            station_id=station_id,
            summary_type="Annual Temperature",
            generation_id=generation_id,
        )

        # Metadata
        meta_dict: Dict[str, Any] = {}
        if gen_id:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM definition d
                WHERE d.definition_id = %s;
            """
            _, def_rows = execute_query(sql_defs, [gen_id])
            if not def_rows:
                sql_defs_fallback = """
                    SELECT d.summary_element, d.definition_value
                    FROM summary_station_metadata ssm
                    JOIN definition d ON d.definition_id = ssm.definition_id
                    WHERE ssm.station_id = %s AND ssm.summary_type = 'Annual Temperature';
                """
                _, def_rows = execute_query(sql_defs_fallback, [station_id])
        else:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM summary_station_metadata ssm
                JOIN definition d ON d.definition_id = ssm.definition_id
                WHERE ssm.station_id = %s AND ssm.summary_type = 'Annual Temperature';
            """
            _, def_rows = execute_query(sql_defs, [station_id])

        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            for k in val:
                if k in TemperatureSummariesMetadata.__fields__:
                    meta_dict[k] = val[k]
        metadata = TemperatureSummariesMetadata.parse_obj(meta_dict)

        # Data
        if gen_id:
            sql_data = """
                SELECT time_value, summary_element, summary_name, summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual'
                  AND summary_type = 'Annual Temperature'
                  AND definition_id = %s
                ORDER BY time_value ASC;
            """
            _, data_rows = execute_query(sql_data, [station_id, gen_id])
        else:
            sql_data = """
                SELECT time_value, summary_element, summary_name, summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual'
                  AND summary_type = 'Annual Temperature'
                ORDER BY time_value ASC;
            """
            _, data_rows = execute_query(sql_data, [station_id])

        year_map: Dict[int, Dict[str, Any]] = defaultdict(dict)
        for row in data_rows:
            yr = _safe_int(row["time_value"])
            if yr is None:
                continue
            name = (row.get("summary_name") or "").strip()
            elem = (row.get("summary_element") or "").strip()
            val = _safe_float(row.get("summary_value"))

            entry = year_map[yr]
            entry["station"] = station_id
            entry["year"] = yr

            if name in ("mean_TMPMIN", "mean_tmin") or elem == "tmin_mean":
                entry["mean_tmin"] = val
            elif name in ("mean_TMPMAX", "mean_tmax") or elem == "tmax_mean":
                entry["mean_tmax"] = val
            elif name in ("min_TMPMIN", "min_tmin") or elem == "tmin_min":
                entry["min_tmin"] = val
            elif name in ("min_TMPMAX", "min_tmax") or elem == "tmax_min":
                entry["min_tmax"] = val
            elif name in ("max_TMPMIN", "max_tmin") or elem == "tmin_max":
                entry["max_tmin"] = val
            elif name in ("max_TMPMAX", "max_tmax") or elem == "tmax_max":
                entry["max_tmax"] = val

        raw_data = [data for yr, data in sorted(year_map.items())]
        trimmed_data = trim_empty_records(raw_data, trim_start=trim_start, trim_end=trim_end)
        records = [AnnualTempartureSummariesdata.parse_obj(data) for data in trimmed_data]
        return AnnualTemperatureSummariesResponce(
            generation_id=gen_id,
            generation_timestamp=gen_timestamp,
            metadata=metadata,
            data=records,
        )

    def get_monthly_temperature_summaries(
        self,
        country: str,
        station_id: str,
        summaries: Optional[List[str]] = None,
        trim_start: bool = True,
        trim_end: bool = True,
        generation_id: Optional[str] = None,
    ) -> MonthlyTemperatureSummariesResponce:
        """Query and pivot monthly temperature summaries."""
        gen_id, gen_timestamp = self.get_latest_generation_for_summary(
            station_id=station_id,
            summary_type="Annual-Monthly Temperature",
            generation_id=generation_id,
        )
        if not gen_id:
            gen_id, gen_timestamp = self.get_latest_generation_for_summary(
                station_id=station_id,
                summary_type="Monthly Temperature",
                generation_id=generation_id,
            )

        # Metadata
        meta_dict: Dict[str, Any] = {}
        if gen_id:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM definition d
                WHERE d.definition_id = %s;
            """
            _, def_rows = execute_query(sql_defs, [gen_id])
            if not def_rows:
                sql_defs_fallback = """
                    SELECT d.summary_element, d.definition_value
                    FROM summary_station_metadata ssm
                    JOIN definition d ON d.definition_id = ssm.definition_id
                    WHERE ssm.station_id = %s AND ssm.summary_type IN ('Annual-Monthly Temperature', 'Monthly Temperature');
                """
                _, def_rows = execute_query(sql_defs_fallback, [station_id])
        else:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM summary_station_metadata ssm
                JOIN definition d ON d.definition_id = ssm.definition_id
                WHERE ssm.station_id = %s AND ssm.summary_type IN ('Annual-Monthly Temperature', 'Monthly Temperature');
            """
            _, def_rows = execute_query(sql_defs, [station_id])

        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            for k in val:
                if k in TemperatureSummariesMetadata.__fields__:
                    meta_dict[k] = val[k]
        metadata = TemperatureSummariesMetadata.parse_obj(meta_dict)

        # Data: annual-monthly rows
        if gen_id:
            sql_data = """
                SELECT time_value, summary_element, summary_name, summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual-monthly'
                  AND summary_type IN ('Annual-Monthly Temperature', 'Monthly Temperature')
                  AND definition_id = %s
                ORDER BY time_value ASC;
            """
            _, data_rows = execute_query(sql_data, [station_id, gen_id])
        else:
            sql_data = """
                SELECT time_value, summary_element, summary_name, summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual-monthly'
                  AND summary_type IN ('Annual-Monthly Temperature', 'Monthly Temperature')
                ORDER BY time_value ASC;
            """
            _, data_rows = execute_query(sql_data, [station_id])

        month_map: Dict[tuple, Dict[str, Any]] = defaultdict(dict)
        for row in data_rows:
            t_val = str(row.get("time_value") or "").strip()
            # e.g. "1951-Jul"
            parts = t_val.split("-")
            if len(parts) != 2:
                continue
            yr = _safe_int(parts[0])
            m_str = parts[1].lower()
            month_num = MONTH_NAME_TO_INT.get(m_str)
            if yr is None or month_num is None:
                continue

            name = (row.get("summary_name") or "").strip()
            elem = (row.get("summary_element") or "").strip()
            val = _safe_float(row.get("summary_value"))

            key = (yr, month_num)
            entry = month_map[key]
            entry["station"] = station_id
            entry["year"] = yr
            entry["month"] = month_num

            if name in ("mean_TMPMIN", "mean_tmin") or elem == "tmin_mean":
                entry["mean_tmin"] = val
            elif name in ("mean_TMPMAX", "mean_tmax") or elem == "tmax_mean":
                entry["mean_tmax"] = val
            elif name in ("min_TMPMIN", "min_tmin") or elem == "tmin_min":
                entry["min_tmin"] = val
            elif name in ("min_TMPMAX", "min_tmax") or elem == "tmax_min":
                entry["min_tmax"] = val
            elif name in ("max_TMPMIN", "max_tmin") or elem == "tmin_max":
                entry["max_tmin"] = val
            elif name in ("max_TMPMAX", "max_tmax") or elem == "tmax_max":
                entry["max_tmax"] = val

        raw_data = [data for k, data in sorted(month_map.items())]
        trimmed_data = trim_empty_records(raw_data, trim_start=trim_start, trim_end=trim_end)
        records = [MonthlyTempartureSummariesdata.parse_obj(data) for data in trimmed_data]
        return MonthlyTemperatureSummariesResponce(
            generation_id=gen_id,
            generation_timestamp=gen_timestamp,
            metadata=metadata,
            data=records,
        )

    def get_crop_success_probabilities(
        self,
        country: str,
        station_id: str,
        generation_id: Optional[str] = None,
    ) -> CropSuccessProbabilitiesResponce:
        """Query and aggregate full crop success probabilities lookup table from crop table using SQL aggregation."""
        gen_id, gen_timestamp = self.get_latest_generation_for_crop(
            station_id=station_id,
            generation_id=generation_id,
        )

        # Metadata
        meta_dict: Dict[str, Any] = {}
        if gen_id:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM definition d
                WHERE d.definition_id = %s;
            """
            _, def_rows = execute_query(sql_defs, [gen_id])
            if not def_rows:
                sql_defs_fallback = """
                    SELECT d.summary_element, d.definition_value
                    FROM summary_station_metadata ssm
                    JOIN definition d ON d.definition_id = ssm.definition_id
                    WHERE ssm.station_id = %s AND ssm.summary_type = 'Crops';
                """
                _, def_rows = execute_query(sql_defs_fallback, [station_id])
        else:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM summary_station_metadata ssm
                JOIN definition d ON d.definition_id = ssm.definition_id
                WHERE ssm.station_id = %s AND ssm.summary_type = 'Crops';
            """
            _, def_rows = execute_query(sql_defs, [station_id])

        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            elem = d.get("summary_element")
            if elem and elem in CropSuccessProbabilitiesMetadata.__fields__:
                meta_dict[elem] = val
            for k in val:
                if k in CropSuccessProbabilitiesMetadata.__fields__:
                    meta_dict[k] = val[k]
        metadata = CropSuccessProbabilitiesMetadata.parse_obj(meta_dict)

        # Full lookup table aggregation query
        if gen_id:
            sql_crop = """
                SELECT
                  CAST(rain_total AS INTEGER) AS total_rain,
                  CAST(plant_day AS INTEGER) AS plant_day,
                  CAST(plant_length AS INTEGER) AS plant_length,
                  COUNT(year) AS year_count,
                  MAX(CASE WHEN year IS NULL AND include_start_condition IS TRUE THEN CAST(summary_value AS FLOAT) ELSE NULL END) AS precomp_with_start,
                  MAX(CASE WHEN year IS NULL AND include_start_condition IS NOT TRUE THEN CAST(summary_value AS FLOAT) ELSE NULL END) AS precomp_no_start,
                  SUM(CASE WHEN include_start_condition IS TRUE THEN 1 ELSE 0 END) AS with_start_total,
                  SUM(CASE WHEN include_start_condition IS TRUE AND UPPER(TRIM(summary_value)) IN ('TRUE', '1') THEN 1 ELSE 0 END) AS with_start_success,
                  SUM(CASE WHEN include_start_condition IS NOT TRUE THEN 1 ELSE 0 END) AS no_start_total,
                  SUM(CASE WHEN include_start_condition IS NOT TRUE AND UPPER(TRIM(summary_value)) IN ('TRUE', '1') THEN 1 ELSE 0 END) AS no_start_success
                FROM crop
                WHERE station_id = %s
                  AND definition_id = %s
                  AND rain_total IS NOT NULL
                  AND plant_day IS NOT NULL
                  AND plant_length IS NOT NULL
                GROUP BY plant_day, plant_length, rain_total
                ORDER BY plant_day, plant_length, rain_total;
            """
            _, rows = execute_query(sql_crop, [station_id, gen_id])
        else:
            sql_crop = """
                SELECT
                  CAST(rain_total AS INTEGER) AS total_rain,
                  CAST(plant_day AS INTEGER) AS plant_day,
                  CAST(plant_length AS INTEGER) AS plant_length,
                  COUNT(year) AS year_count,
                  MAX(CASE WHEN year IS NULL AND include_start_condition IS TRUE THEN CAST(summary_value AS FLOAT) ELSE NULL END) AS precomp_with_start,
                  MAX(CASE WHEN year IS NULL AND include_start_condition IS NOT TRUE THEN CAST(summary_value AS FLOAT) ELSE NULL END) AS precomp_no_start,
                  SUM(CASE WHEN include_start_condition IS TRUE THEN 1 ELSE 0 END) AS with_start_total,
                  SUM(CASE WHEN include_start_condition IS TRUE AND UPPER(TRIM(summary_value)) IN ('TRUE', '1') THEN 1 ELSE 0 END) AS with_start_success,
                  SUM(CASE WHEN include_start_condition IS NOT TRUE THEN 1 ELSE 0 END) AS no_start_total,
                  SUM(CASE WHEN include_start_condition IS NOT TRUE AND UPPER(TRIM(summary_value)) IN ('TRUE', '1') THEN 1 ELSE 0 END) AS no_start_success
                FROM crop
                WHERE station_id = %s
                  AND rain_total IS NOT NULL
                  AND plant_day IS NOT NULL
                  AND plant_length IS NOT NULL
                GROUP BY plant_day, plant_length, rain_total
                ORDER BY plant_day, plant_length, rain_total;
            """
            _, rows = execute_query(sql_crop, [station_id])

        records: List[CropSuccessProbabilitiesdata] = []
        for r in rows:
            year_count = _safe_int(r.get("year_count")) or 0
            if year_count == 0:
                p_with = _safe_float(r.get("precomp_with_start")) or 0.0
                p_no = _safe_float(r.get("precomp_no_start")) or 0.0
            else:
                w_tot = _safe_int(r["with_start_total"]) or 0
                w_suc = _safe_int(r["with_start_success"]) or 0
                n_tot = _safe_int(r["no_start_total"]) or 0
                n_suc = _safe_int(r["no_start_success"]) or 0

                p_with = (w_suc / w_tot) if w_tot > 0 else 0.0
                p_no = (n_suc / n_tot) if n_tot > 0 else 0.0

            records.append(
                CropSuccessProbabilitiesdata(
                    station=station_id,
                    total_rain=_safe_int(r["total_rain"]),
                    plant_day=_safe_int(r["plant_day"]),
                    plant_length=_safe_int(r["plant_length"]),
                    prop_success_with_start=round(p_with, 4),
                    prop_success_no_start=round(p_no, 4),
                )
            )

        return CropSuccessProbabilitiesResponce(
            generation_id=gen_id,
            generation_timestamp=gen_timestamp,
            metadata=metadata,
            data=records,
        )

    def get_season_start_probabilities(
        self,
        country: str,
        station_id: str,
        start_dates: Optional[List[int]] = None,
        generation_id: Optional[str] = None,
    ) -> SeasonStartProbabilitiesResponce:
        """Query and compute cumulative season start probabilities across candidate days."""
        if start_dates is None or len(start_dates) == 0:
            start_dates = [200, 220, 250, 270, 300, 320]

        gen_id, gen_timestamp = self.get_latest_generation_for_summary(
            station_id=station_id,
            summary_type="Annual Rain",
            generation_id=generation_id,
        )

        # Metadata
        meta_dict: Dict[str, Any] = {}
        if gen_id:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM definition d
                WHERE d.definition_id = %s;
            """
            _, def_rows = execute_query(sql_defs, [gen_id])
            if not def_rows:
                sql_defs_fallback = """
                    SELECT d.summary_element, d.definition_value
                    FROM summary_station_metadata ssm
                    JOIN definition d ON d.definition_id = ssm.definition_id
                    WHERE ssm.station_id = %s;
                """
                _, def_rows = execute_query(sql_defs_fallback, [station_id])
        else:
            sql_defs = """
                SELECT d.summary_element, d.definition_value
                FROM summary_station_metadata ssm
                JOIN definition d ON d.definition_id = ssm.definition_id
                WHERE ssm.station_id = %s;
            """
            _, def_rows = execute_query(sql_defs, [station_id])

        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            elem = d.get("summary_element")
            if elem and elem in SeasonStartProbabilitiesMetadata.__fields__:
                meta_dict[elem] = val
        metadata = SeasonStartProbabilitiesMetadata.parse_obj(meta_dict)

        # Query all annual start_rains DOYs
        if gen_id:
            sql_data = """
                SELECT summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual'
                  AND summary_type = 'Annual Rain'
                  AND definition_id = %s
                  AND summary_name IN ('start_rains', 'start')
                  AND summary_value IS NOT NULL
                  AND summary_value != '';
            """
            _, rows = execute_query(sql_data, [station_id, gen_id])
        else:
            sql_data = """
                SELECT summary_value
                FROM summary
                WHERE station_id = %s
                  AND time_type = 'annual'
                  AND summary_name IN ('start_rains', 'start')
                  AND summary_value IS NOT NULL
                  AND summary_value != '';
            """
            _, rows = execute_query(sql_data, [station_id])

        start_doys = [_safe_float(r["summary_value"]) for r in rows if _safe_float(r["summary_value"]) is not None]

        records: List[SeasonStartProbabilitiesdata] = []
        total_years = len(start_doys)
        for day in start_dates:
            if total_years > 0:
                prop = sum(1 for doy in start_doys if doy <= day) / total_years
            else:
                prop = 0.0
            records.append(
                SeasonStartProbabilitiesdata(
                    station=station_id,
                    day=day,
                    proportion=round(prop, 4),
                )
            )

        return SeasonStartProbabilitiesResponce(
            generation_id=gen_id,
            generation_timestamp=gen_timestamp,
            metadata=metadata,
            data=records,
        )


# Global singleton instance & dependency injection helper
_climate_repository = ClimateRepository()


def get_climate_repository() -> ClimateRepository:
    return _climate_repository
