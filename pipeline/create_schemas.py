"""Executes schema SQL script to set up the database schema"""
import logging
from dotenv import load_dotenv
from pipeline.connect_to_database import get_connection, get_cursor


def configure_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        filename='db_schema_creation.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def run_schema_script() -> None:
    """Runs the schema.sql script to create initial tables"""
    conn = get_connection()

    if conn:
        cursor = get_cursor(conn)

        try:
            with open('schema.sql', 'r') as file:
                sql_script = file.read()

            cursor.execute(sql_script)
            conn.commit()
            logging.info("Schema executed successfully.")
        except Exception as e:
            logging.error(f"Error executing schema.sql: {e}")
        finally:
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")


if __name__ == "__main__":
    load_dotenv()

    configure_logging()
    run_schema_script()
