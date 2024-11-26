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

def test_load_data(tmp_path):
    """Test if the load_data function loads a CSV correctly."""
    test_csv = "name,scientific_name,last_watered,soil_moisture,temperature,origin_location\n" \
               "Rose,Rosa indica,2024-01-01,50,25,India\n"
    input_file = tmp_path / "test_input.csv"
    input_file.write_text(test_csv)

    df = load_data(str(input_file))
    assert df.shape == (1, 6)
    assert df.loc[0, 'name'] == 'Rose'

