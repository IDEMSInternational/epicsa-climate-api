import pytest
from pydantic import BaseModel
from typing import Optional

from app.utils.data import is_empty_record, trim_empty_records


class SampleModel(BaseModel):
    station: str
    year: int
    val1: Optional[float] = None
    val2: Optional[int] = None
    val3: Optional[bool] = None


def test_is_empty_record():
    # Empty dict
    assert is_empty_record({"station": "stn1", "year": 1909}) is True
    assert is_empty_record({"station": "stn1", "year": 1909, "val1": None}) is True

    # Non-empty dict
    assert is_empty_record({"station": "stn1", "year": 1909, "val1": 0.0}) is False
    assert is_empty_record({"station": "stn1", "year": 1909, "val2": 0}) is False
    assert is_empty_record({"station": "stn1", "year": 1909, "val3": False}) is False

    # Empty Pydantic model
    assert is_empty_record(SampleModel(station="stn1", year=1909)) is True
    assert is_empty_record(SampleModel(station="stn1", year=1909, val1=None)) is True

    # Non-empty Pydantic model
    assert is_empty_record(SampleModel(station="stn1", year=1909, val1=12.5)) is False
    assert is_empty_record(SampleModel(station="stn1", year=1909, val3=False)) is False


def test_trim_empty_records_both():
    records = [
        {"station": "A", "year": 1909, "rain": None},
        {"station": "A", "year": 1910, "rain": None},
        {"station": "A", "year": 1965, "rain": 296.4},
        {"station": "A", "year": 1979, "rain": None},  # internal gap year
        {"station": "A", "year": 1980, "rain": 310.0},
        {"station": "A", "year": 2026, "rain": None},
    ]

    trimmed = trim_empty_records(records, trim_start=True, trim_end=True)
    assert [r["year"] for r in trimmed] == [1965, 1979, 1980]
    # Check that internal gap year is preserved
    assert trimmed[1]["year"] == 1979
    assert trimmed[1]["rain"] is None


def test_trim_empty_records_start_only():
    records = [
        {"station": "A", "year": 1909, "rain": None},
        {"station": "A", "year": 1965, "rain": 296.4},
        {"station": "A", "year": 2026, "rain": None},
    ]

    trimmed = trim_empty_records(records, trim_start=True, trim_end=False)
    assert [r["year"] for r in trimmed] == [1965, 2026]


def test_trim_empty_records_end_only():
    records = [
        {"station": "A", "year": 1909, "rain": None},
        {"station": "A", "year": 1965, "rain": 296.4},
        {"station": "A", "year": 2026, "rain": None},
    ]

    trimmed = trim_empty_records(records, trim_start=False, trim_end=True)
    assert [r["year"] for r in trimmed] == [1909, 1965]


def test_trim_empty_records_neither():
    records = [
        {"station": "A", "year": 1909, "rain": None},
        {"station": "A", "year": 1965, "rain": 296.4},
        {"station": "A", "year": 2026, "rain": None},
    ]

    trimmed = trim_empty_records(records, trim_start=False, trim_end=False)
    assert [r["year"] for r in trimmed] == [1909, 1965, 2026]


def test_trim_empty_records_all_empty():
    records = [
        {"station": "A", "year": 1909, "rain": None},
        {"station": "A", "year": 1910, "rain": None},
    ]

    assert trim_empty_records(records, trim_start=True, trim_end=True) == []
    assert trim_empty_records(records, trim_start=True, trim_end=False) == []
    # If not trimming from start, end scan finds nothing non-empty
    assert len(trim_empty_records(records, trim_start=False, trim_end=False)) == 2


def test_trim_empty_records_empty_input():
    assert trim_empty_records([]) == []


def test_trim_empty_records_with_pydantic_models():
    models = [
        SampleModel(station="A", year=1909),
        SampleModel(station="A", year=1965, val1=100.0),
        SampleModel(station="A", year=1979),
        SampleModel(station="A", year=1980, val3=False),
        SampleModel(station="A", year=2026),
    ]

    trimmed = trim_empty_records(models, trim_start=True, trim_end=True)
    assert [m.year for m in trimmed] == [1965, 1979, 1980]
    assert trimmed[1].val1 is None
    assert trimmed[2].val3 is False
