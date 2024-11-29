import pytest
import os
from unittest.mock import patch
from email_sender import get_config, read_csv, check_and_alert_unhealthy_plants


@patch.dict('os.environ', {}, clear=True)
def test_get_config_missing_values():
    config = get_config()
    assert config.get('aws_region') is None
    assert config.get('ses_sender_email') is None
    assert config.get('csv_file_path') is None

@patch.dict('os.environ', {
         'AWS_REGION': 'eu-west-2',
         'SES_SENDER_EMAIL': 'trainee.emily.curtis@sigmalabs.co.uk|trainee.emily.curtis@sigmalabs.co.uk',
         'FILE_PATH': 'plants_data_cleaned.csv'
     })
def test_get_config():
    config = get_config()
    assert config['aws_region'] == 'eu-west-2'
    assert config['ses_sender_email'] == 'trainee.emily.curtis@sigmalabs.co.uk|trainee.emily.curtis@sigmalabs.co.uk'
    assert config['csv_file_path'] == 'plants_data_cleaned.csv'

def test_read_csv(tmp_path):
    csv_content = (
        "plant_name,botanist_forename,botanist_surname,soil_moisture,temperature\n"
        "Rose,Jane,Doe,60,10\n"
        "Cactus,John,Smith,40,25\n"
    )
    file_path = tmp_path / "plants_data.csv"
    file_path.write_text(csv_content)
    data = read_csv(str(file_path))
    assert len(data) == 2
    assert data[0]['plant_name'] == 'Rose'
    assert data[1]['botanist_surname'] == 'Smith'
    assert float(data[0]['soil_moisture']) == 60

