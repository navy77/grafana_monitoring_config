from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata

consumer = KafkaConsumer(
    'telegraf',
    bootstrap_servers=['localhost:9093'],
    auto_offset_reset='earliest',
    group_id='my-consumer-group',
    enable_auto_commit=False
)

try:
    print("Starting the consumer")
    for message in consumer:
        print("Received message:", message.value.decode('utf-8'))
        
        # Assume processing happens here

        # Correctly setup the offset commit
        tp = TopicPartition(message.topic, message.partition)
        # OffsetAndMetadata is used here to include metadata (optional) along with the offset
        offsets = {tp: OffsetAndMetadata(message.offset + 1, None)}
        
        # Committing the offset
        consumer.commit(offsets=offsets)

except KeyboardInterrupt:
    print("Stopping consumer")
finally:
    consumer.close()
