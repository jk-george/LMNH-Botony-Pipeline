FROM python:3.9

COPY ../../requirements.txt .

RUN pip3.9 install -r requirements.txt

COPY ../etl_process/connect_to_database.py .
COPY ../etl_process/etl.py .
COPY ../etl_process/extract.py .
COPY ../etl_process/invariable_load.py .
COPY ../etl_process/load_sensor_data.py .
COPY ../etl_process/transform.py .
COPY ../etl_process/email_sender.py .

CMD ["python","etl.py"]
