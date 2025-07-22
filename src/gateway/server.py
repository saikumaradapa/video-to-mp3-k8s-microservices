import os
import json
import logging
import gridfs
import pika
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from auth import validate
from auth_svc import access
from storage import util

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
server = Flask(__name__)
server.config["MONGO_URI"] = os.getenv("MONGO_URI")

# MongoDB setup
try:
    mongo = PyMongo(server)

    videos_db = mongo.cx[os.getenv("VIDEOS_DB", "videos")]
    videos_db["init_collection"].insert_one({"init": True})
    videos_db["init_collection"].delete_many({"init": True})

    mp3s_db = mongo.cx[os.getenv("MP3_DB", "mp3")]
    mp3s_db["init_collection"].insert_one({"init": True})
    mp3s_db["init_collection"].delete_many({"init": True})

    fs_videos = gridfs.GridFS(videos_db)
    fs_mp3s = gridfs.GridFS(mp3s_db)

except Exception as e:
    logging.error(f"MongoDB initialization failed: {e}")
    raise SystemExit("MongoDB connection failed.")

# RabbitMQ setup
try:
    params = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=5672,
        heartbeat=120,
        blocked_connection_timeout=300,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=os.getenv("VIDEO_QUEUE", "video"), durable=True)
    channel.queue_declare(queue=os.getenv("MP3_QUEUE", "mp3"), durable=True)

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
        err = util.upload(file, fs_videos, channel, access_data)
        if err:
            logging.error(f"Upload failed: {err}")
            return err

    logging.info(f"File uploaded successfully by user: {access_data['username']}")
    return "success", 200


@server.route("/download", methods=["GET"])
def download():
    access_token, err = validate.token(request)
    if err:
        return err

    access_data = json.loads(access_token)
    if not access_data.get("admin"):
        return "not authorized", 401

    fid_string = request.args.get("fid", "").strip()
    if not fid_string:
        return "fid required", 400

    try:
        out = fs_mp3s.get(ObjectId(fid_string))
        return send_file(
            out,
            download_name=f"{fid_string}.mp3",
            as_attachment=True,
            mimetype="audio/mpeg"
        )
    except Exception as err:
        logging.error(f"Download failed: {err}")
        return f"internal server error while fetching mp3 audio: {err}", 500


if __name__ == "__main__":
    server.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        debug=os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    )
