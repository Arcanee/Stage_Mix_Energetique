import numpy as np
from collections import Counter
import cv2 as cv
import sys
import json

def prod_main():

    fdcEolON = {"hdf" : 0.29,
                "idf" : 0.37,
                "bre" : 0.26,
                "pll" : 0.23,
                "cvl" : 0.23,
                "bfc" : 0.2,
                "pac" : 0.22,
                "occ" : 0.25,
                "naq" : 0.22,
                "est" : 0.18,
                "ara" : 0.19,
                "nor" : 0.3,
                "cor" : 0.23}
    
    fdcEolOFF = {"hdf" : 0.45,
                "idf" : 0,
                "bre" : 0.45,
                "pll" : 0.42,
                "cvl" : 0,
                "bfc" : 0,
                "pac" : 0.45,
                "occ" : 0.48,
                "naq" : 0.49,
                "est" : 0,
                "ara" : 0,
                "nor" : 0.45,
                "cor" : 0.24}
    
    fdcPV = {"hdf" : 0.14,
            "idf" : 0.15,
            "bre" : 0.15,
            "pll" : 0.16,
            "cvl" : 0.15,
            "bfc" : 0.16,
            "pac" : 0.19,
            "occ" : 0.17,
            "naq" : 0.16,
            "est" : 0.15,
            "ara" : 0.18,
            "nor" : 0.15,
            "cor" : 0.19}

    fdc = { "panneauPV" : fdcPV,
            "eolienneON" : fdcEolON,
            "eolienneOFF" : fdcEolOFF}

    # Hours yearly
    hy = 8760

    # MW
    power = {"panneauPV" : 300,
             "eolienneON" : 140,
             "eolienneOFF" : 480}
    
    prodPanneauPV = {}
    for reg in fdcPV:
        prodPanneauPV[reg] = fdcPV[reg]/100 * power["panneauPV"] * hy

    prodEolienneON = {}
    for reg in fdcEolON:
        prodEolienneON[reg] = fdcEolON[reg]/100 * power["eolienneON"] * hy
    
    prodEolienneOFF = {}
    for reg in fdcEolOFF:
        prodEolienneOFF[reg] = fdcEolOFF[reg]/100 * power["eolienneOFF"] * hy

    # MWh / an
    prod = {}
    for reg in fdcPV:
        prod[reg] = {}
        for pion in power:
            prod[reg][pion] = int (fdc[pion][reg] / 100 * power[pion] * hy)

    
    with open("production_output.json", "w") as f:
        json.dump(prod, f)