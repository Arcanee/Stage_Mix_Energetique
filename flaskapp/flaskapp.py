from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS, cross_origin
import detection
import strat_stockage
import base64
import json
import datetime
import traceback

# with open('logs.txt', 'a') as logs:
#     logs.write("[{}] Home page OK\n".format(datetime.datetime.now()))

#Set up Flask:
app = Flask(__name__)

#Bypass CORS at the front end:
cors = CORS(app)
CORS(app, support_credentials=True)

@app.route('/')
@cross_origin(support_credentials=True)
def home_html():
    return render_template("index.html")

@app.route('/manual')
@cross_origin(support_credentials=True)
def manual_html():
    return render_template("manual.html")

@app.route('/results')
@cross_origin(support_credentials=True)
def results_html():
    return render_template("results.html")

@app.route('/detection')
@cross_origin(support_credentials=True)
def detection_html():
    return render_template("detection.html")


#Create the detector API POST endpoint:
@app.route("/detector", methods=["POST"])
@cross_origin(supports_credentials=True)
def imgProcess():
    data = request.get_json()
    b64str = data['image'].partition(",")[2]
    img = base64.b64decode(b64str + "==")

    with open('static/img/image.png', 'wb') as imgFile:
        imgFile.write(img)

    try:
        detection.detection_main()
        with open("game_data/detection_output.json", "r") as readOutput:
            result = ["detection_success", json.load(readOutput)]

    except Exception as e:
        result = ["detection_error", None]

        with open('logs.txt', 'a') as logs:
            logs.write("[{}] error: {} \n".format(datetime.datetime.now(), e))

    return jsonify(result)


#Create the production API POST endpoint:
@app.route("/production", methods=["POST"])
@cross_origin(supports_credentials=True)
def prodCompute():
    data = request.get_json()

    try:
        strat_stockage.strat_stockage_main((data))
        with open("game_data/production_output.json", "r") as readOutput:
            result = ["production_success", json.load(readOutput)]

    except Exception as e:
        result = ["production_error", None]

        with open('logs.txt', 'a') as logs:
            logs.write("[{}] error: {} \n".format(datetime.datetime.now(), traceback.format_exc()))

    return jsonify(result)