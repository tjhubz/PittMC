from mcrcon import MCRcon
from flask import Flask,request,json,Response

app = Flask(__name__)
mcr = MCRcon("192.168.1.10", "S6cLQiq7Sy3egLCm")

@app.route('/a447249891ggt352', methods=['POST'])
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