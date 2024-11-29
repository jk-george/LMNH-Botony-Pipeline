# This readme is for the set up at the start of the project, ensuring you have all the correct installations

## 🛠️ Getting Setup

**Python version and environment**

1. Install older version of python:
- `brew install python@3.9` 

2. Create a virtual environment:
- `python3.9 -m venv .venv`
  (If you have an existing venv, run `deactivate` and delete the venv folder and empty trash first)
- Then activate it by running `source .venv/bin/activate`


1. Install and connect pyenv:
- `brew install pyenv`
- `pyenv install 3.11.5`
- `pyenv local 3.11.5`

**Microsoft SQL Server**
1. Install SQLCMD - Enables connection to SQL Server
- `brew install sqlcmd`

2. `pymssql` requires extra dependencies:
- Run `brew install freetds`
- Then run `pip install pymssql` 
  (if pymssql is already installed then run `pip uninstall pymssql` before installing it again to link it to FreeTDS)


**Other setup**

1. **AWS credentials** Ensure you have a `.env` file with your AWS credentials (DB_HOST, DB_PORT, DB_PASSWORD, DB_USER, DB_NAME, SCHEMA_NAME).
   
2. **Requirements** Install necessary packages: `pip install -r requirements.txt`.

3. **Database Setup** Ensure your Microsoft SQL Server database is set up: 
   - To create schemas: `python create_schemas.py` -- Only when required.
   - To connect to database: `python pipeline/connect_to_database.py` -- Only needs to be ran once per session.
   - To run full ETL process: `python pipeline/etl.py`

**Useful commands**
- To connect to the RDS database run `bash connect.sh`
- To see all of the schemas run: 
`SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'alpha' AND TABLE_TYPE = 'BASE TABLE';` 
(follow each command with `GO`)
- To leave session run `quit`

- To see all tables and their elements:
SELECT * FROM alpha.plant_species;
SELECT * FROM alpha.country;
SELECT * FROM alpha.botanist;
SELECT * FROM alpha.plant;
SELECT * FROM alpha.sensor_data;

## 🗂️ Files Explained
Things to Know for **extract.py**

- This script uses `argparse` for option to output to either a `.csv` or a `.json`.
If left empty, the script will output to .csv by default.

```
python3 extract.py --format [csv or json]
```

- In the arguments of this function you can specify how many rows you want by altering the `end_id`.

```
def fetch_all_plants(start_id=1, end_id=50):
```

