"""Connects to RDS database using credentials"""
import pymssql
import os
import logging
from dotenv import load_dotenv


schema_name = os.getenv("SCHEMA_NAME")


def configure_logging():
    """Configuring logging"""
    logging.basicConfig(
        filename='db_connection.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_connection():
    """Connects to RDS database using credentials"""
    try:
        conn = pymssql.connect(
            server=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        logging.info("Connected to the database successfully.")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None


def get_cursor(conn):
    """Returns cursor"""
    return conn.cursor(as_dict=True)


if __name__ == "__main__":

    load_dotenv()
    configure_logging()

    connection = get_connection()
    if connection:
        cursor = get_cursor(connection)

        # When executing queries, specify the schema if needed:
        # query = f"SELECT * FROM {schema_name}.your_table"
        # cursor.execute(query)
