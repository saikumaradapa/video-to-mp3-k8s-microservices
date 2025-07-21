import os
import json
import tempfile
import logging
from bson.objectid import ObjectId
from moviepy.editor import VideoFileClip
import pika

def start(message, fs_videos, fs_mp3s, channel):
    try:
        message = json.loads(message)
        video_fid = message.get("video_fid")

        if not video_fid:
            raise ValueError("Missing 'video_fid' in message")

        # Temporary file for video
        with tempfile.NamedTemporaryFile(delete=False) as tf_video:
            out = fs_videos.get(ObjectId(video_fid))
            tf_video.write(out.read())
            temp_video_path = tf_video.name

        logging.info(f"Extracting audio from video: {video_fid}")
        audio = VideoFileClip(temp_video_path).audio

        # Save MP3 to temp file
        temp_mp3_path = os.path.join(tempfile.gettempdir(), f"{video_fid}.mp3")
        audio.write_audiofile(temp_mp3_path)

        # Save MP3 in MongoDB
        with open(temp_mp3_path, "rb") as f:
            fid = fs_mp3s.put(f.read())

        # Cleanup temp files
        os.remove(temp_video_path)
        os.remove(temp_mp3_path)

        # Update message and publish to next queue
        message["mp3_fid"] = str(fid)
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("MP3_QUEUE", "mp3"),
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )

        logging.info(f"MP3 file stored and published: {fid}")
        return None

    except Exception as err:
        logging.error(f"Conversion failed: {err}")
        if 'fid' in locals():
            fs_mp3s.delete(fid)
        return "failed to convert or publish"
