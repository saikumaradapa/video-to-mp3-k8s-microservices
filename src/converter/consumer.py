import gridfs
import os
import pika
import sys

from dotenv import load_dotenv
from pymongo import MongoClient

from convert import to_mp3

load_dotenv(".env")


def main():
    # mongodb
    client = MongoClient(os.getenv("K8S_HOST"), 27017)
    db_videos = client.videos
    db_mp3s = client.mp3

    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)  # negative ack
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.getenv("VIDEO_QUEUE"),
        on_message_callback=callable
    )

    print("waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
