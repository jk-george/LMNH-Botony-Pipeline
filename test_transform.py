"""Test file for the transform.py pipeline script."""
import pytest
import pandas as pd
from io import StringIO

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

def test_drop_missing_data():
    """Test if rows with missing fields are removed."""
    data = [
        {"plant_name": "Rose", "scientific_name": "Rosa indica", "last_watered": "2024-01-01", "soil_moisture": 50, "temperature": 25, "origin_location": "India"},
        {"plant_name": "", "scientific_name": "Rosa alba", "soil_moisture": 45, "temperature": 20, "origin_location": "Pakistan"}
    ]
    df = pd.DataFrame(data)
    cleaned_df = drop_missing_data(df)
    assert cleaned_df.shape == (1, 6)
    assert cleaned_df['plant_name'].iloc[0] == 'Rose'

def test_set_numeric_limits():
    """Test if rows outside the numeric limits are filtered out."""
    data = StringIO(
        "name,scientific_name,last_watered,soil_moisture,temperature,origin_location\n"
        "Rose,Rosa indica,2024-01-01,50,25,India\n"
        "Tulip,Tulipa gesneriana,2024-01-01,120,25,Netherlands\n"
        "Cactus,Cactaceae,2024-01-01,50,-20,USA\n"
    )
    df = pd.read_csv(data)
    filtered_df = set_numeric_limits(df)
    assert filtered_df.shape == (1, 6)
    assert filtered_df['name'].iloc[0] == 'Rose'

def test_clean_text_fields():
    """Test if unnecessary whitespace is removed from text."""
    data = StringIO(
        "name,scientific_name,last_watered,soil_moisture,temperature,origin_location\n"
        " Rose , Rosa indica , 2024-01-01,50,25, India \n"
    )
    df = pd.read_csv(data)
    cleaned_df = clean_text_fields(df, ['name', 'scientific_name', 'origin_location'])
    assert cleaned_df['name'].iloc[0] == 'Rose'
    assert cleaned_df['scientific_name'].iloc[0] == 'Rosa indica'
    assert cleaned_df['origin_location'].iloc[0] == 'India'

def test_convert_dates():
    """Test if 'last_watered' is correctly converted to datetime and invalid rows are dropped."""
    data = StringIO(
        "name,scientific_name,last_watered,soil_moisture,temperature,origin_location\n"
        "Rose,Rosa indica,2024-01-01,50,25,India\n"
        "Tulip,Tulipa gesneriana,invalid_date,45,20,Netherlands\n"
    )
    df = pd.read_csv(data)
    converted_df = convert_dates(df)
    assert converted_df.shape == (1, 6)
    assert pd.api.types.is_datetime64_any_dtype(converted_df['last_watered'])

def test_filter_invalid_location():
    """Test if rows with empty origin_location are filtered out."""
    data = StringIO(
        "name,scientific_name,last_watered,soil_moisture,temperature,country_name\n"
        "Rose,Rosa indica,2024-01-01,50,25,India\n"
        "Tulip,Tulipa gesneriana,2024-01-01,45,20,\n"
    )
    df = pd.read_csv(data)
    filtered_df = filter_invalid_location(df)
    assert filtered_df.shape == (1, 6)
    assert filtered_df['name'].iloc[0] == 'Rose'

def test_save_data(tmp_path):
    """Test if the save_data function writes the DataFrame to a CSV file correctly."""
    data = pd.DataFrame({
        "name": ["Rose"],
        "scientific_name": ["Rosa indica"],
        "last_watered": ["2024-01-01"],
        "soil_moisture": [50],
        "temperature": [25],
        "origin_location": ["India"]
    })
    output_file = tmp_path / "test_output.csv"
    save_data(data, str(output_file))

    saved_data = pd.read_csv(output_file)
    assert saved_data.shape == (1, 6)
    assert saved_data.loc[0, 'name'] == 'Rose'