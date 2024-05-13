import threading
from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata
import pandas as pd
import time

# Setup Kafka Consumer
consumer = KafkaConsumer(
    'telegraf',
    bootstrap_servers=['localhost:9093'],
    auto_offset_reset='earliest',
    group_id='my-consumer-group',
    enable_auto_commit=False
)

def parse_influxdb_line(line):
    parts = line.strip().split(' ')
    measurement_tags, fields, timestamp = parts[0], parts[1], parts[2]

    measurement, *tag_parts = measurement_tags.split(',')
    tags = {}
    for tag in tag_parts:
        key, value = tag.split('=')
        tags[key] = value

    field_data = {}
    for field in fields.split(','):
        key, value = field.split('=')
        field_data[key] = float(value)

    return measurement, tags, field_data, timestamp

def process_data(data_batch):
    if data_batch:
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(data_batch)
        print(df)
        data_batch.clear()

def commit_offsets(last_message):
    if last_message:
        # Committing the offset
        tp = TopicPartition(last_message.topic, last_message.partition)
        offsets = {tp: OffsetAndMetadata(last_message.offset + 1, None)}
        consumer.commit(offsets=offsets)

data = []
last_message = None
stop_event = threading.Event()

def handle_batch():
    global data, last_message
    process_data(data)
    commit_offsets(last_message)
    if not stop_event.is_set():
        # Restart the timer unless the stop event is set
        threading.Timer(10, handle_batch).start()

# Start the initial timer
threading.Timer(10, handle_batch).start()

try:
    print("Starting the consumer")
    for message in consumer:
        last_message = message
        msg = message.value.decode('utf-8')
        print("Received message:", msg)
        
        # Parse message and prepare data for DataFrame
        measurement, tags, fields, timestamp = parse_influxdb_line(msg)
        entry = {**tags, **fields, "timestamp": timestamp, "measurement": measurement}
        data.append(entry)

except KeyboardInterrupt:
    print("Stopping consumer")
    stop_event.set()  # Signal the timer to not restart
    handle_batch()  # Process any remaining data before stopping
finally:
    consumer.close()  # Ensure consumer resources are cleanly released
    print("Consumer closed and resources released.")
