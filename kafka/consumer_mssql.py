from kafka import KafkaConsumer
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select, or_
import urllib.parse
import pymssql
# Database connection setup

username = 'sa'
password = 'sa@admin123'
server = '192.168.0.160'
database = 'kafka'

encoded_password = urllib.parse.quote_plus(password)
engine = create_engine(f'mssql+pymssql://{username}:{encoded_password}@{server}/{database}')
conn = engine.connect()
metadata = MetaData()

# Kafka Consumer Setup
consumer = KafkaConsumer(
    'telegraf',
    bootstrap_servers=['localhost:9093'],
    auto_offset_reset='earliest',
    group_id='my-consumer-group',
    enable_auto_commit=True
)

def parse_influxdb_line(line):
    parts = line.strip().split(' ')
    measurement_tags, fields, timestamp = parts[0], parts[1], parts[2]
    measurement, *tag_parts = measurement_tags.split(',')
    tags = {tag.split('=')[0]: tag.split('=')[1] for tag in tag_parts}
    fields = {field.split('=')[0]: float(field.split('=')[1]) for field in fields.split(',')}
    return measurement, tags, fields, timestamp

data = []

# Consume messages
try:
    print("Starting the consumer")
    for message in consumer:
        msg = message.value.decode('utf-8')
        measurement, tags, fields, timestamp = parse_influxdb_line(msg)
        entry = {**tags, **fields, "timestamp": timestamp, "measurement": measurement}
        data.append(entry)
        if len(data) >= 5:
            df = pd.DataFrame(data)
            print(df)
            # Insert to SQL Server
            df.to_sql("tb1",conn,if_exists="append")

            data = []  # Clear the list after inserting

except KeyboardInterrupt:
    print("Stopping consumer")
finally:
    consumer.close()

print("Finished consuming messages")
