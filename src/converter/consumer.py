import os
import sys
import pika
import gridfs
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from convert import to_mp3

# Load .env file
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def main():
    try:

        mongo_user = os.getenv("MONGO_USER")
        mongo_pass = os.getenv("MONGO_PASSWORD")

        mongo_host = os.getenv("MONGO_HOST", "localhost")
        mongo_port = int(os.getenv("MONGO_PORT", 27017))

        mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"

        client = MongoClient(mongo_uri)

        db_videos = client[os.getenv("VIDEOS_DB", "videos")]
        db_mp3s = client[os.getenv("MP3_DB", "mp3")]

        fs_videos = gridfs.GridFS(db_videos)
        fs_mp3s = gridfs.GridFS(db_mp3s)

        # RabbitMQ setup
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()

        queue_name = os.getenv("VIDEO_QUEUE", "video")

        channel.queue_declare(queue=queue_name, durable=True)

        def callback(ch, method, properties, body):
            logging.info("Received new video processing task")
            err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
            if err:
                logging.error(f"Processing failed: {err}")
                ch.basic_nack(delivery_tag=method.delivery_tag)
            else:
                logging.info("Successfully processed and converted video to mp3")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        logging.info("Waiting for video messages... (CTRL+C to exit)")
        channel.start_consuming()

    except Exception as e:
        logging.error(f"Fatal error in consumer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Consumer interrupted by user.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
