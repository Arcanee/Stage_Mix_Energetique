import numpy as np
from collections import Counter
import cv2 as cv
import sys
import json
import datetime

def prod_main(data):

    # INIT CALCULS /////////////////////////////

    # Les prod sont annuelles et en GWh

    # x10 car un pion = 10 parcs
    prodEolON= {"hdf" : 355.656 * 10,
                "idf" : 453.768 * 10,
                "bre" : 318.864 * 10,
                "pll" : 282.072 * 10,
                "cvl" : 282.072 * 10,
                "bfc" : 245.28 * 10,
                "pac" : 269.808 * 10,
                "occ" : 306.6 * 10,
                "naq" : 269.808 * 10,
                "est" : 220.752 * 10,
                "ara" : 233.016 * 10,
                "nor" : 367.92 * 10,
                "cor" : 282.072 * 10}
    
    # x5 car un pion = 5 parcs
    prodEolOFF={"hdf" : 1892.16 * 5,
                "idf" : 0,
                "bre" : 1892.16 * 5,
                "pll" : 1766.016 * 5,
                "cvl" : 0,
                "bfc" : 0,
                "pac" : 1892.16 * 5,
                "occ" : 2018.304 * 5,
                "naq" : 2060.352 * 5,
                "est" : 0,
                "ara" : 0,
                "nor" : 1892.16 * 5,
                "cor" : 1009.152 * 5}
    
    # x10 car un pion = 10 parcs
    prodPV={"hdf" : 367.92 * 10,
            "idf" : 394.2 * 10,
            "bre" : 394.2 * 10,
            "pll" : 420.48 * 10,
            "cvl" : 394.2 * 10,
            "bfc" : 420.48 * 10,
            "pac" : 499.32 * 10,
            "occ" : 446.76 * 10,
            "naq" : 420.48 * 10,
            "est" : 394.2 * 10,
            "ara" : 473.04 * 10,
            "nor" : 394.2 * 10,
            "cor" : 499.32 * 10}

    prodPluie= {"hdf" : 8.5,
                "idf" : 65,
                "bre" : 29,
                "pll" : 1.846,
                "cvl" : 32.25,
                "bfc" : 37.769,
                "pac" : 158.75,
                "occ" : 61.993,
                "naq" : 44.281,
                "est" : 419.316,
                "ara" : 191.852,
                "nor" : 18.667,
                "cor" : 48.818}

    prodNuc  = {"hdf" : 6000,
                "idf" : 6000,
                "bre" : 6000,
                "pll" : 6000,
                "cvl" : 6000,
                "bfc" : 6000,
                "pac" : 6000,
                "occ" : 6000,
                "naq" : 6000,
                "est" : 6000,
                "ara" : 6000,
                "nor" : 6000,
                "cor" : 6000}
    
    prodTherm= {"hdf" : 1425,
                "idf" : 1425,
                "bre" : 1425,
                "pll" : 1425,
                "cvl" : 1425,
                "bfc" : 1425,
                "pac" : 1425,
                "occ" : 1425,
                "naq" : 1425,
                "est" : 1425,
                "ara" : 1425,
                "nor" : 1425,
                "cor" : 1425}



    prod = {"panneauPV" : prodPV,
            "eolienneON" : prodEolON,
            "eolienneOFF" : prodEolOFF,
            "barrage" : prodPluie,
            "centrale" : prodNuc,
            "usineCharbon" : prodTherm,
            "usineGaz" : prodTherm}

 


    # RECUP DONNEES PLATEAU /////////////////////////////   

    for p in prod:
        for reg in prod[p]:
            if data[reg][p] == '':
                data[reg][p] = 0
            data[reg][p] = int(int(data[reg][p]) * prod[p][reg])
    
    with open("game_data/production_output.json", "w") as output:
        json.dump(data, output)