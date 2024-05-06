from kafka import KafkaConsumer

# Setup Kafka Consumer
consumer = KafkaConsumer(
    'telegraf',  # Change this to the Kafka topic you want to subscribe to
    bootstrap_servers=['localhost:9093'],  # Change this to your Kafka server address if different
    auto_offset_reset='earliest',  # To read messages from the beginning of the topic
    group_id='my-consumer-group',  # Consumer group ID
    enable_auto_commit=True  # Automatic offset committing
)

# Consume messages
try:
    print("Starting the consumer")
    for message in consumer:
        # Decode the message (assuming it's in UTF-8) and print it
        print(f"Received message: {message.value.decode('utf-8')}")
except KeyboardInterrupt:
    print("Stopping consumer")
finally:
    consumer.close()  # Clean up and close the connection when done or interrupted
