"""Complete RTL pipeline"""
from dotenv import load_dotenv
from extract import main_extract
from transform import main_transform
from load_sensor_data import main_load


def run_etl_pipeline():
    """Downloads, cleans and uploads data to the RDS database"""
    load_dotenv()

    raw_csv = './plants_data/plants_data.csv'
    cleaned_csv = 'plants_data_cleaned.csv'

    main_extract()
    main_transform(raw_csv, cleaned_csv)
    main_load(cleaned_csv)


if __name__ == "__main__":
    run_etl_pipeline()
