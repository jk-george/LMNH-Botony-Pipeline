
# ETL Pipeline Documentation

This directory of the repository contains an ETL (Extract, Transform, Load) pipeline for processing plant data. The pipeline integrates various scripts for connecting to a database, extracting data, transforming and cleaning it, loading it into a relational database, and monitoring the plant health.

## Directory Overview

```
pipeline/
├── create_schemas.py        # Script to execute schema.sql and set up the database.
├── connect.sh               # Shell script for connecting to the database.
├── schema.sql               # SQL file defining the database schema.
├── transfer_to_s3.py        # Python script to transfer all data from the database to S3.
├── README.md                # Documentation for the project.
├── etl_process/             # Contains scripts for the ETL pipeline.
│   ├── connect_to_database.py   # Handles database connections and cursors.
│   ├── etl.py                   # Orchestrates the complete ETL pipeline.
│   ├── extract.py               # Script for extracting data from an API to CSV/JSON.
│   ├── transform.py             # Cleans and transforms raw data for loading.
│   ├── invariable_load.py       # Loads static data (e.g., species, countries) into the database.
│   ├── load_sensor_data.py      # Loads variable sensor data into the database.
│   ├── email_sender.py          # Sends email alerts for unhealthy plants.
│   ├── etl.dockerfile           # Dockerfile for containerizing the ETL process.
│   ├── requirements.txt         # Lists Python dependencies for the ETL process.
└── scripts/                # Shell scripts for additional automation tasks.
    ├── dockering_process.sh    # Script for building and running Docker containers.
    ├── transfer_process.sh     # Script for automating data transfer processes.
```

---

Below is the detailed documentation for each file in the pipeline:

---

### 1. `connect_to_database.py`
- **Purpose**: Provides functionality to connect to the RDS database.
- **Key Features**:
  - Uses environment variables for database credentials.
  - Returns reusable connection and cursor objects.
  - Logs database connection attempts and errors.
- **Dependencies**: `pymssql`, `dotenv`

---

### 2. `connect.sh`
- **Purpose**: Shell script for establishing a database connection manually.
- **Key Features**:
  - Sources credentials from the `.env` file.
  - Uses `sqlcmd` to connect to the database.
- **Usage**: Execute this script in the terminal to connect to the database.

---

### 3. `schema.sql`
- **Purpose**: Defines the schema for the database tables.
- **Key Features**:
  - Contains SQL commands for creating tables such as `plant_species`, `sensor_data`, and more.
  - Ensures the database structure is properly set up before loading data.
- **Usage**: This file is executed by the `create_schemas.py` script.

---

### 4. `create_schemas.py`
- **Purpose**: Automates the execution of the `schema.sql` file.
- **Key Features**:
  - Reads the schema file and executes its commands in the database.
  - Logs the success or failure of the schema creation process.
- **Dependencies**: `connect_to_database.py`, `logging`, `dotenv`

---

### 5. `extract.py`
- **Purpose**: Extracts plant data from an external API and saves it as a CSV or JSON file.
- **Key Features**:
  - Fetches data for plants by ID range from an API.
  - Cleans and formats the data for further processing.
  - Supports CSV and JSON export formats.
- **Usage**: Run this script to gather raw plant data for transformation.

---

### 6. `transform.py`
- **Purpose**: Cleans and transforms the raw data fetched by `extract.py`.
- **Key Features**:
  - Handles missing data, invalid numeric values, and date conversions.
  - Validates and formats data for consistency.
  - Saves the cleaned data to a new CSV file.
- **Dependencies**: `pandas`, `logging`
- **Usage**: Use this script to prepare data for loading into the database.

---

### 7. `invariable_load.py`
- **Purpose**: Loads static (invariable) data like plant species, countries, and botanists into the database.
- **Key Features**:
  - Ensures no duplicate entries are inserted.
  - Inserts data into tables like `plant_species`, `country`, and `botanist`.
  - Validates relationships between static data entries.
- **Dependencies**: `connect_to_database.py`, `pandas`, `pymssql`

---

### 8. `email_sender.py`
- **Purpose**: Monitors plant health and sends email alerts for unhealthy plants.
- **Key Features**:
  - Checks plant health metrics against thresholds.
  - Sends email alerts to assigned botanists via AWS SES.
  - Logs all email notifications and errors.
- **Dependencies**: `boto3`, `csv`, `dotenv`, `logging`
- **Usage**: Use this script to monitor plant health and notify botanists.

---

### 9. `load_sensor_data.py`
- **Purpose**: Loads sensor data (e.g., soil moisture, temperature) into the database.
- **Key Features**:
  - Validates sensor data and filters out invalid entries.
  - Inserts sensor readings into the `sensor_data` table.
  - Ensures data consistency with plant IDs.
- **Dependencies**: `connect_to_database.py`, `pandas`, `pymssql`
- **Usage**: Run this script to load variable sensor data into the database.

---

### 10. `etl.py`
- **Purpose**: Orchestrates the complete ETL pipeline.
- **Key Features**:
  - Runs the extract, transform, and load (ETL) scripts in sequence.
  - Monitors and logs the entire pipeline process.
  - Sends email alerts upon pipeline completion.
- **Dependencies**: `extract.py`, `transform.py`, `invariable_load.py`, `load_sensor_data.py`, `email_sender.py`
- **Usage**: Use this script to execute the full ETL pipeline.

---

## Getting Started

### Prerequisites
- Install required Python packages using `pip install -r requirements.txt`.


### Running the Pipeline on the Cloud

Note: Please do the following while inside the scripts directory.

1. Initialize the database schema  and create the ECRs by running:
   ```bash
   bash ecr_setup.sh
   ```
2. Dockerise and upload the Images of the ETL process and Long Term Data Storage Process using:
  ```bash
   bash dockering_process.sh
   ```
2. Finally execute the full pipeline using:
   ```bash
   bash create_architecture.sh
   ```

### Logs
- Logs for each script can be found in the `logs` directory.


