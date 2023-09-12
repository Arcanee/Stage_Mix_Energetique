from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_cors import CORS, cross_origin
import detection
import strat_stockage
import base64
import json
import datetime
import traceback
import exc
from constantes import *


# with open(dataPath+'logs.txt', 'a') as logs:
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


@app.route('/get_mix')
@cross_origin(support_credentials=True)
def get_mix():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    with open(dataPath+"game_data/{}/{}/mix.json".format(group, team), "r") as f:
        mix = json.load(f)

    return jsonify(mix)


@app.route('/get_detection')
@cross_origin(support_credentials=True)
def get_detection():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    with open(dataPath+"game_data/{}/{}/detection.json".format(group, team), "r") as f:
        detection = json.load(f)

    return jsonify(detection)


@app.route('/get_results')
@cross_origin(support_credentials=True)
def get_results():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    with open(dataPath+"game_data/{}/{}/resultats.json".format(group, team), "r") as f:
        resultats = json.load(f)

    return jsonify(resultats)


@app.route('/set_group', methods=["POST"])
@cross_origin(support_credentials=True)
def set_group():
    try:
        data = request.get_json()
        group = data[0]
        team = data[1]
        action = data[2]

        resp = make_response(jsonify(["log_in_success"]))
        resp.set_cookie(key="groupe", value=group, samesite="Lax")
        resp.set_cookie(key="equipe", value=team, samesite="Lax")

        if action == "new":
            with open(dataPath+"game_data/save_init.json", "r") as src:
                newSave = json.load(src)
            with open(dataPath+"game_data/{}/{}/save.json".format(group, team), "w") as dst:
                json.dump(newSave, dst)

            with open(dataPath+"game_data/mix_init.json", "r") as src:
                newMix = json.load(src)
            with open(dataPath+"game_data/{}/{}/mix.json".format(group, team), "w") as dst:
                json.dump(newMix, dst)

            with open(dataPath+"game_data/resultats_init.json", "r") as src:
                newResultats = json.load(src)
            with open(dataPath+"game_data/{}/{}/resultats.json".format(group, team), "w") as dst:
                json.dump(newResultats, dst)

    except:
        resp = jsonify(["log_in_error"])

        with open(dataPath+'logs.txt', 'a') as logs:
            logs.write("[{}] {} \n".format(datetime.datetime.now(), traceback.format_exc()))

    return resp


@app.route('/photo')
@cross_origin(support_credentials=True)
def photo_html():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    if (group is None) or (team is None):
        resp = make_response(redirect("/"))
    else:
        resp = make_response(render_template("photo.html"))
    
    return resp

@app.route('/photo/')
@cross_origin(support_credentials=True)
def photo_bis_html():
    return redirect("/photo")



@app.route('/detection')
@cross_origin(support_credentials=True)
def detection_html():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    if (group is None) or (team is None):
        resp = make_response(redirect("/"))
    else:
        resp = make_response(render_template("detection.html"))
    
    return resp

@app.route('/detection/')
@cross_origin(support_credentials=True)
def detection_bis_html():
    return redirect("/detection")


@app.route('/manual')
@cross_origin(support_credentials=True)
def manual_html():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    if (group is None) or (team is None):
        resp = make_response(redirect("/"))
    else:
        resp = make_response(render_template("manual.html"))
    
    return resp

@app.route('/manual/')
@cross_origin(support_credentials=True)
def manual_bis_html():
    return redirect("/manual")



@app.route('/results')
@cross_origin(support_credentials=True)
def results_html():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    if (group is None) or (team is None):
        resp = make_response(redirect("/"))
    else:
        resp = make_response(render_template("results.html"))
    
    return resp

@app.route('/results/')
@cross_origin(support_credentials=True)
def results_bis_html():
    return redirect("/results")


@app.route("/commit")
@cross_origin(supports_credentials=True)
def commitResults():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")    

    if newSave["annee"] == 2055:
        with open(dataPath+"game_data/mix_init.json", "r") as src:
            newMix = json.load(src)
        with open(dataPath+"game_data/{}/{}/mix.json".format(group, team), "w") as dst:
            json.dump(newMix, dst)

        with open(dataPath+"game_data/resultats_init.json", "r") as src:
            newResultats = json.load(src)
        with open(dataPath+"game_data/{}/{}/resultats.json".format(group, team), "w") as dst:
            json.dump(newResultats, dst)

        with open(dataPath+"game_data/save_init.json".format(group), "r") as src:
            newSave = json.load(src)
    else:
        with open(dataPath+"game_data/{}/{}/save_tmp.json".format(group, team), "r") as src:
            newSave = json.load(src)


    with open(dataPath+"game_data/{}/{}/save.json".format(group, team), "w") as dst:
        json.dump(newSave, dst)
    
    return redirect("/photo")


#Create the detector API POST endpoint:
@app.route("/detector", methods=["POST"])
@cross_origin(supports_credentials=True)
def imgProcess():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    team = int(team)

    data = request.get_json()
    b64str = data['image'].partition(",")[2]
    img = base64.b64decode(b64str + "==")
    # Padding --> https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding

    with open(dataPath+"game_data/{}/{}/image.png".format(group, team), 'wb') as imgFile:
        imgFile.write(img)

    try:
        detection.detection_main(group, team)
        resp = ["success"]
        
        with open(dataPath+"game_data/{}/{}/mix.json".format(group, team), "r") as f:
            mix = json.load(f)
        mix["actif"] = False
        with open(dataPath+"game_data/{}/{}/mix.json".format(group, team), "w") as f:
            json.dump(mix, f)

    except:
        resp = ["error", None]

        with open(dataPath+'logs.txt', 'a') as logs:
            logs.write("[{}] Groupe {} Equipe {} \n {} \n".format(datetime.datetime.now(), group, team, traceback.format_exc()))

    resp = jsonify(resp)

    return resp


#Create the production API POST endpoint:
@app.route("/production", methods=["POST"])
@cross_origin(supports_credentials=True)
def prodCompute():
    group = request.cookies.get("groupe")
    team = request.cookies.get("equipe")

    team = int(team)

    data = request.get_json()
    errDetails = 0

    try:
        with open(dataPath+"game_data/{}/{}/save.json".format(group, team), "r") as f:
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
                

        strat_stockage.strat_stockage_main(data, group, team)
        resp = ["success"]


        with open(dataPath+"game_data/{}/{}/mix.json".format(group, team), "w") as dst:
            json.dump(data, dst)

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

        with open(dataPath+'logs.txt', 'a') as logs:
            logs.write("[{}] {} \n".format(datetime.datetime.now(), traceback.format_exc()))

    resp = jsonify(resp)

    return resp