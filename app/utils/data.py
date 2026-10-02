from typing import Any, Callable, Dict, List, Optional, Sequence, TypeVar, Union

T = TypeVar("T")

DEFAULT_IGNORE_KEYS: Sequence[str] = (
    "station",
    "station_name",
    "station_id",
    "year",
    "month",
    "country",
    "country_code",
)


def is_empty_record(
    record: Union[Dict[str, Any], Any],
    ignore_keys: Sequence[str] = DEFAULT_IGNORE_KEYS,
) -> bool:
    """Check if a record has no data measurements (all non-ignored fields are None).

    Args:
        record: A dict, Pydantic model, or object with attributes.
        ignore_keys: Keys/attributes to ignore when evaluating data emptiness (metadata/identifiers).

    Returns:
        True if all measurement fields are None (or absent), False if at least one measurement is present.
    """
    if isinstance(record, dict):
        d = record
    elif hasattr(record, "dict") and callable(record.dict):
        d = record.dict()
    elif hasattr(record, "__dict__"):
        d = record.__dict__
    else:
        return False

    return all(v is None for k, v in d.items() if k not in ignore_keys)


def trim_empty_records(
    records: List[T],
    trim_start: bool = True,
    trim_end: bool = True,
    ignore_keys: Sequence[str] = DEFAULT_IGNORE_KEYS,
    is_empty: Optional[Callable[[T], bool]] = None,
) -> List[T]:
    """Trim empty data records from the start and/or end of a sequential record list.

    An empty record is defined as having all non-ignored fields equal to None
    (or satisfying the custom `is_empty` predicate).
    Internal empty/null records (gaps) occurring between non-empty records are preserved.

    Args:
        records: List of records (dicts, Pydantic models, or objects).
        trim_start: Whether to trim empty records from the start (default: True).
        trim_end: Whether to trim empty records from the end (default: True).
        ignore_keys: Keys to ignore when checking if a record is empty (default: station, year, month, etc.).
        is_empty: Optional custom predicate returning True if a record is empty.

    Returns:
        A new trimmed list of records.
    """
    if not records:
        return []

    predicate = is_empty or (lambda r: is_empty_record(r, ignore_keys=ignore_keys))

    # Find first non-empty index
    first_non_empty = 0
    if trim_start:
        while first_non_empty < len(records) and predicate(records[first_non_empty]):
            first_non_empty += 1

    # If all records are empty and we trimmed from start, return empty list
    if first_non_empty >= len(records):
        return []

    # Find last non-empty index
    last_non_empty = len(records)
    if trim_end:
        while last_non_empty > first_non_empty and predicate(records[last_non_empty - 1]):
            last_non_empty -= 1

    return records[first_non_empty:last_non_empty]
