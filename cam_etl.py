from extract import fetch_data
from transform import clean_data
from load import main as load_data_to_rds

API_URL = "https://data-eng-plants-api.herokuapp.com/plants/"

def run_etl():
    print("Extracting data...")
    raw_data = fetch_data(API_URL)
    if not raw_data:
        print("No data fetched. Exiting ETL process.")
        return

    print("Transforming data...")
    cleaned_data = clean_data(raw_data)
    print(cleaned_data)

#     # Step 3: Load
#     print("Loading data to RDS...")
#     load_data_to_rds(cleaned_data)

if __name__ == "__main__":
    run_etl()