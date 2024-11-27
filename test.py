import pandas as pd
import os
import logging
import pymssql
# from connect_to_database import get_connection, get_cursor


def get_connection():
    """Connects to RDS database using credentials"""
    try:
        conn = pymssql.connect(
            server=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT")
        )
        logging.info("Connected to the database successfully.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None


def insert_sensor_data(conn, sensor_data):
    try:
        with conn.cursor(as_dict=True) as cur:

            query = """
            INSERT INTO alpha.sensor_data (
                plant_id,
                recording_taken,
                last_watered,
                soil_moisture,
                temperature
            ) OUTPUT INSERTED.sensor_data_id
            VALUES (%s, %s, %s, %s, %s)
            """

            inserted_ids = []
            for row in sensor_data:
                cur.execute(query, row)
                inserted_id = cur.fetchone()[0]
                inserted_ids.append(inserted_id)

            conn.commit()
            print(f"Inserted {len(sensor_data)} records into sensor_data.")
    except Exception as e:
        print(f"Error inserting data into sensor_data: {e}")
        conn.rollback()


def main(cleaned_csv):

    conn = get_connection()
    print("connected")
    df = pd.read_csv(cleaned_csv)

    sensor_data = df[['plant_id', 'recording_taken',
                      'last_watered', 'soil_moisture', 'temperature']]

    sensor_data = sensor_data.dropna()
    print("1")

    sensor_data_list = sensor_data.to_records(index=False).tolist()
    print("2")

    print(sensor_data)
    insert_sensor_data(conn, sensor_data_list)
    print("3")

    conn.close()


if __name__ == '__main__':

    cleaned_csv = 'plants_data_cleaned.csv'
    main(cleaned_csv)
