from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_cors import CORS, cross_origin
import detection
import strat_stockage
import base64
import json
import datetime
import traceback
import exc

# with open('/var/www/html/flaskapp/logs.txt', 'a') as logs:
#     logs.write("[{}] error: {} \n".format(datetime.datetime.now(), traceback.format_exc()))

#Set up Flask:
app = Flask(__name__)

#Bypass CORS at the front end:
cors = CORS(app)
CORS(app, support_credentials=True)



@app.route('/')
@cross_origin(support_credentials=True)
def home_html():
    return render_template("index.html")



@app.route('/set_group', methods=["POST"])
@cross_origin(support_credentials=True)
def group_cookie():
    try:
        data = request.get_json()
        group = data[0]
        action = data[1]

        resp = make_response(jsonify(["log_in_success"]))
        resp.set_cookie(key="groupe", value=group, samesite="Lax")

        if action == "new":
            with open("/var/www/html/flaskapp/game_data/save_template.json".format(group), "r") as src:
                newSave = json.load(src)
            with open("/var/www/html/flaskapp/game_data/groupe{}/save.json".format(group), "w") as dst:
                json.dump(newSave, dst)

    except:
        resp = jsonify(["log_in_error"])

        with open('/var/www/html/flaskapp/logs.txt', 'a') as logs:
            logs.write("[{}] {} \n".format(datetime.datetime.now(), traceback.format_exc()))

    return resp


@app.route('/photo')
@cross_origin(support_credentials=True)
def photo_html():
    group = request.cookies.get("groupe")

    if group is None:
        resp = make_response(redirect("http://apps-gei.insa-toulouse.fr/"))
    else:
        resp = make_response(render_template("photo.html"))
    
    return resp

@app.route('/photo/')
@cross_origin(support_credentials=True)
def photo_bis_html():
    return redirect("http://apps-gei.insa-toulouse.fr/photo")



@app.route('/detection')
@cross_origin(support_credentials=True)
def detection_html():
    group = request.cookies.get("groupe")

    if group is None:
        resp = make_response(redirect("http://apps-gei.insa-toulouse.fr/"))
    else:
        resp = make_response(render_template("detection.html"))
    
    return resp

@app.route('/detection/')
@cross_origin(support_credentials=True)
def detection_bis_html():
    return redirect("http://apps-gei.insa-toulouse.fr/detection")


@app.route('/manual')
@cross_origin(support_credentials=True)
def manual_html():
    group = request.cookies.get("groupe")

    if group is None:
        resp = make_response(redirect("http://apps-gei.insa-toulouse.fr/"))
    else:
        resp = make_response(render_template("manual.html"))
    
    return resp

@app.route('/manual/')
@cross_origin(support_credentials=True)
def manual_bis_html():
    return redirect("http://apps-gei.insa-toulouse.fr/manual")



@app.route('/results')
@cross_origin(support_credentials=True)
def results_html():
    group = request.cookies.get("groupe")

    if group is None:
        resp = make_response(redirect("http://apps-gei.insa-toulouse.fr/"))
    else:
        resp = make_response(render_template("results.html"))
    
    return resp

@app.route('/results/')
@cross_origin(support_credentials=True)
def results_bis_html():
    return redirect("http://apps-gei.insa-toulouse.fr/results")


@app.route("/commit")
@cross_origin(supports_credentials=True)
def commitResults():
    group = request.cookies.get("groupe")

    with open("/var/www/html/flaskapp/game_data/groupe{}/save_tmp.json".format(group), "r") as src:
        newSave = json.load(src)

    if newSave["annee"] == 2055:
        with open("/var/www/html/flaskapp/game_data/save_template.json".format(group), "r") as src:
            newSave = json.load(src)

    with open("/var/www/html/flaskapp/game_data/groupe{}/save.json".format(group), "w") as dst:
        json.dump(newSave, dst)
    
    return redirect("http://apps-gei.insa-toulouse.fr/photo")


#Create the detector API POST endpoint:
@app.route("/detector", methods=["POST"])
@cross_origin(supports_credentials=True)
def imgProcess():
    group = request.cookies.get("groupe")

    if group is None:
        resp = make_response(redirect("http://apps-gei.insa-toulouse.fr/"))

    else:
        group = int(group)
        data = request.get_json()
        b64str = data['image'].partition(",")[2]
        img = base64.b64decode(b64str + "==")

        with open('/var/www/html/flaskapp/static/img/image_groupe_{}.png'.format(group), 'wb') as imgFile:
            imgFile.write(img)

        try:
            detection.detection_main(group)
            with open("/var/www/html/flaskapp/game_data/groupe{}/detection_output.json".format(group), "r") as readOutput:
                resp = ["detection_success", json.load(readOutput)]

        except:
            resp = ["detection_error", None]

            with open('/var/www/html/flaskapp/logs.txt', 'a') as logs:
                logs.write("[{}] {} \n".format(datetime.datetime.now(), traceback.format_exc()))

        resp = jsonify(resp)

    return resp


#Create the production API POST endpoint:
@app.route("/production", methods=["POST"])
@cross_origin(supports_credentials=True)
def prodCompute():
    group = request.cookies.get("groupe")

    if group is None:
        resp = make_response(redirect("http://apps-gei.insa-toulouse.fr/"))

    else:
        group = int(group)
        data = request.get_json()
        errDetails = 0

        try:
            with open("/var/www/html/flaskapp/game_data/groupe{}/save.json".format(group), "r") as f:
                save = json.load(f)

                if data["annee"] != save["annee"]:
                    errDetails = save["annee"]
                    raise exc.errAnnee

                if data["stock"] < save["stock"]:
                    errDetails = save["stock"]
                    raise exc.errStock
                    
                if data["annee"] != 2030 and data["carte"] != save["carte"]:
                    errDetails = save["carte"]
                    raise exc.errCarte
                
                for reg in save["capacite"]:
                    for p in save["capacite"][reg]:
                        if data[reg][p] > save["capacite"][reg][p]:
                            errDetails = [reg, p, save["capacite"][reg][p]]
                            raise exc.errSol
                
                if data["alea"] == "MECS3":
                    nbNuc = 0
                    for reg in data:
                        if reg!="annee" and reg!="alea" and reg!="stock" and reg!="carte":
                            nbNuc += data[reg]["centraleNuc"]
                    if nbNuc > save["pions"]["nbNuc"] + save["pionsInit"]["nbNuc"]:
                        errDetails = save["pions"]["nbNuc"] + save["pionsInit"]["nbNuc"]
                        raise exc.errNuc
                    

            strat_stockage.strat_stockage_main(data, group)
            with open("/var/www/html/flaskapp/game_data/groupe{}/production_output.json".format(group), "r") as prod:
                resp = ["success", json.load(prod)]

        except exc.errAnnee:
            resp = ["errAnnee", errDetails]
        except exc.errStock:
            resp = ["errStock", errDetails]
        except exc.errCarte:
            resp = ["errCarte", errDetails]
        except exc.errSol:
            resp = ["errSol", errDetails]
        except exc.errNuc:
            resp = ["errNuc", errDetails]

        except:
            resp = ["err", None]

            with open('/var/www/html/flaskapp/logs.txt', 'a') as logs:
                logs.write("[{}] {} \n".format(datetime.datetime.now(), traceback.format_exc()))

        resp = jsonify(resp)

    return resp


