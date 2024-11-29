"""A script to move variable/changing data from a csv into the RDS."""
import os
import pandas as pd
import pymssql
from typing import Optional, Set
from pandas import DataFrame
from pipeline.connect_to_database import get_connection


def clean_and_prepare_sensor_data(csv_file: str) -> DataFrame:
    """Load and clean the sensor data from a CSV file."""
    df = pd.read_csv(csv_file)
    df["recording_taken"] = pd.to_datetime(
        df["recording_taken"], errors="coerce")
    df["last_watered"] = pd.to_datetime(df["last_watered"], errors="coerce")
    df = df.dropna(subset=["recording_taken", "last_watered"])
    df["recording_taken"] = df["recording_taken"].dt.tz_localize(None)
    df["last_watered"] = df["last_watered"].dt.tz_localize(None)

    return df


def fetch_valid_plant_ids(conn: pymssql.Connection) -> Set[int]:
    """Fetch valid plant IDs from the alpha.plant table."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT plant_id FROM alpha.plant;")
            rows = cursor.fetchall()
            return {row[0] for row in rows}
    except Exception as e:
        print(f"Failed to fetch valid plant IDs: {e}")
        return set()


def filter_valid_sensor_data(df: DataFrame, valid_plant_ids: Set[int]) -> DataFrame:
    """Filter the sensor data to include only rows with valid plant IDs."""
    return df[df["plant_id"].isin(valid_plant_ids)]


def insert_sensor_data(conn: pymssql.Connection, sensor_data_df: DataFrame) -> None:
    """Insert the sensor data into the alpha.sensor_data table."""
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
            print(f"Inserted {len(data)} records into sensor_data.")
    except Exception as e:
        print(f"Error inserting data into sensor_data: {e}")
        conn.rollback()


def main_load(csv_file: str) -> None:
    """Main function to load, clean, validate, and insert sensor data into the database."""
    conn = get_connection()
    if conn is None:
        return
    try:
        sensor_data_df = clean_and_prepare_sensor_data(csv_file)
        valid_plant_ids = fetch_valid_plant_ids(conn)
        sensor_data_df = filter_valid_sensor_data(
            sensor_data_df, valid_plant_ids)
        insert_sensor_data(conn, sensor_data_df)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    csv_file = "plants_data_cleaned.csv"
    main_load(csv_file)
