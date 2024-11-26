"""Test file for the transform.py pipeline script."""
import pytest
import pandas as pd

from transform import (
    load_data,
    drop_missing_data,
    set_numeric_limits,
    clean_text_fields,
    convert_dates,
    filter_invalid_location,
    save_data
)

def test_load_data()