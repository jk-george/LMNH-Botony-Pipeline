import pandas as pd
import logging
import pymssql

# SQL statement for insertion
SQL_STATEMENT = """
INSERT INTO sensor_data (
    plant_id, 
    recording_taken, 
    last_watered, 
    soil_moisture, 
    temperature
) OUTPUT INSERTED.sensor_data_id
VALUES (%s, %s, %s, %s, %s)
"""


def load_to_db(cleaned_csv: str) -> None:
    """Loads cleaned data from a CSV file into the database."""
    try:
        logging.info(f"Loading cleaned data from {cleaned_csv}.")
        df = pd.read_csv(cleaned_csv)
        logging.info(f"Loaded cleaned data. Shape: {df.shape}")

        conn = pymssql.connect(server, username, password, database)
        cursor = conn.cursor(as_dict=True)

        for _, row in df.iterrows():
            cursor.execute(
                SQL_STATEMENT,
                (

                    row['plant_id'],
                    # 'YYYY-MM-DD HH:MM:SS' format
                    row['recording_taken'],
                    # Ensure date is in 'YYYY-MM-DD HH:MM:SS' format
                    row['last_watered'],
                    row['soil_moisture'],     # Soil moisture value
                    row['temperature']        # Temperature value
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

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


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
