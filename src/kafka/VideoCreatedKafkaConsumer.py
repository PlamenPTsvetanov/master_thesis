import os
import threading

from confluent_kafka import Consumer

BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': 'dev',
    'auto.offset.reset': 'latest'
}


def consume_messages():
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe(['video.created'])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            print(f"Received message: {msg}")
    finally:
        consumer.close()


consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()
