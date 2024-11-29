"""Testing file for the load_sensor_data.py script."""
import pytest
import pandas as pd
from datetime import datetime
from io import StringIO
from pipeline.etl_process.load_sensor_data import clean_and_prepare_sensor_data, filter_valid_sensor_data

CSV_CONTENT = """
plant_id,recording_taken,soil_moisture,temperature,last_watered
1,2023-11-01 08:00:00,23.5,15.8,2023-10-31 08:00:00
2,invalid_date,20.0,16.2,2023-10-30 08:00:00
3,2023-11-01 09:00:00,25.0,17.0,invalid_date
"""


def create_sample_dataframe():
    return pd.read_csv(StringIO(CSV_CONTENT))


def test_clean_and_prepare_sensor_data(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(CSV_CONTENT)
    cleaned_df = clean_and_prepare_sensor_data(str(csv_file))
    assert len(cleaned_df) == 1
    assert cleaned_df.iloc[0]["plant_id"] == 1
    assert isinstance(cleaned_df.iloc[0]["recording_taken"], datetime)
    assert isinstance(cleaned_df.iloc[0]["last_watered"], datetime)


def test_filter_valid_sensor_data():
    df = create_sample_dataframe()
    valid_plant_ids = {1, 3}
    filtered_df = filter_valid_sensor_data(df, valid_plant_ids)
    assert len(filtered_df) == 2
    assert set(filtered_df["plant_id"]) == {1, 3}
