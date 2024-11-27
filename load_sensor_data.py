import pandas as pd
import logging
import pymssql
from connect_to_database import get_connection, get_cursor


# def insert_sensor_data(conn, cursor):
#     """Inserts sendor data to the schema"""


def load_to_db(cleaned_csv: str) -> None:
    """Loads cleaned data from a CSV file into the database."""
    try:
        logging.info(f"Loading cleaned data from {cleaned_csv}.")
        df = pd.read_csv(cleaned_csv)

        conn = get_connection()
        cursor = get_cursor(conn)

        SQL_STATEMENT = """
            INSERT INTO alpha.sensor_data (
                plant_id,
                recording_taken,
                last_watered,
                soil_moisture,
                temperature
            ) OUTPUT INSERTED.sensor_data_id
            VALUES (%s, %s, %s, %s, %s)
            """

        for _, row in df.iterrows():
            cursor.execute(
                SQL_STATEMENT,
                (
                    row['plant_id'],
                    row['recording_taken'],
                    row['last_watered'],
                    row['soil_moisture'],
                    row['temperature']
                )
            )
            result = cursor.fetchone()
            if result:
                logging.info(f"Inserted record with sensor_data_id: {
                             result['sensor_data_id']}")

        # Commit the transaction
        conn.commit()
        logging.info("All data inserted successfully.")

    except Exception as e:
        logging.error(f"Failed to load data into the database: {e}")
        raise


if __name__ == '__main__':
    # Specify the cleaned CSV file
    cleaned_csv = 'plants_data_cleaned.csv'

    logging.info("Starting data loading process.")
    try:
        load_to_db(cleaned_csv)
        logging.info("Data loading process completed successfully.")
    except Exception as e:
        logging.error(f"Data loading process failed: {e}")
        raise
