import os
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
        
conn = get_connection()
cursor = conn.cursor()

def insert_botanist(cursor, botanist_email, botanist_forename, botanist_surname, botanist_phone):
    """
    Inserts a botanist into the database if they don't exist and retrieves the ID.
    """
    try:
        print("Inserting botanist:", botanist_email, botanist_forename, botanist_surname, botanist_phone)

        check_query = "SELECT botanist_id FROM alpha.botanist WHERE botanist_email = %s"
        check_params = (botanist_email,)
        print("Executing Check Query:", check_query, "with params:", check_params)
        cursor.execute(check_query, check_params)
        result = cursor.fetchone()

        if result is None:
            print(f"Botanist with email {botanist_email} not found. Inserting into database.")

            insert_query = """
                INSERT INTO alpha.botanist (botanist_email, botanist_forename, botanist_surname, botanist_phone)
                VALUES (%s, %s, %s, %s)
            """
            insert_params = (botanist_email, botanist_forename, botanist_surname, botanist_phone)
            print("Executing Insert Query:", insert_query, "with params:", insert_params)
            cursor.execute(insert_query, insert_params)

            cursor.execute(check_query, check_params)
            result = cursor.fetchone()

        print("Botanist ID Retrieved:", result[0])
        return result[0]
    except Exception as e:
        print(f"Error inserting botanist: {e}")
        raise

row = {
    "plant_id": 11,
    "plant_name": "Asclepias Curassavica",
    "scientific_name": "Asclepias curassavica",
    "soil_moisture": 77.33964770318352,
    "temperature": 9.46715515910055,
    "last_watered": "2024-11-28 13:37:24+0000",
    "botanist_email": "gertrude.jekyll@lnhm.co.uk",
    "botanist_forename": "Gertrude",
    "botanist_surname": "Jekyll",
    "botanist_phone": "001-481-273-3691x127",
    "country_name": "Kahului",
    "recording_taken": "2024-11-28 20:20:45"
}

botanist_id = insert_botanist(cursor, row["botanist_email"], row["botanist_forename"], row["botanist_surname"], row["botanist_phone"])
print("Botanist ID:", botanist_id)