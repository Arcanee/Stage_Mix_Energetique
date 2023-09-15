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

    with open(dataPath+"game_data/{}/{}/save_tmp.json".format(group, team), "r") as src:
        newSave = json.load(src)  

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

        
        
        # VERIF ANNEE / STOCK / CARTE / CAPACITE LEGITIMES
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



        # TRAITEMENT SUPPLEMENTAIRE POUR LE NUCLEAIRE AU 1ER TOUR
        if data["annee"] == 2030:
            save["hdf"]["centraleNuc"][0:6] = [1995,1995,1995,1995,1995,1995]
            save["occ"]["centraleNuc"][0:2] = [2020,2020]
            save["naq"]["centraleNuc"][0:6] = [1995,1995,1995,1995,2000,2000]
            save["pac"]["centraleNuc"][0:8] = [2000,2000,2000,2000,2000,2000,2000,2000]
            save["cvl"]["centraleNuc"][0:7] = [2005,2005,2005,2005,2005,2005,2005]
            save["bfc"]["centraleNuc"][0:2] = [2005,2005]
            save["est"]["centraleNuc"][0:5] = [2005,2010,2010,2010,2010]
            save["ara"]["centraleNuc"][0:3] = [2010,2010,2010]
            save["nor"]["centraleNuc"][0:8] = [2010,2010,2010,2020,2020,2020,2020,2020]


        # CALCUL NOMBRE DE NOUVEAU PIONS + TOTAL A CE TOUR
        nvPionsReg = {
            "hdf": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "idf": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "est": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "nor": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "occ": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "pac": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "bre": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "cvl": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "pll": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "naq": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "ara": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "bfc": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}, 
            "cor": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0, "methanation": 0, "EPR2": 0, "biomasse": 0}
        }

        nvPions = {
            "eolienneON": 0,
            "eolienneOFF": 0,
            "panneauPV": 0,
            "methanation": 0,
            "EPR2": 0,
            "biomasse": 0
        }

        nbPions = {
            "eolienneON": 0,
            "eolienneOFF": 0,
            "panneauPV": 0,
            "methanation": 0,
            "centraleNuc": 0,
            "EPR2" : 0,
            "biomasse": 0
        }

        for reg in save["capacite"]:
            nbPions["centraleNuc"] += data[reg]["centraleNuc"]
        if data["annee"] == 2030 and nbPions["centraleNuc"] != 47:
            raise exc.errMixInit
        else:
            nbPions["centraleNuc"] = 0


        for reg in save["capacite"]:
            for p in data[reg]:
                nbPions[p] += data[reg][p]

                if p == "eolienneON" or p == "eolienneOFF":
                    eolSuppr = len(save[reg][p]) - data[reg][p]
                    for i in range(eolSuppr):
                        save[reg][p].remove(data["annee"]-15)
                        
                if p != "centraleNuc":
                    nvPionsReg[reg][p] = data[reg][p] - len(save[reg][p])
                    nvPions[p] += data[reg][p] - len(save[reg][p])
                    
                    for i in range(nvPionsReg[reg][p]):
                        save[reg][p].append(data["annee"])
                else:
                    nucSuppr = len(save[reg][p]) - data[reg][p]
                    for i in range(nucSuppr):
                        save[reg][p].remove(data["annee"]-40)

        
        if data["alea"] == "MECS3":
            if nvPions["EPR2"] > 0:
                errDetails = nvPions["EPR2"]
                raise exc.errNuc
                

        strat_stockage.strat_stockage_main(data, save, nbPions, nvPions, nvPionsReg, group, team)
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
    except exc.errMixInit:
        resp = ["errMixInit", None]

    except:
        resp = ["err", None]

        with open(dataPath+'logs.txt', 'a') as logs:
            logs.write("[{}] {} \n".format(datetime.datetime.now(), traceback.format_exc()))

    resp = jsonify(resp)

    return resp



# TESTS EN LOCAL:

if __name__ == "__main__":
    app.run(debug=True)