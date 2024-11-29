import pytest
import os
from pipeline.etl_process.extract import fetch_plant_data, get_all_keys, fetch_all_plants, export_to_csv


def test_plants_fetch_data():
    plant_id = 1
    result = fetch_plant_data(plant_id)
    assert result is not None, "API returned no data."
    assert "plant_name" in result, "Key 'plant_name' missing in result."
    assert "botanist_email" in result, "Key 'botanist_email' missing in result."


def test_get_all_keys():
    data = [
        {"plant_id": 1, "plant_name": "Rose", "country_name": "USA"},
        {"plant_id": 2, "plant_name": "Tulip"}
    ]
    keys = get_all_keys(data)
    assert set(keys) == {"plant_id", "plant_name", "country_name"}


def test_fetch_all_plants():
    result = fetch_all_plants(start_id=1, end_id=5)
    assert len(result) > 0, "No plants fetched."
    assert "plant_name" in result[0], "Key 'plant_name' missing in results."


def test_export_to_csv(tmp_path):
    data = fetch_all_plants(start_id=1, end_id=3)
    output_file = tmp_path / "plants_data.csv"
    export_to_csv(data, output_file)
    assert os.path.exists(output_file), "CSV file was not created."
    with open(output_file, "r") as f:
        content = f.read()
        assert "plant_id,plant_name" in content, "CSV headers are incorrect."
        assert len(content.splitlines()) > 1, "CSV content is missing."
