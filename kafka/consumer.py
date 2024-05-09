from kafka import KafkaConsumer
import pandas as pd

# Setup Kafka Consumer
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
    tags = {}
    for tag in tag_parts:
        key, value = tag.split('=')
        tags[key] = value

    field_data = {}
    for field in fields.split(','):
        key, value = field.split('=')
        field_data[key] = float(value)

    return measurement, tags, field_data, timestamp

data = []

# Consume messages
try:
    print("Starting the consumer")
    for message in consumer:
        msg = message.value.decode('utf-8')
        print("Received message:", msg)
        measurement, tags, fields, timestamp = parse_influxdb_line(msg)

        # Prepare data for DataFrame
        entry = {**tags, **fields, "timestamp": timestamp, "measurement": measurement}
        data.append(entry)
        if len(data) >= 10:  # Example: Process after collecting 10 messages.
            break

except KeyboardInterrupt:
    print("Stopping consumer")
finally:
    consumer.close()  # Clean up and close the connection when done or interrupted

# Convert list of dictionaries to DataFrame
if data:
    df = pd.DataFrame(data)
    print(df)
else:
    print("No data collected")