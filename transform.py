"""
transform.py transforms and cleans data from a given CSV file.
This function reads data from the specified input CSV file, performs
necessary transformations and cleaning operations, and then writes
the cleaned data to the specified output CSV file.
"""
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_cleaning.log',
    filemode='a'
)

def load_data(input_file: str) -> pd.DataFrame:
    """Loads data from the original CSV file."""
    try:
        logging.info(f"Loading data from {input_file}.")
        df = pd.read_csv(input_file)
        logging.info(f"Data loaded successfully.")
        return df
    except Exception as e:
        logging.error(f"Failed to load data from {input_file}: {e}")
        raise

def drop_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drops rows with missing fields."""
    mandatory_fields = ['plant_name', 'scientific_name', 'country_name', 
            'botanist_email', 'botanist_forename', 'botanist_surname', 'botanist_phone']
    initial_shape = df.shape
    df = df.dropna(subset=mandatory_fields)
    logging.info(
        f"Dropped rows with missing mandatory fields {mandatory_fields}. "
        f"Rows before: {initial_shape[0]}, Rows after: {df.shape[0]}"
    )
    return df

def set_numeric_limits(df: pd.DataFrame) -> pd.DataFrame:
    """Drops rows that aren't within the specified numeric limits."""
    initial_shape = df.shape
    df = df[(df['soil_moisture'] >= 0) & (df['soil_moisture'] <= 100)]
    df = df[(df['temperature'] >= -10) & (df['temperature'] <= 50)]
    logging.info(
        f"Filtered with limits on 'soil_moisture' (0-100) and 'temperature' (-10 to 50). "
        f"Rows before: {initial_shape[0]}, Rows after: {df.shape[0]}"
    )
    return df

def clean_text_fields(df: pd.DataFrame, text_fields: list[str]) -> pd.DataFrame:
    """Strips any unnecessary whitespace from text fields."""
    for field in text_fields:
        if field in df.columns:
            initial_non_empty = df[field].notnull().sum()
            df[field] = df[field].str.strip()
            logging.info(
                f"Cleaned whitespace in column '{field}'. Non-empty values: {initial_non_empty}"
            )
    return df

def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the last_watered column to datetime and drop rows which don't comply with this."""
    initial_shape = df.shape
    df['last_watered'] = pd.to_datetime(df['last_watered'], errors='coerce')
    df = df.dropna(subset=['last_watered'])
    logging.info(
        f"Converted 'last_watered' to datetime and dropped invalid rows. "
        f"Rows before: {initial_shape[0]}, Rows after: {df.shape[0]}"
    )
    return df

def filter_invalid_location(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that have an empty country_name column."""
    initial_shape = df.shape
    df = df[df['country_name'].notnull()]
    logging.info(
        f"Filtered rows with an empty 'country_name'. "
        f"Rows before: {initial_shape[0]}, Rows after: {df.shape[0]}"
    )
    return df

def validate_botanist_details(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean botanist details."""
    botanist_fields = ['botanist_email', 'botanist_forename', 'botanist_surname', 'botanist_phone']
    for field in botanist_fields:
        if field in df.columns:
            initial_non_empty = df[field].notnull().sum()
            df[field] = df[field].str.strip()
            logging.info(
                f"Validated and cleaned botanist detail '{field}'. Non-empty values: {initial_non_empty}"
            )
    return df

def save_data(df: pd.DataFrame, output_file: str) -> None:
    """Save the cleaned data to a new CSV file."""
    try:
        df.to_csv(output_file, index=False)
        logging.info(f"Data saved successfully to {output_file}. Final shape: {df.shape}")
    except Exception as e:
        logging.error(f"Failed to save data to {output_file}: {e}")
        raise

def main(input_file: str, output_file: str) -> None:
    """Main function to carry out the transformation process."""
    logging.info("Data cleaning process started.")
    try:
        df = load_data(input_file)
        df = drop_missing_data(df)
        df = set_numeric_limits(df)
        df = clean_text_fields(df, text_fields=[
            'plant_name', 'scientific_name', 'country_name', 
            'botanist_email', 'botanist_forename', 'botanist_surname', 'botanist_phone'
        ])
        df = convert_dates(df)
        df = filter_invalid_location(df)
        df = validate_botanist_details(df)
        save_data(df, output_file)
        logging.info("Data cleaning process completed successfully.")
    except Exception as e:
        logging.error(f"Data cleaning process failed: {e}")
        raise

if __name__ == '__main__':
    input_file = 'plants_data.csv'
    output_file = 'plants_data_cleaned.csv'
    main(input_file, output_file)
