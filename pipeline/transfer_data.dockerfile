FROM python:3.9

COPY etl_process/requirements.txt .

RUN pip3.9 install -r requirements.txt

COPY transfer_to_s3.py .

CMD ["python","transfer_to_s3.py"]