import pandas as pd
from datetime import datetime

def separate_botanist_dict(df):
    """
    Extracts the botanist dictionary into separate columns, including splitting names.
    """
    if 'botanist' in df.columns:
        botanist_df = pd.json_normalize(df['botanist'])
        
        botanist_df.columns = [f"botanist_{col}" for col in botanist_df.columns]
        
        if 'botanist_name' in botanist_df.columns:
            botanist_df[['botanist_forename', 'botanist_surname']] = botanist_df['botanist_name'].str.split(n=1, expand=True)
            botanist_df.drop(columns=['botanist_name'], inplace=True)
        
        df = pd.concat([df.drop(columns=['botanist']), botanist_df], axis=1)
    else:
        print("No 'botanist' column found.")
    return df


def process_origin_location(df):
    """
    Processes the origin_location field to extract country_name.
    """
    if 'origin_location' in df.columns:
        df['country_name'] = df['origin_location'].apply(lambda x: x[2] if isinstance(x, list) else None)
        df.drop(columns=['origin_location'], inplace=True)
    else:
        print("No 'origin_location' column found.")
    return df


def drop_missing_data(df):
    """
    Drops rows with missing fields.
    """
    before_drop = len(df)
    df.dropna(inplace=True)
    after_drop = len(df)
    print(f"Dropped {before_drop - after_drop} rows with missing fields. Remaining rows: {after_drop}")
    return df


def set_numeric_limits(df):
    """
    Filters rows based on numeric limits for soil_moisture and temperature.
    """
    before_filter = len(df)
    df = df[(df["soil_moisture"].between(0, 100)) & (df["temperature"].between(-10, 50))]
    after_filter = len(df)
    print(f"Filtered rows outside valid ranges. Dropped {before_filter - after_filter} rows. Remaining rows: {after_filter}")
    return df


def clean_text_fields(df, text_columns):
    """
    Strips whitespace from specified text columns.
    """
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].str.strip()
            print(f"Stripped whitespace from column: {col}")
    return df


def convert_dates(df, date_columns):
    """
    Converts specified columns to datetime format.
    """
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            print(f"Converted column '{col}' to datetime.")
    return df


def drop_empty_country_name(df):
    """
    Drops rows with empty country_name.
    """
    before_drop = len(df)
    df = df[df["country_name"].notna()]
    after_drop = len(df)
    print(f"Dropped {before_drop - after_drop} rows with empty country_name. Remaining rows: {after_drop}")
    return df


def clean_data(raw_data):
    """
    Cleans and transforms the raw data from the API by calling modular functions.
    """
    print("Raw data received:", raw_data[:2])

    try:
        df = pd.DataFrame(raw_data)
        print("Initial DataFrame created:\n", df.head())
    except Exception as e:
        print("Error creating DataFrame from raw_data:", e)
        return pd.DataFrame()

    df = separate_botanist_dict(df)

    df = process_origin_location(df)

    df.rename(columns={"name": "plant_name"}, inplace=True)

    if 'scientific_name' in df.columns:
        df['scientific_name'] = df['scientific_name'].apply(lambda x: x[0] if isinstance(x, list) else x)
    else:
        print("No 'scientific_name' column found. Adding a placeholder.")
        df['scientific_name'] = None

    relevant_columns = [
        "plant_id", "plant_name", "scientific_name", "soil_moisture", "temperature", "last_watered",
        "botanist_email", "botanist_forename", "botanist_surname", "botanist_phone",
        "country_name", "recording_taken"
    ]
    try:
        df = df[relevant_columns]
        print("DataFrame after selecting relevant columns:\n", df.head())
    except KeyError as e:
        print("KeyError selecting relevant columns:", e)
        return pd.DataFrame()

    df = drop_missing_data(df)

    df = set_numeric_limits(df)

    text_columns = ["plant_name", "scientific_name", "botanist_email", "botanist_name", "botanist_phone", "country_name"]
    df = clean_text_fields(df, text_columns)

    date_columns = ["last_watered", "recording_taken"]
    df = convert_dates(df, date_columns)

    df = drop_empty_country_name(df)

    print("Final cleaned DataFrame:\n", df.head())
    return df