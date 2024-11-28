import requests

def fetch_data(base_url, start_id=1, end_id=50):
    """
    Fetches data from the API for plant IDs from start_id to end_id.
    """
    aggregated_data = []
    
    for plant_id in range(start_id, end_id + 1):
        url = f"{base_url}/{plant_id}"
        try:
            print(f"Fetching data for plant ID: {plant_id}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            aggregated_data.append(data)
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error for plant ID {plant_id}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error for plant ID {plant_id}: {req_err}")
        except Exception as e:
            print(f"Unexpected error for plant ID {plant_id}: {e}")
    
    print(f"Fetched data for {len(aggregated_data)} plants.")
    return aggregated_data