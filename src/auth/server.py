import os
import jwt
import datetime
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

server = Flask(__name__)

# MySQL Configuration
server.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
server.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "auth_user")
server.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "auth123")
server.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "auth")
server.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", 3306))

mysql = MySQL(server)

# JWT Secret
JWT_SECRET = os.getenv("JWT_SECRET", "secret")


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"error": "Missing credentials in the request"}), 401

    try:
        cur = mysql.connection.cursor()
        res = cur.execute(
            "SELECT email, password FROM user WHERE email = %s", (auth.username,)
        )

        if res == 0:
            return jsonify({"error": "Credentials not found"}), 404

        email, password = cur.fetchone()

        if auth.password != password:
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_jwt(auth.username, JWT_SECRET, True)
        return jsonify({"token": token})

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@server.route("/validate", methods=["POST"])
def validate():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify(decoded), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Not authorized"}), 403


def create_jwt(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256"
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
