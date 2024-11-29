FROM python:3.9

COPY requirements.txt .

RUN pip3.9 install -r requirements.txt

COPY connect_to_database.py .
COPY email_sender.py .
COPY etl.py .
COPY extract.py .
COPY invariable_load.py .
COPY load_sensor_data.py .
COPY transform.py .


CMD ["python","etl.py"]
