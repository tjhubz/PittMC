import os
from rcon import Client
from flask import Flask, request, jsonify

route = os.getenv("route", "/default_route")
rcon_ip = os.getenv("rcon_ip")
rcon_port = int(os.getenv("rcon_port", 25575))  # Make sure to set the RCON port as an environment variable
rcon_pass = os.getenv("rcon_pass")
app = Flask(__name__)

@app.route(route, methods=['POST'])
def return_response():
    data = request.get_json()

    if data is None or "username" not in data:
        return jsonify({"error": "Invalid JSON or missing 'username' field."}), 400

    username = data["username"]

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