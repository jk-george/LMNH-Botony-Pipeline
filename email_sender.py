"""
email_sender.py checks the plants_data_cleaned.csv file for any values outside
of the specified range of 'healthy plant' (this can be changed within this script)
and emails the botanist who has been assigned to the plant if the plant is classified
as 'unhealthy'.
Logging is also utilised to ensure a clear story can be told throughout the running of
the script.
"""
import boto3
import csv
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='email_sender.log',
    filemode='a'
)

load_dotenv()

def get_config():
    """Fetches configuration settings for the application."""
    return {
        'aws_region': os.getenv('AWS_REGION'),
        'ses_sender_email': os.getenv('SES_SENDER_EMAIL'),
        'csv_file_path': 'plants_data_cleaned.csv',
        'soil_moisture_threshold': 50,
        'temperature_threshold': 15,
    }

def get_ses_client(aws_region):
    """Initializes and returns the SES client."""
    return boto3.client('ses', region_name=aws_region)

def read_csv(file_path):
    """Reads the CSV file and returns a list of plant health data."""
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = [row for row in reader]
        logging.info(f"Read {len(data)} rows from {file_path}")
        return data
    except Exception as e:
        logging.error(f"Failed to read CSV file {file_path}: {e}")
        raise

def send_email_alert(ses, sender_email, receiver_email, plant_data):
    """Send an alert email to the botanist."""
    subject = f"Plant Health Alert for {plant_data['plant_name']}"
    body = (
        f"Dear {plant_data['botanist_forename']} {plant_data['botanist_surname']},\n\n"
        f"We have detected an issue with the health of your plant:\n"
        f"Plant Name: {plant_data['plant_name']} ({plant_data['scientific_name']})\n"
        f"Plant ID: {plant_data['plant_id']}\n"
        f"Country of Origin: {plant_data['country_name']}\n"
        f"\nCurrent Conditions:\n"
        f"- Soil Moisture: {plant_data['soil_moisture']}%\n"
        f"- Temperature: {plant_data['temperature']}°C\n"
        f"- Last Watered: {plant_data['last_watered']}\n"
        f"\nRecommended Action: Please check the plant's environment and address the issue promptly.\n\n"
        f"Best regards,\n"
        f"The Plant Health Monitoring Team"
    )
    try:
        ses.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [plant_data['botanist_email']]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        logging.info(f"Alert email sent to {plant_data['botanist_email']} for plant {plant_data['plant_name']}")
    except Exception as e:
        logging.error(f"Failed to send email to {plant_data['botanist_email']}: {e}")

def main():
    """Main function to monitor plant health and send alerts."""
    try:
        config = get_config()
        ses = get_ses_client(config['aws_region'])
        plant_data_list = read_csv(config['csv_file_path'])

        for plant_data in plant_data_list:
            soil_moisture = float(plant_data['soil_moisture'])
            temperature = float(plant_data['temperature'])

            if soil_moisture > config['soil_moisture_threshold'] or temperature < config['temperature_threshold']:
                logging.warning(f"Alert: Plant '{plant_data['plant_name']}' requires attention.")
                send_email_alert(
                    ses, 
                    config['ses_sender_email'], 
                    config['ses_receiver_email'], 
                    plant_data
                )
            else:
                logging.info(f"Plant '{plant_data['plant_name']}' is healthy.")
    except Exception as e:
        logging.error(f"Error occurred in main: {e}")

if __name__ == '__main__':
    main()
