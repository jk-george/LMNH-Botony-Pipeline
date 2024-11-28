"""

This file contains the power to move all the data from a given Microsoft SQL Server Database
into an s3 bucket on AWS.

Steps:
1. Get connection to the database
2. Use a cursor to query all data.
3. Store data in rows in a csv
4. Upload the csv onto and s3 instance

"""

from invariable_load import get_connection
import pymssql
from pymssql import Cursor


JOIN_TABLES_QUERY = """







"""


def execute_query(cursor: Cursor):
    ...


def main() -> None:
    """ Main function that carries out all steps. """
    conn = get_connection()
    with conn.cursor() as db_cursor:

        ...

    conn.close()


if __name__ == "__main__":

    ...
