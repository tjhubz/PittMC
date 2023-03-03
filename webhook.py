import os
from mcrcon import MCRcon
from flask import Flask,request,json,Response

route = os.getenv("route")
rcon_ip = os.getenv("rcon_ip")
rcon_pass = os.getenv("rcon_pass")
app = Flask(__name__)
mcr = MCRcon(f'{rcon_ip}', f'{rcon_pass}')

@app.route(f'{route}', methods=['POST'])
def return_response():
     print(request.json);
     data = request.json
     mcr.connect()
     resp = mcr.command(f'whitelist add {data["username"]}')
     print(resp)
     mcr.disconnect()
     return Response(response=f'{resp}.',status=200)


if __name__ == "__main__": 
     app.run(debug=True,host="0.0.0.0")