import os
import json
import pika

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        return f"internal server error while saving video: {err}", 500

    # Manually process pika heartbeats
    channel.connection.process_data_events()

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("VIDEO_QUEUE", "video"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs.delete(fid)
        return f"internal server error while queuing video: {err}", 500
