"""A script to move variable/changing data from a csv into the RDS."""
import os
import pandas as pd
import pymssql
import logging
from typing import Optional, Set
from pandas import DataFrame
from connect_to_database import get_connection

logging.basicConfig(
    filename="sensor_data_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def clean_and_prepare_sensor_data(csv_file: str) -> DataFrame:
    """Load and clean the sensor data from a CSV file."""
    logging.info("Starting to clean and prepare sensor data.")
    try:
        df = pd.read_csv(csv_file)
        df["recording_taken"] = pd.to_datetime(
            df["recording_taken"], errors="coerce")
        df["last_watered"] = pd.to_datetime(df["last_watered"], errors="coerce")
        df = df.dropna(subset=["recording_taken", "last_watered"])
        df["recording_taken"] = df["recording_taken"].dt.tz_localize(None)
        df["last_watered"] = df["last_watered"].dt.tz_localize(None)
        logging.info("Successfully loaded and cleaned data from {csv_file}.")
        return df
    except Exception as e:
        logging.error(f"Error cleaning and preparing sensor data: {e}")
        raise


def fetch_valid_plant_ids(conn: pymssql.Connection) -> Set[int]:
    """Fetch valid plant IDs from the alpha.plant table."""
    logging.info("Fetching valid plant IDs from the database.")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT plant_id FROM alpha.plant;")
            rows = cursor.fetchall()
            valid_ids = {row[0] for row in rows}
            logging.info(f"Fetched {len(valid_ids)} valid plant IDs.")
            return valid_ids
    except Exception as e:
        logging.error(f"Failed to fetch valid plant IDs: {e}")
        return set()


def filter_valid_sensor_data(df: DataFrame, valid_plant_ids: Set[int]) -> DataFrame:
    """Filter the sensor data to include only rows with valid plant IDs."""
    logging.info("Filtering sensor data for valid plant IDs.")
    try:
        filtered_df = df[df["plant_id"].isin(valid_plant_ids)]
        logging.info(f"Filtered sensor data to {len(filtered_df)} valid rows.")
        return filtered_df
    except Exception as e:
        logging.error(f"Error filtering sensor data: {e}")
        raise


def insert_sensor_data(conn: pymssql.Connection, sensor_data_df: DataFrame) -> None:
    """Insert the sensor data into the alpha.sensor_data table."""
    logging.info("Inserting sensor data into the database.")
    try:
        with conn.cursor() as cur:
            query = '''
            INSERT INTO alpha.sensor_data (
                plant_id,
                recording_taken,
                soil_moisture,
                temperature,
                last_watered
            ) VALUES (%s, %s, %s, %s, %s);
            '''
            data = [
                (
                    row.plant_id,
                    row.recording_taken,
                    row.soil_moisture,
                    row.temperature,
                    row.last_watered
                )
                for row in sensor_data_df.itertuples(index=False)
            ]
            cur.executemany(query, data)
            conn.commit()
            logging.info(f"Inserted {len(data)} records into sensor_data.")
    except Exception as e:
        logging.error(f"Error inserting data into sensor_data: {e}")
        conn.rollback()
        raise


def main_load(csv_file: str) -> None:
    """Main function to load, clean, validate, and insert sensor data into the database."""
    logging.info("Starting main process for sensor data processing.")
    conn = get_connection()
    if conn is None:
        logging.error("Database connection could not be established.")
        return
    try:
        sensor_data_df = clean_and_prepare_sensor_data(csv_file)
        valid_plant_ids = fetch_valid_plant_ids(conn)
        sensor_data_df = filter_valid_sensor_data(
            sensor_data_df, valid_plant_ids)
        insert_sensor_data(conn, sensor_data_df)
        logging.info("Sensor data processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")
    finally:
        conn.close()
        logging.info("Database connection closed.")


if __name__ == "__main__":
    csv_file = "plants_data_cleaned.csv"
    main_load(csv_file)
