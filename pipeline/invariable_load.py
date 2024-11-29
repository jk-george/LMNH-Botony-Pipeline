"""Inserts into invariable tables from csv."""

import pandas as pd
import pymssql
from pipeline.connect_to_database import get_connection

def load_plant_species(cursor: pymssql.Cursor, data: pd.DataFrame) -> None:
    """Loads plant species data into the alpha.plant_species table if not already present."""
    plant_species = data[['scientific_name', 'plant_name']].drop_duplicates()
    for _, row in plant_species.iterrows():
        cursor.execute(
            """
            SELECT scientific_name_id FROM alpha.plant_species
            WHERE scientific_name = %s
            """,
            (row['scientific_name'],)
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO alpha.plant_species (scientific_name, plant_name)
                VALUES (%s, %s)
                """,
                (row['scientific_name'], row['plant_name'])
            )
            print(f"Inserted plant species: {row['scientific_name']}")

def load_countries(cursor: pymssql.Cursor, data: pd.DataFrame) -> None:
    """Loads country data into the alpha.country table if not already present."""
    countries = data[['country_name']].drop_duplicates()
    for _, row in countries.iterrows():
        cursor.execute(
            """
            SELECT country_id FROM alpha.country
            WHERE country_name = %s
            """,
            (row['country_name'],)
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO alpha.country (country_name)
                VALUES (%s)
                """,
                (row['country_name'],)
            )
            print(f"Inserted country: {row['country_name']}")

def load_botanists(cursor: pymssql.Cursor, data: pd.DataFrame) -> None:
    """Loads botanist data into the alpha.botanist table if not already present."""
    botanists = data[['botanist_email', 'botanist_forename', 'botanist_surname', 'botanist_phone']].drop_duplicates()
    for _, row in botanists.iterrows():
        cursor.execute(
            """
            SELECT botanist_id FROM alpha.botanist
            WHERE botanist_email = %s
            """,
            (row['botanist_email'],)
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO alpha.botanist (botanist_email, botanist_forename, botanist_surname, botanist_phone)
                VALUES (%s, %s, %s, %s)
                """,
                (row['botanist_email'], row['botanist_forename'], row['botanist_surname'], row['botanist_phone'])
            )
            print(f"Inserted botanist: {row['botanist_email']}")

def load_plants(cursor: pymssql.Cursor, data: pd.DataFrame) -> None:
    """Loads plant data into the alpha.plant table if not already present."""
    plants = data[['plant_id', 'scientific_name', 'country_name', 'botanist_email']].drop_duplicates()
    for _, row in plants.iterrows():
        cursor.execute(
            """
            SELECT plant_id FROM alpha.plant
            WHERE plant_id = %s
            """,
            (row['plant_id'],)
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                SELECT ps.scientific_name_id, c.country_id, b.botanist_id
                FROM alpha.plant_species ps, alpha.country c, alpha.botanist b
                WHERE ps.scientific_name = %s AND c.country_name = %s AND b.botanist_email = %s
                """,
                (row['scientific_name'], row['country_name'], row['botanist_email'])
            )
            result = cursor.fetchone()
            if result:
                scientific_name_id, country_id, botanist_id = result
                cursor.execute(
                    """
                    INSERT INTO alpha.plant (plant_id, scientific_name_id, country_id, botanist_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (row['plant_id'], scientific_name_id, country_id, botanist_id)
                )
                print(f"Inserted plant: {row['plant_id']}, {scientific_name_id}, {country_id}, {botanist_id}")
            else:
                print(f"Plant not inserted: No match for {row['scientific_name']}, {row['country_name']}, {row['botanist_email']}")

def main() -> None:
    """Main function to load data into the database."""
    file_path = "plants_data_cleaned.csv"
    data = pd.read_csv(file_path)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        load_plant_species(cursor, data)
        load_countries(cursor, data)
        load_botanists(cursor, data)
        load_plants(cursor, data)
        conn.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()