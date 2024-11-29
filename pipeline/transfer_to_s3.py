"""

This file contains the power to move all the data from a given Microsoft SQL Server Database
into an s3 bucket on AWS.

Steps:
1. Get connection to the database

2. Use a cursor to query all data.

3. Store data in rows in a csv

4. Upload the csv onto and s3 instance

5. Use the cursor to drop all values in the sensor data table.

"""

from os import environ
import logging
import io
import csv
from datetime import date

import boto3
from botocore.exceptions import ClientError
from botocore import client

from dotenv import load_dotenv

import pymssql
from pymssql import Connection, Cursor


JOIN_TABLES_QUERY = """

SELECT
    s.recording_taken,
    s.last_watered,
    ps.plant_name,
    ps.scientific_name,
    s.soil_moisture,
    s.temperature,
    c.country_name,
    b.botanist_forename,
    b.botanist_surname
FROM 
    alpha.plant_species ps
JOIN 
    alpha.plant p ON ps.scientific_name_id = p.scientific_name_id
JOIN 
    alpha.sensor_data s ON s.plant_id = p.plant_id
JOIN 
    alpha.botanist b ON b.botanist_id = p.botanist_id
JOIN 
    alpha.country c ON c.country_id = p.country_id;

"""

DROP_SENSOR_DATA_QUERY = """

TRUNCATE TABLE alpha.sensor_data

"""

CSV_FILE_NAME = "data_for_long_term_storage.csv"


def get_connection() -> Connection:
    """Connects to RDS database using credentials"""
    try:
        conn = pymssql.connect(
            server=environ["DB_HOST"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"],
            database=environ["DB_NAME"],
            port=int(environ["DB_PORT"])
        )
        logging.info("Connected to the database successfully.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None


def execute_query(cursor: Cursor, query):
    """ Returns a list of all outputs from a cursor """
    cursor.execute(query)
    return cursor.fetchall()


def write_csv_from_query(db_cursor: Cursor, file_exists: bool) -> None:
    """ Function that carries out writing csv steps. """

    joined_database_data = execute_query(db_cursor, JOIN_TABLES_QUERY)

    with open(CSV_FILE_NAME, 'a+') as csv_file:
        file_writer = csv.writer(csv_file)
        if not file_exists:
            file_writer.writerow(["recording_taken", "last_watered", "plant_name",
                                  "scientific_name", "soil_moisture", "temperature",
                                  "country_name", "botanist_forename", "botanist_surname"])
        file_writer.writerows(joined_database_data)


def downloads_csv_file(s3_client: client, bucket_name: str, object_key: str) -> bool:
    """ If a historical_plants_data.csv exists in the S3 bucket, download it, otherwise create it locally. """
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        s3_client.download_file(bucket_name, object_key, object_key)
        print(f"File {object_key} downloaded successfully to this directory.")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(
                f"Object '{object_key}' does not exist in the bucket '{bucket_name}'.")
            return False
        else:
            print(f"Error checking object: {e}")
            return False


def send_to_bucket(s3_client: client, bucket_name: str, file_key: str) -> None:
    """ Sends a csv file to an s3 resource """
    try:
        s3_client.upload_file(CSV_FILE_NAME, bucket_name, file_key)
        print(f"CSV file uploaded successfully to {bucket_name}/{file_key}")
    except ClientError as e:
        logging.error(f"Error uploading file to S3: {e}")


def clear_sensor_data(cursor: Cursor):
    """Clears sensor data in database table."""
    try:
        cursor.execute(DROP_SENSOR_DATA_QUERY)
    except Exception as e:
        raise e


def main_transfer():
    """ Main transfer function that executes the whole process """
    s3_client = boto3.client('s3')
    bucket_name = environ["BUCKET"]
    file_key = f"historical_plants_data.csv"

    file_existed = downloads_csv_file(s3_client, bucket_name, file_key)

    conn = get_connection()
    with conn.cursor() as cursor:
        write_csv_from_query(cursor, file_existed)

        send_to_bucket(s3_client, bucket_name, file_key)

        clear_sensor_data(cursor)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    load_dotenv
    main_transfer()
    ...
