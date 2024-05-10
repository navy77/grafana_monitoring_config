from kafka import KafkaConsumer
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import pymssql

class KafkaToSQL:
    def __init__(self, kafka_topic, kafka_servers, database_details):
        self.kafka_topic = kafka_topic
        self.kafka_servers = kafka_servers
        self.database_details = database_details
        self.consumer = None
        self.engine = None
        self.conn = None
        self.data = []

    def create_engine(self):
        username = self.database_details['username']
        password = self.database_details['password']
        server = self.database_details['server']
        database = self.database_details['database']
        encoded_password = urllib.parse.quote_plus(password)
        connection_string = f'mssql+pymssql://{username}:{encoded_password}@{server}/{database}'
        self.engine = create_engine(connection_string)
        self.conn = self.engine.connect()

    def setup_kafka_consumer(self):
        self.consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=self.kafka_servers,
            auto_offset_reset='earliest',
            group_id='my-consumer-group',
            enable_auto_commit=True
        )

    @staticmethod
    def parse_influxdb_line(line):
        parts = line.strip().split(' ')
        measurement_tags, fields, timestamp = parts[0], parts[1], parts[2]
        measurement, *tag_parts = measurement_tags.split(',')
        tags = {tag.split('=')[0]: tag.split('=')[1] for tag in tag_parts}
        fields = {field.split('=')[0]: float(field.split('=')[1]) for field in fields.split(',')}
        return measurement, tags, fields, timestamp

    def consume_messages(self):
        try:
            print("Starting the consumer")
            for message in self.consumer:
                msg = message.value.decode('utf-8')
                measurement, tags, fields, timestamp = self.parse_influxdb_line(msg)
                entry = {**tags, **fields, "timestamp": timestamp, "measurement": measurement}
                self.data.append(entry)
                if len(self.data) >= 10:
                    self.insert_into_sql()

        except KeyboardInterrupt:
            print("Stopping consumer")
        finally:
            self.consumer.close()
            if self.conn:
                self.conn.close()
            print("Finished consuming messages")

    def insert_into_sql(self):
        df = pd.DataFrame(self.data)
        df.to_sql("tb1", self.conn, if_exists="append")
        self.data = []  # Clear the list after inserting

if __name__ == "__main__":
    database_details = {
        'username': 'sa',
        'password': 'sa@admin123',
        'server': '192.168.0.160',
        'database': 'kafka'
    }
    kafka_consumer = KafkaToSQL('telegraf', ['localhost:9093'], database_details)
    kafka_consumer.create_engine()
    kafka_consumer.setup_kafka_consumer()
    kafka_consumer.consume_messages()
