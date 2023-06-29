from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import detection_cubes
import production
import base64
import json

#Set up Flask:
app = Flask(__name__)

#Bypass CORS at the front end:
cors = CORS(app)
CORS(app, support_credentials=True)

#Create the detector API POST endpoint:
@app.route("/detector", methods=["POST"])
@cross_origin(supports_credentials=True)
def imgProcess():
    data = request.get_json()
    b64str = data['image'].partition(",")[2]
    
    img = base64.b64decode(b64str + "==")
    with open('image.png', 'wb') as imgFile:
        imgFile.write(img)

    try:
        detection_cubes.cubes_main()
        with open("detection_output.json", "r") as readOutput:
            result = ["detection_success", readOutput.readlines()[0]]
    except:
        result = ["detection_error", None]


    return jsonify(result)


#Create the production API POST endpoint:
@app.route("/production", methods=["GET"])
@cross_origin(supports_credentials=True)
def prodCompute():
    try:
        production.prod_main()
        with open("production_output.json", "r") as readOutput:
            result = ["detection_success", json.load(readOutput)]
    except:
        result = ["detection_error", None]


    return jsonify(result)

#Run the app:
if __name__ == "__main__":
   app.run(debug=True)