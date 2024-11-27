import boto3
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')
SES_SENDER_EMAIL = os.getenv('SES_SENDER_EMAIL')
SES_RECEIVER_EMAIL = os.getenv('SES_RECEIVER_EMAIL')
CSV_FILE_PATH = 'plants_data_cleaned.csv'

SOIL_MOISTURE_THRESHOLD = 80
TEMPERATURE_THRESHOLD = 15

ses = boto3.client('ses', region_name=AWS_REGION)

def read_csv(file_path):
    """Reads the CSV file and returns a list of plant health data."""
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    print(f"Read {len(data)} rows from {file_path}")
    return data

def send_email_alert(plant_data):
    """Send an alert email to the botanist"""
    subject = f"Plant Health Alert for {plant_data['plant_name']}"