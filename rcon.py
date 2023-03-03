from mcrcon import MCRcon
from flask import Flask,request,json,Response

user = "Teejers"
app = Flask(__name__)

@app.route('/my_webhook', methods=['POST'])
def return_response():
    print(request.json);
#    with MCRcon("192.168.1.10", "minecraft") as mcr:
#         resp = mcr.command("say "+user)
#         print(resp)
    return Response(status=200)


if __name__ == "__main__": 
     app.run(debug=True)