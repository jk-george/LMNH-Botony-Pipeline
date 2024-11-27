"""Script to load data that doesn't change into the RDS DB."""
import os
import pandas as pd
import pymysql

def get_connection():
    """Connect to the AWS RDS Microsoft SQL Server database using pymssql. Returns a connection object."""
    try:
        conn = pymysql.connect(
            server=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT")
        )
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit(1)

def insert_data(conn, table: str, data: list, columns: list):
    """Insert data into the specified table."""
    try:
        with conn.cursor() as cur:
            placeholders = ", ".join(["?" for _ in columns])
            columns_str = ", ".join(columns)
            query = f"""
            INSERT INTO {table} ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING;
            """
            cur.executemany(query, data)
            conn.commit()
            print(f"Inserted {len(data)} records into {table}.")
    except Exception as e:
        print(f"Error inserting data into {table}: {e}")
        conn.rollback()


def insert_countries(conn, df):
    """Insert data into the 'country' table."""
    countries = df["country_name"].dropna().unique()
    country_data = [(country,) for country in countries]
    insert_data(conn, "country", country_data, ["country_name"])

def insert_botanists(conn, df):
    """Insert data into the 'botanist' table."""
    botanists = df[["botanist_email", "botanist_forename", "botanist_surname", "botanist_phone"]].drop_duplicates()
    botanist_data = botanists.to_records(index=False).tolist()
    insert_data(conn, "botanist", botanist_data, ["botanist_email", "botanist_forename", "botanist_surname", "botanist_phone"])

def insert_plant_species(conn, df):
    """Insert data into the 'plant_species' table."""
    plant_species = df[["plant_name", "scientific_name"]].drop_duplicates()
    plant_species_data = plant_species.to_records(index=False).tolist()
    insert_data(conn, "plant_species", plant_species_data, ["plant_name", "scientific_name"])

def insert_plants(conn, df):
    """Insert data into the 'plant' table."""
    plants = df[["plant_id", "plant_name", "country_name", "botanist_email"]].drop_duplicates()
    plant_data = plants.to_records(index=False).tolist()
    insert_data(conn, "plant", plant_data, ["plant_id", "plant_name", "country_name", "botanist_email"])

def main():
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