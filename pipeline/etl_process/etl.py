"""Complete RTL pipeline"""
import os
from dotenv import load_dotenv
from extract import main_extract
from transform import main_transform
from load_sensor_data import main_load
from email_sender import main_email_alerts
from invariable_load import main as main_load_inv

def delete_if_existing_csv(file_path):
    """Deletes any csvs if they exist already."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print("Deleted old files.")
        else:
            print("No old files to delete.")
    except Exception as e:
        print(f"Error deleting file: {e}")


def run_etl_pipeline():
    """Downloads, cleans and uploads data to the RDS database"""
    load_dotenv()

    raw_csv = './plants_data/plants_data.csv'
    cleaned_csv = './plants_data/plants_data_cleaned.csv'

    delete_if_existing_csv(raw_csv)
    delete_if_existing_csv(cleaned_csv)
    main_extract()
    main_transform(raw_csv, cleaned_csv)
    main_load_inv()
    main_email_alerts()
    main_load(cleaned_csv)


if __name__ == "__main__":
    run_etl_pipeline()
