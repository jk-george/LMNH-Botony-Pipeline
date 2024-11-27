import os
import pandas as pd
import pymssql

def get_connection():
    """Connects to RDS database using credentials."""
    try:
        conn = pymssql.connect(
            server=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def debug_invalid_dates(sensor_data):
    """Identify rows with invalid or problematic datetime values."""
    print("Original sensor_data:")
    print(sensor_data.head())

    invalid_recording = sensor_data[
        ~pd.to_datetime(sensor_data["recording_taken"], errors="coerce").notna()
    ]
    print("\nRows with invalid recording_taken:")
    print(invalid_recording)

    invalid_watered = sensor_data[
        ~pd.to_datetime(sensor_data["last_watered"], errors="coerce").notna()
    ]
    print("\nRows with invalid last_watered:")
    print(invalid_watered)

    return sensor_data

def clean_dates(sensor_data):
    """Clean and validate datetime columns to avoid SQL Server conversion errors."""
    sensor_data["recording_taken"] = pd.to_datetime(sensor_data["recording_taken"], errors="coerce")
    sensor_data["last_watered"] = pd.to_datetime(sensor_data["last_watered"], errors="coerce")

    sensor_data["recording_taken"] = sensor_data["recording_taken"].dt.tz_localize(None)
    sensor_data["last_watered"] = sensor_data["last_watered"].dt.tz_localize(None)

    valid_min_date = pd.Timestamp("1753-01-01")
    valid_max_date = pd.Timestamp("9999-12-31")

    sensor_data = sensor_data[
        (sensor_data["recording_taken"] >= valid_min_date) &
        (sensor_data["recording_taken"] <= valid_max_date) &
        (sensor_data["last_watered"] >= valid_min_date) &
        (sensor_data["last_watered"] <= valid_max_date)
    ]

    sensor_data = sensor_data.dropna(subset=["recording_taken", "last_watered"])
    return sensor_data

def insert_sensor_data(conn, sensor_data):
    """Insert data into the sensor_data table."""
    try:
        with conn.cursor() as cur:
            query = '''
            INSERT INTO alpha.sensor_data (
                plant_id,
                recording_taken,
                last_watered,
                soil_moisture,
                temperature
            ) VALUES (%s, %s, %s, %s, %s)
            '''
            for row in sensor_data:
                print(f"Inserting row: {row}")  # Debugging rows
                cur.execute(query, row)
            conn.commit()
            print(f"Inserted {len(sensor_data)} records into sensor_data.")
    except Exception as e:
        print(f"Error inserting data into sensor_data: {e}")
        conn.rollback()

def main(cleaned_csv):
    """Main function to load, clean, and insert data into sensor_data."""
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database. Exiting...")
        return

    try:
        df = pd.read_csv(cleaned_csv)
        sensor_data = df[["plant_id", "recording_taken", "soil_moisture", "temperature", "last_watered"]].copy()

        sensor_data = debug_invalid_dates(sensor_data)

        sensor_data = clean_dates(sensor_data)

        print("\nCleaned sensor_data:")
        print(sensor_data.head())

        sensor_data_list = sensor_data.to_records(index=False).tolist()
        insert_sensor_data(conn, sensor_data_list)

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        print("Process completed.")

if __name__ == "__main__":
    cleaned_csv = "plants_data_cleaned.csv"
    main(cleaned_csv)