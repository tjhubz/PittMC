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

@app.route("/", methods=['GET'])
def default_route():
    return jsonify({"status": "error", "response": "You must be lost!"}), 404

@app.route(route, methods=['POST'])
@auth.login_required
def return_response():
    data = request.get_json()

    if data is None or "username" not in data or "type" not in data:
        return jsonify({"status": "error", "response": "Invalid JSON or missing 'username' or 'type' field."}), 400

    game_type = data["type"]
    if game_type not in ["java", "bedrock"]:
        return jsonify({"status": "error", "response": "Invalid game type."}), 400

    username = data["username"]

    if game_type == "bedrock":
        username = "." + username.replace(" ", "_")

    try:
        with Client(rcon_ip, rcon_port, passwd=rcon_pass) as client:
            resp = client.run(f'whitelist add {username}')
            if "already whitelisted" in resp:
                status_msg = "Already Whitelisted"
                status_code = 200
            elif "Added" in resp:
                status_msg = "Whitelisted"
                status_code = 200
            elif "does not exist" in resp:
                status_msg = "Player Not Found"
                status_code = 400
            else:
                status_msg = "error"
                status_code = 500
            print(f"Result: {status_msg}")
            return jsonify({"status": status_msg, "response": resp}), status_code
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "response": "An unknown error occurred while processing the request."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")