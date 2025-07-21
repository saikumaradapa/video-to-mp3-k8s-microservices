import os
import json
import logging
import gridfs
import pika
from flask import Flask, request
from flask_pymongo import PyMongo

from auth import validate
from auth_svc import access
from storage import util

# Set up logging
logging.basicConfig(level=logging.INFO)

server = Flask(__name__)
server.config["MONGO_URI"] = os.getenv("MONGO_URI")

try:
    mongo = PyMongo(server)
    videos_db = mongo.cx["videos"]
    videos_db["init_collection"].insert_one({"init": True})
    videos_db["init_collection"].delete_many({"init": True})
    fs = gridfs.GridFS(videos_db)
except Exception as e:
    logging.error(f"MongoDB initialization failed: {e}")
    raise SystemExit("MongoDB connection failed.")

try:
    params = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=5672,
        heartbeat=30,  # Set to a value < 60s timeout (default)
        blocked_connection_timeout=300
    )
    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    channel.queue_declare(queue="video", durable=True)
    channel.queue_declare(queue="mp3", durable=True)

except Exception as e:
    logging.error(f"RabbitMQ connection failed: {e}")
    raise SystemExit("RabbitMQ connection failed.")


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    return token if not err else err


@server.route("/upload", methods=["POST"])
def upload():
    access_token, err = validate.token(request)
    if err:
        return err

    access_data = json.loads(access_token)
    if not access_data.get("admin"):
        return "not authorized", 401

    if len(request.files) != 1:
        return "exactly 1 file required", 400

    for _, file in request.files.items():
        err = util.upload(file, fs, channel, access_data)
        if err:
            return err

    return "success", 200


@server.route("/download", methods=["GET"])
def download():
    return "Not implemented", 501


if __name__ == "__main__":
    server.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        debug=os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    )
