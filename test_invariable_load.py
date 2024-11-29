import pandas as pd
import pytest
from unittest.mock import MagicMock
from invariable_load import load_plant_species, load_countries, load_botanists, load_plants

@pytest.fixture
def mock_cursor():
    return MagicMock()

@pytest.fixture
def mock_data():
    data = {
        'scientific_name': ['Plantus exampleus', 'Plantus exampleuss'],
        'plant_name': ['Example Plant', 'Example Plantt'],
        'country_name': ['Exampleland', 'Anotherlandd'],
        'botanist_email': ['example@botany.com', 'another@botany.com'],
        'botanist_forename': ['Alice', 'Bob'],
        'botanist_surname': ['Example', 'Another'],
        'botanist_phone': ['1234567890', '0987654321'],
        'plant_id': ['P1', 'P2'],
    }
    return pd.DataFrame(data)

def test_load_plant_species(mock_cursor, mock_data):
    load_plant_species(mock_cursor, mock_data)
    assert mock_cursor.execute.call_count == 2
   
def test_load_countries(mock_cursor, mock_data):
    load_countries(mock_cursor, mock_data)
    assert mock_cursor.execute.call_count == 2

def test_load_botanists(mock_cursor, mock_data):
    load_botanists(mock_cursor, mock_data)
    assert mock_cursor.execute.call_count == 2

