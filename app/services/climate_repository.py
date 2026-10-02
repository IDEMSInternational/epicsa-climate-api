import json
from typing import Any, Dict, List, Optional
from collections import defaultdict
from fastapi import HTTPException

from app.core.database import execute_query
from app.definitions import country_code
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

    def get_stations_by_country(self, country: str) -> List[StationDataResponce]:
        """Retrieve list of stations for a given country code."""
        db_codes = self.normalize_country_codes(country)
        placeholders = ", ".join(["%s"] * len(db_codes))
        sql = f"""
            SELECT DISTINCT station_id, station_name, latitude, longitude, elevation, district, country_code
            FROM station
            WHERE country_code IN ({placeholders})
            ORDER BY station_name ASC;
        """
        _, rows = execute_query(sql, db_codes)

        # Deduplicate stations by station_name, prioritizing name-based station_ids
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
                )
            )
        return stations

    def get_station_detail(self, country: str, station_id: str) -> StationAndDefintionResponce:
        """Retrieve station metadata and climate definitions for a station."""
        sql_stn = """
            SELECT station_id, station_name, latitude, longitude, elevation, district, country_code
            FROM station
            WHERE station_id = %s
            LIMIT 1;
        """
        _, stn_rows = execute_query(sql_stn, [station_id])
        if not stn_rows:
            raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found.")

        r = stn_rows[0]
        stn_id = str(r["station_id"])
        stn_name = r.get("station_name") or stn_id
        api_country = self.map_to_api_country_code(r.get("country_code"))

        # Fetch definitions linked to station
        sql_defs = """
            SELECT ssm.summary_type, d.definition_id, d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s;
        """
        _, def_rows = execute_query(sql_defs, [station_id])

        def_ids: List[str] = list(set(row["definition_id"] for row in def_rows if row.get("definition_id")))

        # Map definition objects
        def_map: Dict[str, Any] = {}
        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            elem = d.get("summary_element")
            if elem and elem in StationDefinitionDataResponce.__fields__:
                def_map[elem] = val
            for k in val:
                if k in StationDefinitionDataResponce.__fields__:
                    def_map[k] = val[k]

        definition_data = StationDefinitionDataResponce.parse_obj(def_map)

        return StationAndDefintionResponce(
            station_id=stn_id,
            station_name=stn_name,
            latitude=_safe_float(r.get("latitude")),
            longitude=_safe_float(r.get("longitude")),
            elevation=_safe_float(r.get("elevation")),
            district=r.get("district"),
            country_code=api_country,
            definitions_id=def_ids,
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
    ) -> AnnualRainfallSummariesResponce:
        """Query and pivot annual rainfall summaries from summary table."""
        # 1. Fetch metadata definitions
        sql_defs = """
            SELECT d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s AND ssm.summary_type = 'Annual Rain';
        """
        _, def_rows = execute_query(sql_defs, [station_id])
        meta_dict: Dict[str, Any] = {}
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
            name = (row.get("summary_name") or "").strip()
            elem = (row.get("summary_element") or "").strip()
            val = row.get("summary_value")

            entry = year_map[yr]
            entry["station"] = station_id
            entry["year"] = yr

            if elem == "total_rain" or name in ("annual_rain", "total_rain", "Oct_Apr_PRECIP", "seasonal_PRECIP"):
                entry["annual_rain"] = _safe_float(val)
            elif elem == "rain_day" or name in ("n_rain", "Oct_Apr_rainday", "annual_rainday"):
                entry["n_rain"] = _safe_int(val)
            elif elem == "start_rain" or name in ("start_rains", "start"):
                entry["start_rains_doy"] = _safe_int(val)
            elif elem == "start_rain_date" or name in ("start_rains_date", "start_d"):
                entry["start_rains_date"] = str(val) if val else None
            elif elem == "start_rain_status" or name in ("start_rains_status", "start_s"):
                entry["start_rains_status"] = _safe_bool(val)
            elif elem == "end_rain" or name == "end_rains":
                entry["end_rains_doy"] = _safe_int(val)
            elif elem == "end_rain_date" or name == "end_rains_date":
                entry["end_rains_date"] = str(val) if val else None
            elif elem == "end_rain_status" or name == "end_rains_status":
                entry["end_rains_status"] = _safe_bool(val)
            elif elem == "end_season" or name == "end_season":
                entry["end_season_doy"] = _safe_int(val)
            elif elem == "end_season_date" or name == "end_season_date":
                entry["end_season_date"] = str(val) if val else None
            elif elem == "end_season_status" or name == "end_season_status":
                entry["end_season_status"] = _safe_bool(val)
            elif elem == "seasonal_total_rain" or name in ("seasonal_PRECIP", "seasonal_rain"):
                entry["seasonal_rain"] = _safe_int(val)
            elif elem == "seasonal_rain_day" or name in ("seasonal_rainday", "n_seasonal_rain"):
                entry["n_seasonal_rain"] = _safe_int(val)
            elif elem == "season_length" or name in ("length_rains", "length_season", "season_length"):
                entry["season_length"] = _safe_float(val)

        raw_data = [data for yr, data in sorted(year_map.items())]
        trimmed_data = trim_empty_records(raw_data, trim_start=trim_start, trim_end=trim_end)
        records = [AnnualRainfallSummariesdata.parse_obj(data) for data in trimmed_data]
        return AnnualRainfallSummariesResponce(metadata=metadata, data=records)

    def get_annual_temperature_summaries(
        self,
        country: str,
        station_id: str,
        summaries: Optional[List[str]] = None,
        trim_start: bool = True,
        trim_end: bool = True,
    ) -> AnnualTemperatureSummariesResponce:
        """Query and pivot annual temperature summaries."""
        # Metadata
        sql_defs = """
            SELECT d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s AND ssm.summary_type = 'Annual Temperature';
        """
        _, def_rows = execute_query(sql_defs, [station_id])
        meta_dict: Dict[str, Any] = {}
        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            for k in val:
                if k in TemperatureSummariesMetadata.__fields__:
                    meta_dict[k] = val[k]
        metadata = TemperatureSummariesMetadata.parse_obj(meta_dict)

        # Data
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
        return AnnualTemperatureSummariesResponce(metadata=metadata, data=records)

    def get_monthly_temperature_summaries(
        self,
        country: str,
        station_id: str,
        summaries: Optional[List[str]] = None,
        trim_start: bool = True,
        trim_end: bool = True,
    ) -> MonthlyTemperatureSummariesResponce:
        """Query and pivot monthly temperature summaries."""
        # Metadata
        sql_defs = """
            SELECT d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s AND ssm.summary_type IN ('Annual-Monthly Temperature', 'Monthly Temperature');
        """
        _, def_rows = execute_query(sql_defs, [station_id])
        meta_dict: Dict[str, Any] = {}
        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            for k in val:
                if k in TemperatureSummariesMetadata.__fields__:
                    meta_dict[k] = val[k]
        metadata = TemperatureSummariesMetadata.parse_obj(meta_dict)

        # Data: annual-monthly rows
        sql_data = """
            SELECT time_value, summary_element, summary_name, summary_value
            FROM summary
            WHERE station_id = %s
              AND time_type = 'annual-monthly'
              AND summary_type = 'Annual-Monthly Temperature'
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
        return MonthlyTemperatureSummariesResponce(metadata=metadata, data=records)

    def get_crop_success_probabilities(
        self,
        country: str,
        station_id: str,
    ) -> CropSuccessProbabilitiesResponce:
        """Query and aggregate full crop success probabilities lookup table from crop table using SQL aggregation."""
        # Metadata
        sql_defs = """
            SELECT d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s AND ssm.summary_type = 'Crops';
        """
        _, def_rows = execute_query(sql_defs, [station_id])
        meta_dict: Dict[str, Any] = {}
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
        sql_crop = """
            SELECT
              CAST(rain_total AS INTEGER) AS total_rain,
              CAST(plant_day AS INTEGER) AS plant_day,
              CAST(plant_length AS INTEGER) AS plant_length,
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

        return CropSuccessProbabilitiesResponce(metadata=metadata, data=records)

    def get_season_start_probabilities(
        self,
        country: str,
        station_id: str,
        start_dates: Optional[List[int]] = None,
    ) -> SeasonStartProbabilitiesResponce:
        """Query and compute cumulative season start probabilities across candidate days."""
        if start_dates is None or len(start_dates) == 0:
            start_dates = [200, 220, 250, 270, 300, 320]

        # Metadata
        sql_defs = """
            SELECT d.summary_element, d.definition_value
            FROM summary_station_metadata ssm
            JOIN definition d ON d.definition_id = ssm.definition_id
            WHERE ssm.station_id = %s;
        """
        _, def_rows = execute_query(sql_defs, [station_id])
        meta_dict: Dict[str, Any] = {}
        for d in def_rows:
            val = _parse_definition_value(d.get("definition_value"))
            elem = d.get("summary_element")
            if elem and elem in SeasonStartProbabilitiesMetadata.__fields__:
                meta_dict[elem] = val
        metadata = SeasonStartProbabilitiesMetadata.parse_obj(meta_dict)

        # Query all annual start_rains DOYs
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

        return SeasonStartProbabilitiesResponce(metadata=metadata, data=records)


# Global singleton instance & dependency injection helper
_climate_repository = ClimateRepository()


def get_climate_repository() -> ClimateRepository:
    return _climate_repository
