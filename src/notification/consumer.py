import os
import sys
import pika
import logging
from dotenv import load_dotenv
from send import email

# Load environment variables from .env
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def main():
    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        queue_name = os.getenv("MP3_QUEUE", "mp3")

        logging.info(f"Connecting to RabbitMQ at {rabbitmq_host}...")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)
        logging.info(f"Listening on queue: {queue_name}")

        def callback(ch, method, properties, body):
            logging.info("📥 New task received for MP3 email notification")
            err = email.notification(body)
            if err:
                logging.error(f"❌ Email notification failed: {err}")
                ch.basic_nack(delivery_tag=method.delivery_tag)
            else:
                logging.info("✅ Email notification sent successfully")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        logging.info("🚀 Consumer started. Waiting for messages... (Press CTRL+C to stop)")
        channel.start_consuming()

    except Exception as e:
        logging.critical(f"🔥 Fatal error in consumer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("🛑 Consumer stopped by user.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
