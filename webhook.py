import os
from rcon import Client
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth

route = os.getenv("route", "/default_route")
rcon_ip = os.getenv("rcon_ip")
rcon_port = int(os.getenv("rcon_port", 25575))
rcon_pass = os.getenv("rcon_pass")
app = Flask(__name__)
auth = HTTPBasicAuth()

auth_username = os.getenv("AUTH_USERNAME")
auth_password = os.getenv("AUTH_PASSWORD")

@auth.verify_password
def verify_password(username, password):
    if username == auth_username and password == auth_password:
        return username
    return None

@app.route(route, methods=['POST'])
@auth.login_required
def return_response():
    data = request.get_json()

    if data is None or "username" not in data:
        return jsonify({"error": "Invalid JSON or missing 'username' field."}), 400

    game_type = request.headers.get("type")

    if game_type not in ["java", "bedrock"]:
        return jsonify({"error": "Invalid game type"}), 400

    username = data["username"]

    if game_type == "bedrock":
        username = f".{username.replace(' ', '_')}"

    try:
        with Client(rcon_ip, rcon_port, passwd=rcon_pass) as client:
            resp = client.run(f'whitelist add {username}')
            if "already whitelisted" in resp:
                return jsonify({"response": resp, "status": "Already Whitelisted"}), 200
            elif "Added" in resp:
                return jsonify({"response": resp, "status": "Whitelisted"}), 200
            else:
                return jsonify({"error": "An unexpected response was received.", "response": resp}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")