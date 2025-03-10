import os
import json
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic

from src.Gateway import Gateway

BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': 'dev',
    'auto.offset.reset': 'latest'
}
gateway = Gateway()
class VideoCreatedKafkaConsumer():

    @staticmethod
    def consume_messages(consumer):
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                print(f"Received message: {msg.value().decode('utf-8')}")
                video_created_json = json.loads(msg.value().decode('utf-8'))
                gateway.process_video_created(video_created_json["location"])

        except KeyboardInterrupt:
            print("Consuming interrupted.")
        finally:
            consumer.close()

    @staticmethod
    def create_if_not_exists(admin, topic_name):
        metadata = admin.list_topics(timeout=10)
        if topic_name in metadata.topics:
            print(f"Topic '{topic_name}' exists.")
            return topic_name
        else:
            print(f"Topic '{topic_name}' does not exist. Creating it...")
            new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)

            admin.create_topics([new_topic])
            print(f"Topic '{topic_name}' created.")
            return topic_name


    def run(self):
        admin = AdminClient(KAFKA_CONFIG)
        consumer = Consumer(KAFKA_CONFIG)

        video_created_topic = 'video.created'
        video_created_topic = self.create_if_not_exists(admin, video_created_topic)

        consumer.subscribe([video_created_topic])
        self.consume_messages(consumer)

if __name__ == "__main__":
    runner = VideoCreatedKafkaConsumer()
    runner.run()