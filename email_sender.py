import boto3
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')
SES_SENDER_EMAIL = os.getenv('SES_SENDER_EMAIL')
SES_RECEIVER_EMAIL = os.getenv('SES_RECEIVER_EMAIL')
HEALTH_THRESHOLD = float(os.getenv('HEALTH_THRESHOLD', 70))
CSV_FILE_PATH = 'plants_data_cleaned.csv'

ses = boto3.client('ses', region_name=AWS_REGION)

