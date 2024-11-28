import pymssql
import os
from dotenv import load_dotenv

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

def insert_plant_species(cursor, plant_name, scientific_name):
    """
    Inserts a plant species into the database if it doesn't exist and retrieves the ID.
    """
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM alpha.plant_species WHERE plant_name = %s AND scientific_name = %s)
        INSERT INTO alpha.plant_species (plant_name, scientific_name)
        VALUES (%s, %s)
    """, (plant_name, scientific_name, plant_name, scientific_name))

    cursor.execute("SELECT scientific_name_id FROM alpha.plant_species WHERE plant_name = %s AND scientific_name = %s",
                   (plant_name, scientific_name))
    return cursor.fetchone()[0]


def insert_country(cursor, country_name):
    """
    Inserts a country into the database if it doesn't exist and retrieves the ID.
    """
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM alpha.country WHERE country_name = %s)
        INSERT INTO alpha.country (country_name)
        VALUES (%s)
    """, (country_name, country_name))

    cursor.execute("SELECT country_id FROM alpha.country WHERE country_name = %s", (country_name,))
    return cursor.fetchone()[0]


def insert_botanist(cursor, botanist_email, botanist_forename, botanist_surname, botanist_phone):
    """
    Inserts a botanist into the database if they don't exist and retrieves the ID.
    """
    try:
        print("Inserting botanist:", botanist_email, botanist_forename, botanist_surname, botanist_phone)

        # Check if botanist exists
        check_query = "SELECT botanist_id FROM alpha.botanist WHERE botanist_email = %s"
        check_params = (botanist_email,)
        print("Executing Check Query:", check_query, "with params:", check_params)
        cursor.execute(check_query, check_params)
        result = cursor.fetchone()

        if result is None:
            print(f"Botanist with email {botanist_email} not found. Inserting into database.")

            # Insert botanist if not exists
            insert_query = """
                INSERT INTO alpha.botanist (botanist_email, botanist_forename, botanist_surname, botanist_phone)
                VALUES (%s, %s, %s, %s)
            """
            insert_params = (botanist_email, botanist_forename, botanist_surname, botanist_phone)
            print("Executing Insert Query:", insert_query, "with params:", insert_params)
            cursor.execute(insert_query, insert_params)

            # Retrieve the ID of the inserted botanist
            cursor.execute(check_query, check_params)
            result = cursor.fetchone()

        print("Botanist ID Retrieved:", result[0])
        return result[0]
    except Exception as e:
        print(f"Error inserting botanist: {e}")
        raise


def insert_plant(cursor, plant_id, scientific_name_id, country_id, botanist_id):
    """
    Inserts a plant into the database if it doesn't exist.
    """
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM alpha.plant WHERE plant_id = %s)
        INSERT INTO alpha.plant (plant_id, scientific_name_id, country_id, botanist_id)
        VALUES (%s, %s, %s, %s)
    """, (plant_id, scientific_name_id, country_id, botanist_id))


def insert_sensor_data(cursor, plant_id, recording_taken, last_watered, soil_moisture, temperature):
    """
    Inserts sensor data for a plant into the database.
    """
    cursor.execute("""
        INSERT INTO alpha.sensor_data (plant_id, recording_taken, last_watered, soil_moisture, temperature)
        VALUES (%s, %s, %s, %s, %s)
    """, (plant_id, recording_taken, last_watered, soil_moisture, temperature))


def process_data(cursor, cleaned_data):
    """
    Processes and inserts cleaned data row by row into the database.
    """
    for _, row in cleaned_data.iterrows():
        print("Processing row:", row.to_dict())

        try:
            scientific_name_id = insert_plant_species(cursor, row["plant_name"], row["scientific_name"])

            country_id = insert_country(cursor, row["country_name"])

            botanist_id = insert_botanist(
                cursor, row["botanist_email"], row["botanist_forename"], row["botanist_surname"], row["botanist_phone"]
            )

            insert_plant(cursor, row["plant_id"], scientific_name_id, country_id, botanist_id)

            insert_sensor_data(
                cursor, row["plant_id"], row["recording_taken"], row["last_watered"],
                row["soil_moisture"], row["temperature"]
            )
        except Exception as e:
            print(f"Error processing row: {e}")
            raise


def main(cleaned_data):
    """
    Main function to connect to the database and process the data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        process_data(cursor, cleaned_data)
        conn.commit()
        print("Data successfully loaded into the database.")
    except Exception as e:
        print(f"Error loading data: {e}")
        conn.rollback()
    finally:
        conn.close()