from src.kafka.VideoCreatedKafkaConsumer import VideoCreatedKafkaConsumer

VIDEO_CREATED_CONSUMER = VideoCreatedKafkaConsumer()

if __name__ == "__main__":
    VIDEO_CREATED_CONSUMER.run()
