"""Script to load all of the data that doesn't change into their respective tables."""

import os
import pandas as pd
import pymssql


def get_connection():
    """Connect to the AWS RDS Microsoft SQL Server database using pymssql. Returns a connection object."""
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
        exit(1)


def insert_data(conn, table: str, data: list, columns: list, identity_insert=False):
    """Insert data into the specified table."""
    try:
        with conn.cursor() as cur:

            if identity_insert:
                cur.execute(f"SET IDENTITY_INSERT {table} ON;")

            placeholders = ", ".join(["%s" for _ in columns])
            columns_str = ", ".join(columns)
            query = f"""
            INSERT INTO {table} ({columns_str})
            VALUES ({placeholders});
            """
            cur.executemany(query, data)

            if identity_insert:
                cur.execute(f"SET IDENTITY_INSERT {table} OFF;")

            conn.commit()
            print(f"Inserted {len(data)} records into {table}.")
    except Exception as e:
        print(f"Error inserting data into {table}: {e}")
        conn.rollback()


def get_foreign_key_map(conn, table: str, key_column: str, value_column: str):
    """Retrieve a mapping of key-value pairs from a table."""
    try:
        with conn.cursor(as_dict=True) as cur:
            query = f"SELECT {key_column}, {value_column} FROM {table}"
            cur.execute(query)
            return {row[key_column]: row[value_column] for row in cur.fetchall()}
    except Exception as e:
        print(f"Error fetching data from {table}: {e}")
        return {}


def insert_countries(conn, df):
    """Insert data into the 'country' table."""
    countries = df["country_name"].dropna().unique()
    country_data = [(i + 1, country) for i, country in enumerate(countries)]
    insert_data(conn, "alpha.country", country_data, [
                "country_id", "country_name"], identity_insert=True)


def insert_botanists(conn, df):
    """Insert data into the 'botanist' table."""
    botanists = df[["botanist_email", "botanist_forename",
                    "botanist_surname", "botanist_phone"]].drop_duplicates()
    botanist_data = [(i + 1, *row)
                     for i, row in enumerate(botanists.to_records(index=False).tolist())]
    insert_data(conn, "alpha.botanist", botanist_data, [
                "botanist_id", "botanist_email", "botanist_forename", "botanist_surname", "botanist_phone"], identity_insert=True)


def insert_plant_species(conn, df):
    """Insert data into the 'plant_species' table."""
    plant_species = df[["plant_name", "scientific_name"]].drop_duplicates()
    plant_species_data = [
        (i + 1, *row) for i, row in enumerate(plant_species.to_records(index=False).tolist())]
    insert_data(conn, "alpha.plant_species", plant_species_data, [
                "scientific_name_id", "plant_name", "scientific_name"], identity_insert=True)


def insert_plants(conn, df):
    """Insert data into the 'plant' table."""
    plants = df[["plant_id", "plant_name", "country_name",
                 "botanist_email"]].drop_duplicates()

    country_map = get_foreign_key_map(
        conn, "alpha.country", "country_name", "country_id")
    botanist_map = get_foreign_key_map(
        conn, "alpha.botanist", "botanist_email", "botanist_id")
    plant_species_map = get_foreign_key_map(
        conn, "alpha.plant_species", "plant_name", "scientific_name_id")

    plant_data = [
        (
            plant["plant_id"],
            plant_species_map.get(plant["plant_name"]),
            country_map.get(plant["country_name"]),
            botanist_map.get(plant["botanist_email"])
        )
        for _, plant in plants.iterrows()
        if plant["plant_name"] in plant_species_map and
        plant["country_name"] in country_map and
        plant["botanist_email"] in botanist_map
    ]

    insert_data(conn, "alpha.plant", plant_data, [
                "plant_id", "scientific_name_id", "country_id", "botanist_id"], identity_insert=True)


def main() -> None:
    """Main function to connect to the database, load the CSV, and insert data into tables."""
    conn = get_connection()

    print("Loading data from CSV...")
    df = pd.read_csv("plants_data_cleaned.csv")

    insert_countries(conn, df)
    insert_botanists(conn, df)
    insert_plant_species(conn, df)
    insert_plants(conn, df)

    conn.close()
    print("Data insertion completed successfully.")


if __name__ == "__main__":
    main()
