from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from detection_coord import *
import base64
import json

#Set up Flask:
app = Flask(__name__)

#Bypass CORS at the front end:
cors = CORS(app)
CORS(app, support_credentials=True)

#Create the receiver API POST endpoint:
@app.route("/receiver", methods=["POST"])
@cross_origin(supports_credentials=True)
def imgProcess():
    data = request.get_json()
    b64str = data['image'].partition(",")[2]
    data = jsonify(data)
    
    img = base64.b64decode(b64str + "==")
    with open('image.png', 'wb') as imgFile:
        imgFile.write(img)

    try:
        coord_main()
        with open("data_output.json", "r") as readOutput:
            result = ["detection_success", json.load(readOutput)]
    except:
        result = ["detection_error", None]


    return result

#Run the app:
if __name__ == "__main__": 
   app.run()