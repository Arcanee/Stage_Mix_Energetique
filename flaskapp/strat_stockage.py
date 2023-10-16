import numpy as np
from collections import Counter
import sys
import json
import pandas as pd
import os
import datetime
from constantes import *


                                #########################
                                ### TOUT EST EN GW(h) ###
                                #########################

np.seterr('raise') # A ENLEVER SUR LE CODE FINAL


# Classe regroupant toutes les technologies de stockage et de production pilotables
#
# @params
# name (str) : nom de la techno
# stored (array) : niveau des stocks a chaque heure
# prod (array) : ce qui est produit chaque heure
# etain (float) : coefficient de rendement a la charge
# etaout (float) : coefficient de rendement a la decharge
# Q (float) : capacite installee (flux sortant)
# S (float) : capacite de charge (flux entrant)
# vol (float) : capacite maximale de stockage
class Techno:
    def __init__(self, name, stored, prod, etain, etaout, Q, S, Vol):
        self.name = name     # nom de la techno
        self.stored = stored # ce qui est stocke
        self.prod = prod     # ce qui est produit
        self.etain = etain     # coefficient de rendement à la charge
        self.etaout = etaout   # coefficient de rendement à la decharge
        self.Q=Q             # capacite installee (flux sortant)
        self.S=S             # capacite de charge d'une techno de stockage (flux entrant)
        self.vol=Vol         # Capacite maximale de stockage de la techno (Volume max)


# Recharge les moyens de stockage quand on a trop d'energie
#
# @params
# tec : technologie de stockage a recharger (batterie, phs, ...)
# k (int) : heure courante
# astocker (float) : qte d'energie a stocker
def load(tec, k, astocker):
    if astocker == 0:
        out = 0

    else:
        temp = min(astocker*tec.etain, tec.vol-tec.stored[k-1], tec.S*tec.etain)
        tec.stored[k:] = tec.stored[k-1] + temp
        out = astocker - temp / tec.etain
    
    return out


# Decharge les moyens de stockage quand on a besoin d'energie
#
# @params
# tec : technologie de stockage a utiliser pour la production (batterie, phs, ...)
# k (int) : heure courante
# aproduire (float) : qte d'energie a fournir
# endmonthlake (array) : qte d'energie restante dans les lacs jusqu'a la fin du mois
# prod (boolean) : indique si l'energie dechargee est a prendre en compte pour la production globale (faux pour les echanges internes)
def unload(tec, k, aproduire, endmonthlake, prod=True):
    if aproduire <= 0:
        out = 0

    else:
        temp = min(aproduire/tec.etaout, tec.stored[k], tec.Q/tec.etaout)

        if tec.name == 'Lake':
            tec.stored[k:int(endmonthlake[k])] = tec.stored[k] - temp
        else:
            tec.stored[k:] = tec.stored[k] - temp

        if prod:
            tec.prod[k] = temp * tec.etaout

        out = aproduire - temp * tec.etaout

    
    return out


# Renvoie la puissance dispo actuellement pour le nucleaire, par rapport a la puissance max
#
# @params
# k (int) : heure courante
def cycle(k):

    # Sur ATH : pas de penurie avec 56 centrales min.
    # Sur ATL : 28 centrales min. (50%)
    # Diviser en 4 ou 8 groupes (plutôt 8 pour les besoins humains)
    # 1/8 = 0.125, 7/8 = 0.875
    # 2180, 2920, 3650, 4400, 5130, 5900, 6732, 7580
    # Tiers de 8760 : 2920(4*730), 5840, 8460
    # DANS le dernier tiers : 50% croissance lineaire min, 25% baisse de 20% prod min/max, 25% arret

    # La production nucleaire est divisee en 8 groupes, chacun a son cycle d'arret. 
    # Dans cette fonction, on regarde dans quel partie du cycle on est pour chaque groupe, 
    # pour calibrer la production min et max.

    H = 8760
    N = 8
    n = 1/N
    
    # Intervalles des 3 parties importantes du cycle, pour chaque groupe
    A_ranges = [((2180+6570)%H,(2180+8030)%H), ((2920+6570)%H,(2920+8030)%H), 
               ((3650+6570)%H,(3650+8030)%H), ((4400+6570)%H,(4400+8030)%H),
               ((5130+6570)%H,(5130+8030)%H), ((5900+6570)%H,(5900+8030)%H),
               ((6732+6570)%H,(6732+8030)%H), ((7580+6570)%H,(7580+8030)%H)]
    
    B_ranges = [((2180+8030)%H,2180), ((2920+8030)%H,2920), ((3650+8030)%H,3650),
               ((4400+8030)%H,4400), ((5130+8030)%H,5130), ((5900+8030)%H,5900),
               ((6732+8030)%H,6732), ((7580+8030)%H,7580)]
    
    C_ranges = [(2180, (2180+730)%H), (2920, (2920+730)%H), (3650, (3650+730)%H),
               (4400, (4400+730)%H), (5130, (5130+730)%H), (5900, (5900+730)%H),
               (6732, (6732+730)%H), (7580, (7580+730)%H)]

    inA = [lower <= k < upper for (lower, upper) in A_ranges]
    inB = [lower <= k < upper for (lower, upper) in B_ranges]
    inC = [lower <= k < upper for (lower, upper) in C_ranges]
    
    sMin = 0
    sMax = 0
    
    # Pour chaque groupe, on regarde sa zone et on ajuste son min et son max
    for i in range(N):
        if inA[i]:
            start = A_ranges[i][0]
            sMin += n * (0.2 + 0.00054795*(k-start))
            sMax += n * 1
        elif inB[i]:
            start = B_ranges[i][0]
            sMin += n * (1 - 0.00027397260274*(k-start))
            sMax += n * (1 - 0.00027397260274*(k-start))
        elif inC[i]:
            sMin += n * 0
            sMax += n * 0
        else:
            sMin += n * 0.2
            sMax += n * 1
    
    return (sMin, sMax)


# Lance la production des centrales nucleaires
#
# @params
# tec : objet à utiliser pour la production  (ici, Techno Nucleaire)
# k (int) : heure courante
# aproduire (float) : qte d'energie a fournir
def nucProd(tec, k, aproduire):
    if aproduire <= 0:
        out = 0

    else:
        # Si la demande est trop faible ou nulle, on produit quand meme à hauteur de 20%
        MinMax = cycle(k)
        Pmin = MinMax[0]
        Pmax = MinMax[1]
        
        if aproduire > tec.Q/tec.etaout * Pmin:
            temp = min(aproduire/tec.etaout, tec.Q*Pmax/tec.etaout)
            tec.prod[k] = temp * tec.etaout
        else:
            tec.prod[k] = tec.Q / tec.etaout * Pmin
        
        out = aproduire - tec.prod[k]
    
    return out


# Lance la production des centrales thermiques
#
# @params
# tec : objet à utiliser pour la production  (ici, Techno Thermique)
# k (int) : heure courante
# aproduire (float) : qte d'energie a fournir
def thermProd(tec, k, aproduire):
    if aproduire <= 0:
        out = 0

    else:
        temp = min(aproduire/tec.etaout, tec.Q/tec.etaout)
        tec.prod[k] = temp * tec.etaout
        out = aproduire - tec.prod[k]
    
    return out


# 1ere methode de calcul des seuils de stock
#
# @params
# y1 (array) : heures avec surplus
# y2 (array) : heures avec penuries
# y3 (array) : heures sans surplus ni penurie 
# stockmax (float) : capacite max des batteries + phs
def certitudeglobal(y1, y2, y3, stockmax):
    certitude_interval = np.zeros(3)
    
    ##distribution ecretage : min, max, moyenne et ecart-type
    if y1[y1!=-1].size > 0:
        emoy = np.mean(y1[y1!=-1]) ##moyenne de l'echantillon //
        eetype = np.std(y1[y1!=-1]) ##ecart-type de l'echantillon //
        certitude_interval[1] = emoy - 2.33 * eetype / np.sqrt(len(y1[y1!=-1])) ##99% sur ecretage (valeur sup de l'IC)
    else:
        # Si jamais de surplus
        certitude_interval[1] = stockmax - 10

    ##distribution penurie : min, max, moyenne, ecart-type
    if y2[y2!=-1].size > 0:
        pmoy = np.mean(y2[y2!=-1])
        petype = np.std(y2[y2!=-1])
        certitude_interval[0] = pmoy + 1.76 * petype / np.sqrt(len(y2[y2!=-1])) ##96% sur penurie (valeur inf de l'IC)
    else:
        # Si jamais de penurie
        certitude_interval[0] = 10
    
    certitude_interval[2] = (certitude_interval[0] + certitude_interval[1]) / 2 ##valeur moyenne entre 98% et 99% 

    return certitude_interval

    
# 2e methode de calcul des seuils de stock
#
# @params
# a (array) : heures avec surplus
# b (array) : heures avec penuries
# c (array) : heures sans surplus ni penurie 
# crit (float) : critere de separation des penuries (ex: si 0.2, on garde 20% des penuries d'un cote, 80% de l'autre)
# mode (str) : vaut 'u' ou 'd' selon qu'on veuille se placer au dessus ou en dessous du seuil
def seuil(a, b, c, crit, mode):
        
    y1 = np.copy(a)
    y2 = np.copy(b)
    y3 = np.copy(c)
    
    
    for i in range (len(y1)):
        y3[i] = -1 if (y1[i]==y3[i] or y2[i]==y3[i]) else y3[i]
        
    
    bestRatio = -1
    bestStock = -1
    
    for s in range(270):
        nbPen = 0
        nbSeuil = 0
    
        for i in range (len(y1)):
            if mode == "u":
                if y1[i] >= s or y3[i] >= s:
                    nbSeuil += 1
                elif y2[i] >= s:
                    nbSeuil += 1
                    nbPen += 1
            else:
                if 0 <= y1[i] <= s or 0 <= y3[i] <= s:
                    nbSeuil += 1
                elif 0 <= y2[i] <= s:
                    nbSeuil += 1
                    nbPen += 1
        
        if nbSeuil != 0:
            ratio = nbPen / nbSeuil
            if abs(ratio-crit) < abs(bestRatio-crit):
                bestRatio = ratio
                bestStock = s
                
    
    return bestStock


# Premiere strat de stockage naive
#
# @params
# prodres (array) : production residuelle sur l'annee
# H (int) : nombre d'heures dans l'annee
# Battery - Nuclear : objets de la classe Techno
# endmonthlake (array) : contient la qte d'energie restante dans les lacs jusqu'a la fin de chaque mois
def StratStockage(prodres, H, Phs, Battery, Gas, Lake, Nuclear, endmonthlake):
    Surplus=np.zeros(H)
    ##Ajout paramètre Penurie
    Manque = np.zeros(H)
    #Definition d'un ordre sur les differentes technologies de stockage et destockage
    Tecstock= {"Phs":Phs , "Battery":Battery , "Gas":Gas}
    Tecstock2= {"Gas":Gas , "Phs":Phs , "Battery":Battery}
        
    Tecdestock= {"Battery":Battery , "Phs":Phs , "Gas":Gas , "Lake":Lake}
    
    for k in range(1,H):
        if prodres[k]>0:
            
            # La production min de nucleaire s'ajoute à la qte d'energie à stocker
            nucMin = nucProd(Nuclear, k, 0)
            Astocker = prodres[k] + abs(nucMin)
            
            for tec in Tecstock:
                Astocker = load(Tecstock[tec], k, Astocker)

            Surplus[k] = Astocker

        else:
            Aproduire = -prodres[k]
            
            Aproduire = nucProd(Nuclear, k, Aproduire)
            
            for tec in Tecdestock:
                Aproduire = unload(Tecdestock[tec], k, Aproduire, endmonthlake)
                
            ##liste penurie --> pour savoir si il y a penurie dans la production d'electricite 
            Manque[k] = Aproduire
                
    return Surplus, Manque


# Strat de stockage optimisee
#
# @params
# prodres (array) : production residuelle sur l'annee
# H (int) : nombre d'heures dans l'annee
# Battery - Nuclear : objets de la classe Techno
# I0, I1, I2 (array) : seuils de stockage dirigeant la strat de stockage, et deduits de la strat naive
# endmonthlake (array) : contient la qte d'energie restante dans les lacs jusqu'a la fin de chaque mois
def StratStockagev2(prodres, H, Phs, Battery, Gas, Lake, Nuclear, I0, I1, I2, endmonthlake):
    Surplus=np.zeros(H)
    ##Ajout paramètre Penurie
    Manque = np.zeros(H)
    
    #Definition d'un ordre sur les differentes technologies de stockage et destockage
    Tecstock2= {"Gas":Gas , "Phs":Phs , "Battery":Battery} ##on stocke du gaz zone 1,2
    Tecstock3= {"Phs":Phs , "Battery":Battery , "Gas":Gas} ## zone 3
    Tecstock4 = {"Battery":Battery , "Phs":Phs , "Gas":Gas} ## zone 4
        
    Tecdestock1= {"Battery":Battery , "Phs":Phs , "Gas":Gas , "Lake":Lake} #zone 1
    Tecdestock2 = {"Phs":Phs , "Battery":Battery , "Gas":Gas , "Lake":Lake} ## zone 2
    Tecdestock3 = {"Gas":Gas , "Battery":Battery , "Phs":Phs , "Lake":Lake} ## zone 3,4
    
    for k in range(H):
        stock_PB = Phs.stored[k] + Battery.stored[k]
        
        # Suivant le niveau de stock, on change l'ordre de de/stockage et on fait du power2gaz ou
        # gaz2power si besoin
        
        if 0 <= stock_PB < I0[k%24] :
            strat_stock = Tecstock4
            strat_destock = Tecdestock3
            qteInit = min(Gas.Q, Phs.S+Battery.S)
            reste = unload(Gas, k, qteInit, endmonthlake, prod=False)
            reste = load(Battery, k, qteInit-reste)
            load(Phs, k, reste)
            
        elif I0[k%24] <= stock_PB < I1[k%24] :
            strat_stock = Tecstock3
            strat_destock = Tecdestock3
            
        elif I1[k%24] <= stock_PB < I2[k%24] :
            strat_stock = Tecstock2
            strat_destock = Tecdestock2
            
        else :
            strat_stock = Tecstock2
            strat_destock = Tecdestock1
            qteInit = min(Phs.Q+Battery.Q, Gas.S)
            reste = unload(Battery, k, qteInit, endmonthlake, prod=False)
            reste = unload(Phs, k, reste, endmonthlake, prod=False)
            load(Gas, k, qteInit-reste)
            
            
        
        if prodres[k]>0 :
            # La production min de nucleaire s'ajoute à la qte d'energie à stocker
            nucMin = nucProd(Nuclear, k, 0)
            Astocker = prodres[k] + abs(nucMin)
            
            for tec in strat_stock:
                Astocker = load(strat_stock[tec], k, Astocker)

            Surplus[k] = Astocker

        else:
            Aproduire = -prodres[k]

            Aproduire = nucProd(Nuclear, k, Aproduire)

            for tec in strat_destock:
                Aproduire = unload(strat_destock[tec], k, Aproduire, endmonthlake)
            
            ##liste penurie --> pour savoir si il y a penurie dans la production d'electricite 
            Manque[k]=Aproduire
            
                
    return Surplus, Manque


# Optimisation de strategie de stockage et de destockage du Mix energetique
#
# @params
# scenario (array) : scenario de consommation heure par heure
# mix (dict) : donnees du plateau
# save (dict) : donnees du tour precedent
# nbPions (dict) : nombre de pions total pour chaque techno
# nvPions (dict) : nombre de nouveaux pions total pour chaque techno ce tour-ci
# nvPionsReg (dict) : nombre de pions total pour chaque techno
# group (str) : groupe de TD de l'equipe qui joue
# team (int) : numero de l'equipe qui joue dans ce groupe
def simulation(scenario, mix, save, nbPions, nvPions, nvPionsReg, group, team):

    H = 8760

    save["carte"] = mix["carte"]
    save["annee"] += 5
    save["stock"] = mix["stock"]


    ##Carte Choix politique --> 1 choix politique parmi les 3 proposes

    #Carte politique A
    if mix["politique"] == "CPA1" :
        save["varConso"] -= 1e4
    if mix["politique"] == "CPA2" :
        save["varConso"] -= 6e3
    
    #Carte politique B
    if mix["politique"] == "CPB1" :
        save["varConso"] += 4.92e3
    
    #Carte politique C
    if mix["politique"] == "CPC1" :
        save["varConso"] -= 2e4
    if mix["politique"] == "CPC2" :
        save["varConso"] -= 6.3e4

    #Carte politique D 
    if mix["politique"] == "CPD1" :
        save["varConso"] += 6.8e4
    if mix["politique"] == "CPD2" :
        save["varConso"] -= 1e4
    
    #Carte politique E
    if mix["politique"] == "CPE1" :
        save["varConso"] +=1.03e5
    if mix["politique"] == "CPE2" :
        save["varConso"] += 6.7e4

    #Carte politique F
    if mix["politique"] == "CPF1" :
        save["varConso"] -= 3.5e4
    if mix["politique"] == "CPF2" :
        save["varConso"] -= 1.3e4

    scenario += np.ones(H)*(save["varConso"]/H)

    #carte alea MEVUAPV  (lance de 1 / 2)
    # if mix["alea"] == "MEVUAPV1" or mix["alea"] == "MEVUAPV2" or mix["alea"] == "MEVUAPV3": 
    #     save["varConso"] = 9e4
    # scenario += np.ones(H) * (save["varConso"]/H)
    
    if mix["alea"] == "MEVUAPV2" or mix["alea"] == "MEVUAPV3":
        save["innovPV"] = 0.15

    #carte alea MEMDA (lance 3)
    if mix["alea"] == "MEMDA3":
        scenario = 0.95 * scenario

    fdc_on = pd.read_csv(dataPath+"mix_data/fdc_on.csv")
    fdc_off = pd.read_csv(dataPath+"mix_data/fdc_off.csv")
    fdc_pv = pd.read_csv(dataPath+"mix_data/fdc_pv.csv")
    
    prodOnshore = np.zeros(H)
    prodOffshore = np.zeros(H)
    prodPV = np.zeros(H)

    # Puissance d'un pion
    powOnshore = 1.4
    powOffshore = 2.4
    powPV = 3

    # On fait la somme des prods par region pour chaque techno (FacteurDeCharge * NbPions * PuissanceParPion)

    for reg in save["capacite"]:
        prodOnshore += np.array(fdc_on[reg]) * mix[reg]["eolienneON"] * powOnshore
        prodPV += np.array(fdc_pv[reg]) * mix[reg]["panneauPV"] * powPV
        if reg!="bfc" and reg!="ara" and reg!="cvl" and reg!="idf" and reg!="est":
            prodOffshore += np.array(fdc_off[reg]) * mix[reg]["eolienneOFF"] * powOffshore

    
    #carte alea MEMFDC (lance 1)
    if mix["alea"] == "MEMFDC1" or mix["alea"] == "MEMFDC2" or mix["alea"] == "MEMFDC3":
        prodOnshore -= (np.array(fdc_on["cvl"]) * mix["cvl"]["eolienneON"] * powOnshore) * 0.1
        

    # Alea +15% prod PV
    prodPV += save["innovPV"] * prodPV



    # Definition des productions electriques des rivières et lacs 
    coefriv = 13
    river = pd.read_csv(dataPath+"mix_data/run_of_river.csv", header=None)
    river.columns = ["heures", "prod2"]
    rivprod = np.array(river.prod2) * coefriv

    lake = pd.read_csv(dataPath+"mix_data/lake_inflows.csv", header=None)
    lake.columns = ["month", "prod2"]
    lakeprod = np.array(lake.prod2)

    # Calcul de ce qui est stocke dans les lacs pour chaque mois
    horlake = np.array([0,31,31+28,31+28+31,31+28+31+30,31+28+31+30+31,31+28+31+30+31+30,31+28+31+30+31+30+31\
                ,31+28+31+30+31+30+31+31,31+28+31+30+31+30+31+31+30,31+28+31+30+31+30+31+31+30+31\
                ,31+28+31+30+31+30+31+31+30+31+30,31+28+31+30+31+30+31+31+30+31+30+31])*24

    storedlake = np.zeros(H)
    endmonthlake = np.zeros(H)
    for k in range(12):
        storedlake[horlake[k]:horlake[k+1]] = 1000*lakeprod[k]
    for k in range(12):
        endmonthlake[horlake[k]:horlake[k+1]] = int(horlake[k+1])


    # Calcul de la production residuelle
    # prodresiduelle = prod2006_offshore + prod2006_onshore + prod2006_pv + rivprod - scenario
    prodresiduelle = prodOffshore + prodOnshore + prodPV + rivprod - scenario


    # Techno params : name, stored, prod, etain, etaout, Q, S, vol

    initGaz = 1000000
    gazBiomasse = nbPions["biomasse"] * 2 * 0.1 * 0.71 * 6200  # nbPions * nbCentraleParPion * puissance * fdc * nbHeures

    #carte alea MEMFDC (lance 2 / 3)
    if mix["alea"] == "MEMFDC3":
        gazBiomasse -= mix["naq"]["biomasse"] * 2 * 0.1 * 0.71 * 6200

    # Definition des differentes technologies
    # Methanation : 1 pion = 10 unites de 100 MW = 1 GW
    P=Techno('Phs', np.ones(H)*16, np.zeros(H), 0.95, 0.9, 9.3, 9.3, 180)
    B=Techno('Battery', np.ones(H)*2, np.zeros(H), 0.9, 0.95, mix["stock"]/10*20.08, (mix["stock"]/10)*20.08, (mix["stock"]/10)*74.14)
    G=Techno('Gaz', np.ones(H)*(initGaz+gazBiomasse), np.zeros(H), 0.59, 0.45, 34.44, 1*nbPions["methanation"], 10000000)    
    L=Techno('Lake', storedlake, np.zeros(H), 1, 1, 10, 10, 2000)

    # Puissance centrales territoire : 18.54 GWe repartis sur 24 centrales (EDF)
    # Rendement meca (inutile ici) : ~35% generalement (Wiki)
    # T = Techno('Centrale thermique', None, np.zeros(H), None, 1, 0.7725*nbTherm, None, None)
    
    # Puissance : 1.08 GWe (EDF)
    # Meme rendement
    #reacteurs nucleaires effectifs qu'après 1 tour
    nbProdNuc = nbPions["centraleNuc"]
    nbProdNuc2 = (nbPions["EPR2"]-nvPions["EPR2"])
    N = Techno('Reacteur nucleaire', None, np.zeros(H), None, 1, 1.08*nbProdNuc + 1.67*nbProdNuc2, None, None)
    
    
    if mix["alea"] == "MEMFDC3" :
        N.Q *= 45 / 60

        
    # resultats de la strat initiale
    # Renvoie Surplus,Penurie et met à jour Phs,Battery,Methanation,Lake,Therm,Nuc
    s, p = StratStockage(prodresiduelle, H, P, B, G, L, N, endmonthlake)
    
    
    #############################
    ## NUAGES DE POINTS POUR OPTIMISER LE STOCKAGE
    
    stockage_PB = np.zeros(365) ##liste qui va servir à enregister les stockages Phs + Battery à l'heure H pour tous les jours
    
    stockmax = B.vol + P.vol ##stockage maximum total = max total stockage Phs + max total stockage Battery    
    
    ##listes pour ecretage : x1 enregistre les jours où le lendemain il y a ecretage
    ##y1 enregistre la valeur du stock Phs + Battery où le lendemain il y a ecretage
    x1 = np.ones(365)*(-1)
    y1 = np.ones(365)*(-1)
    
    ##pareil que precèdemment mais pour lendemains avec penurie
    x2 = np.ones(365)*(-1)
    y2 = np.ones(365)*(-1)
    
    ##pareil que precèdemment mais pour lendemains avec demande satisfaite et sans perte
    x3 = np.ones(365)*(-1)
    y3 = np.ones(365)*(-1)
    
    ##on enlevera les -1 des listes x1, x2, x3, y1, y2, y3 pour ne recuperer que les points essentiels
        
    StockPB = P.stored + B.stored ##valeur des deux stocks 
    
    
    ###############################################################################
    ##Certitude interval pour toutes les heures
    certitude_interval_inf = np.zeros(24)
    certitude_interval_sup = np.zeros(24)
    certitude_interval_med = np.zeros(24)
    
    seuils_top = np.zeros(24)
    seuils_mid = np.zeros(24)
    seuils_bot = np.zeros(24)
    
    for h1 in range(24):
        for jour in range(365): ##on regarde tous les jours de l'annee
        
            stockage_PB[jour]=StockPB[jour*24 + h1] #Au jour jour, valeur du stock Phs + Battery
        
            ##on regarde dans les 24h qui suivent si il y a ecretage, penurie ou aucun des deux
            for h2 in range(24): 
                t = (jour*24 + h1 + h2) % H
                
                if s[t] > 0 and StockPB[t] >= stockmax : ##cas ecretage
                    x1[jour] = jour + 1 ##on note le jour precèdant jour avec ecretage
                    y1[jour] = stockage_PB[jour] ##on note le stock du jour precèdant jour avec ecretage
            
                elif p[t] > 0 : ##cas penurie
                    x2[jour] = jour + 1 ##memes explications mais pour penurie
                    y2[jour] = stockage_PB[jour]
                
                else : ##cas ni ecretage, ni penurie
                    x3[jour] = jour + 1 ##memes explications mais avec ni ecretage, ni penurie
                    y3[jour] = stockage_PB[jour]
                
                if x1[jour] == x2[jour]: ##si ecretage et penurie le meme jour, on considère que c'est une penurie 
                    x1[jour] = -1
                    y1[jour] = -1
            
            
        int_glob = certitudeglobal(y1, y2, y3, stockmax)
        certitude_interval_inf[h1] = int_glob[0]
        certitude_interval_sup[h1] = int_glob[1]
        certitude_interval_med[h1] = int_glob[2]
        
        seuils_top[h1] = seuil(y1, y2, y3, 0.02, "u")
        seuils_bot[h1] = seuil(y1, y2, y3, 0.9, "d")
        seuils_mid[h1] = (seuils_top[h1] + seuils_bot[h1]) / 2
        
    
        
        
    # Renvoie Surplus,Penurie, et met à jour les technos
    
    #Decommenter pour methode 1 (intervalles de confiance)
    s, p = StratStockagev2(prodresiduelle, H, P, B, G, L, N,
                        certitude_interval_inf, certitude_interval_med, certitude_interval_sup, endmonthlake)
    
    #Decommenter pour methode 2 (recherche iterative du meilleur seuil)
    #s,p=StratStockagev2(prodresiduelle, H, P, B, M, L, T, N,
    #                    seuils_bot, seuils_mid, seuils_top, endmonthlake)
    
    
    ####Demande des choix de la fiche Usage à l'utilisateur
    # choix_utilisateur = input("Entrez les valeurs separees par des espaces : ")

    # # Diviser la chaîne en valeurs individuelles
    # liste = choix_utilisateur.split(',')

    # valeurs = [float(valeur) for valeur in liste]

    # # Appeler la fonction avec les valeurs fournies par l'utilisateur
    # d, e = Usages(valeurs)

    

    # Infos qu'on peut retourner (plusieurs axes temporels et 2 strategies sont possibles):
    # - Stock PHS / Batteries 
    # - Combien de surpus / penurie ***
    # - Evolution des seuils
    # - (Mix des 2 premiers points)
    # - Stocks de gaz ***
    # - Courbes de production X demande ***
    # - Prod residuelle
    # - CO2 ***

    prodOn = int(np.sum(prodOnshore))
    prodOff = int(np.sum(prodOffshore))
    prodPv = int(np.sum(prodPV))
    prodEau = int(np.sum(L.prod + rivprod))
    prodNuc = int(np.sum(N.prod))
    prodGaz = int(np.sum(G.prod))
    prodPhs = int(np.sum(P.prod))
    prodBat = int(np.sum(B.prod))

    save["prodOnshore"][str(mix["annee"])] = prodOn
    save["prodOffshore"][str(mix["annee"])] = prodOff
    save["prodPv"][str(mix["annee"])] = prodPv
    save["prodEau"][str(mix["annee"])] = prodEau
    save["prodNucleaire"][str(mix["annee"])] = prodNuc
    save["prodGaz"][str(mix["annee"])] = prodGaz
    save["prodPhs"][str(mix["annee"])] = prodPhs
    save["prodBatterie"][str(mix["annee"])] = prodBat
    


    prodTotale = prodOn + prodOff + prodPv + prodEau + prodNuc + prodGaz + prodPhs + prodBat


    #calcul des productions par region

    nbTherm = 20
    nbThermReg = {
        "hdf" : 0,
        "idf" : 0,
        "est" : 0,
        "nor" : 0,
        "occ" : 0,
        "pac" : 0,
        "bre" : 0,
        "cvl" : 0,
        "pll" : 0,
        "naq" : 0,
        "ara" : 0,
        "bfc" : 0,
        "cor" : 0
    }

    factNuc = 0 if (nbProdNuc + nbProdNuc2 == 0) else prodNuc / (nbProdNuc + nbProdNuc2)

    ##Occitanie
    popOCC = 0.09 ##pourcentage population
    prodOCC = (np.array(fdc_off.occ)*mix["occ"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.occ)*mix["occ"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.occ)*mix["occ"]["panneauPV"]*powPV + 
                (mix["occ"]["EPR2"]-nvPionsReg["occ"]["EPR2"] + mix["occ"]["centraleNuc"]) * factNuc +
                nbThermReg["occ"] * prodGaz / nbTherm)

    ##Nouvelle-Aquitaine
    popNA = 0.09
    prodNA = (np.array(fdc_off.naq)*mix["naq"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.naq)*mix["naq"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.naq)*mix["naq"]["panneauPV"]*powPV + 
                (mix["naq"]["EPR2"]-nvPionsReg["naq"]["EPR2"] + mix["naq"]["centraleNuc"]) * factNuc +
                nbThermReg["naq"] * prodGaz / nbTherm)

    ##Bretagne
    popBRE = 0.05
    prodBRE = (np.array(fdc_off.bre)*mix["bre"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.bre)*mix["bre"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.bre)*mix["bre"]["panneauPV"]*powPV + 
                (mix["bre"]["EPR2"]-nvPionsReg["bre"]["EPR2"] + mix["bre"]["centraleNuc"]) * factNuc +
                nbThermReg["bre"] * prodGaz / nbTherm)

    ##Haut-de-France
    popHDF = 0.09
    prodHDF = (np.array(fdc_off.hdf)*mix["hdf"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.hdf)*mix["hdf"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.hdf)*mix["hdf"]["panneauPV"]*powPV + 
                (mix["hdf"]["EPR2"]-nvPionsReg["hdf"]["EPR2"] + mix["hdf"]["centraleNuc"]) * factNuc +
                nbThermReg["hdf"] * prodGaz / nbTherm)

    ##Pays de la Loire
    popPDL = 0.06
    prodPDL = (np.array(fdc_off.pll)*mix["pll"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.pll)*mix["pll"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.pll)*mix["pll"]["panneauPV"]*powPV + 
                (mix["pll"]["EPR2"]-nvPionsReg["pll"]["EPR2"] + mix["pll"]["centraleNuc"]) * factNuc +
                nbThermReg["pll"] * prodGaz / nbTherm)

    ##Auvergne-Rhône-Alpes
    popARA = 0.12
    prodARA = (np.array(fdc_on.ara)*mix["ara"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.ara)*mix["ara"]["panneauPV"]*powPV + 
                (mix["ara"]["EPR2"]-nvPionsReg["ara"]["EPR2"] + mix["ara"]["centraleNuc"]) * factNuc +
                nbThermReg["ara"] * prodGaz / nbTherm)

    ##Grand Est
    popGE = 0.08
    prodGE = (np.array(fdc_on.est)*mix["est"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.est)*mix["est"]["panneauPV"]*powPV + 
                (mix["est"]["EPR2"]-nvPionsReg["est"]["EPR2"] + mix["est"]["centraleNuc"]) * factNuc +
                nbThermReg["est"] * prodGaz / nbTherm)

    ##Normandie
    popNOR = 0.05
    prodNOR = (np.array(fdc_off.nor)*mix["nor"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.nor)*mix["nor"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.nor)*mix["nor"]["panneauPV"]*powPV + 
                (mix["nor"]["EPR2"]-nvPionsReg["nor"]["EPR2"] + mix["nor"]["centraleNuc"]) * factNuc +
                nbThermReg["nor"] * prodGaz / nbTherm)

    ##Bourgogne-Franche-Comte
    popBFC = 0.04
    prodBFC = (np.array(fdc_on.bfc)*mix["bfc"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.bfc)*mix["bfc"]["panneauPV"]*powPV + 
                (mix["bfc"]["EPR2"]-nvPionsReg["bfc"]["EPR2"] + mix["bfc"]["centraleNuc"]) * factNuc +
                nbThermReg["bfc"] * prodGaz / nbTherm)

    ##Centre Val de Loire
    popCVL = 0.04
    prodCVL = (np.array(fdc_on.cvl)*mix["cvl"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.cvl)*mix["cvl"]["panneauPV"]*powPV + 
                (mix["cvl"]["EPR2"]-nvPionsReg["cvl"]["EPR2"] + mix["cvl"]["centraleNuc"]) * factNuc +
                nbThermReg["cvl"] * prodGaz / nbTherm)

    ##PACA
    popPAC = 0.08
    prodPAC = (np.array(fdc_off.pac)*mix["pac"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.pac)*mix["pac"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.pac)*mix["pac"]["panneauPV"]*powPV + 
                (mix["pac"]["EPR2"]-nvPionsReg["pac"]["EPR2"] + mix["pac"]["centraleNuc"]) * factNuc +
                nbThermReg["pac"] * prodGaz / nbTherm)

    ##Ile-de-France
    popIDF = 0.19
    prodIDF = (np.array(fdc_on.idf)*mix["idf"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.idf)*mix["idf"]["panneauPV"]*powPV + 
                (mix["idf"]["EPR2"]-nvPionsReg["idf"]["EPR2"] + mix["idf"]["centraleNuc"]) * factNuc +
                nbThermReg["idf"] * prodGaz / nbTherm)

    ##Corse
    popCOR = 0.005
    prodCOR = (np.array(fdc_off.cor)*mix["cor"]["eolienneOFF"]*powOffshore + 
                np.array(fdc_on.cor)*mix["cor"]["eolienneON"]*powOnshore + 
                np.array(fdc_pv.cor)*mix["cor"]["panneauPV"]*powPV + 
                (mix["cor"]["EPR2"]-nvPionsReg["cor"]["EPR2"] + mix["cor"]["centraleNuc"]) * factNuc +
                nbThermReg["cor"] * prodGaz / nbTherm)

    ##production totale sur le territoire
    prod = prodOCC + prodNA + prodBRE + prodHDF + prodPDL + prodARA + prodGE + prodNOR + prodBFC + prodCVL + prodPAC + prodIDF + prodCOR

    ##calcul des ratios (prod de la region/pros totale --> heure par heure)
    ratioOCC = np.zeros(H)
    ratioNA = np.zeros(H)
    ratioBRE = np.zeros(H)
    ratioHDF = np.zeros(H)
    ratioPDL = np.zeros(H)
    ratioARA = np.zeros(H)
    ratioGE = np.zeros(H)
    ratioNOR = np.zeros(H)
    ratioBFC = np.zeros(H)
    ratioCVL = np.zeros(H)
    ratioPAC = np.zeros(H)
    ratioIDF = np.zeros(H)
    ratioCOR = np.zeros(H)

    for i in range(H):
        ratioOCC[i] = prodOCC[i]/prod[i] if prod[i] != 0 else 0 
        ratioNA[i] = prodNA[i]/prod[i] if prod[i] != 0 else 0 
        ratioBRE[i] = prodBRE[i]/prod[i] if prod[i] != 0 else 0 
        ratioHDF[i] = prodHDF[i]/prod[i] if prod[i] != 0 else 0 
        ratioPDL[i] = prodPDL[i]/prod[i] if prod[i] != 0 else 0 
        ratioARA[i] = prodARA[i]/prod[i] if prod[i] != 0 else 0 
        ratioGE[i] = prodGE[i]/prod[i] if prod[i] != 0 else 0 
        ratioNOR[i] = prodNOR[i]/prod[i] if prod[i] != 0 else 0 
        ratioBFC[i] = prodBFC[i]/prod[i] if prod[i] != 0 else 0 
        ratioCVL[i] = prodCVL[i]/prod[i] if prod[i] != 0 else 0 
        ratioPAC[i] = prodPAC[i]/prod[i] if prod[i] != 0 else 0 
        ratioIDF[i] = prodIDF[i]/prod[i] if prod[i] != 0 else 0 
        ratioCOR[i] = prodCOR[i]/prod[i] if prod[i] != 0 else 0 
    
    # print(ratioOCC)
    ##difference des rations prod et ratios pop regions par regions
    
    diffOCC = np.zeros(H)
    diffNA = np.zeros(H)
    diffBRE = np.zeros(H)
    diffHDF = np.zeros(H)
    diffPDL = np.zeros(H)
    diffARA = np.zeros(H)
    diffGE = np.zeros(H)
    diffNOR = np.zeros(H)
    diffBFC = np.zeros(H)
    diffCVL = np.zeros(H)
    diffPAC = np.zeros(H)
    diffIDF = np.zeros(H)
    diffCOR = np.zeros(H)

    diffOCC = ratioOCC - popOCC*np.ones(H)
    diffNA = ratioNA - popNA*np.ones(H)
    diffBRE = ratioBRE - popBRE*np.ones(H)
    diffHDF = ratioHDF - popHDF*np.ones(H)
    diffPDL = ratioPDL - popPDL*np.ones(H)
    diffARA = ratioARA - popARA*np.ones(H)
    diffGE= ratioGE - popGE*np.ones(H)
    diffNOR = ratioNOR - popNOR*np.ones(H)
    diffBFC = ratioBFC - popBFC*np.ones(H)
    diffCVL = ratioCVL - popCVL*np.ones(H)
    diffPAC = ratioPAC - popPAC*np.ones(H)
    diffIDF = ratioIDF - popIDF*np.ones(H)
    diffCOR = ratioCOR - popCOR*np.ones(H)

    ##moyenne sur les heures de l'annee des differences
    moyOCC = np.sum(diffOCC)/8760*100
    moyNA = np.sum(diffNA)/8760*100
    moyBRE = np.sum(diffBRE)/8760*100
    moyHDF = np.sum(diffHDF)/8760*100
    moyPDL = np.sum(diffPDL)/8760*100
    moyARA = np.sum(diffARA)/8760*100
    moyGE = np.sum(diffGE)/8760*100
    moyNOR = np.sum(diffNOR)/8760*100
    moyBFC = np.sum(diffBFC)/8760*100
    moyCVL = np.sum(diffCVL)/8760*100
    moyPAC = np.sum(diffPAC)/8760*100
    moyIDF = np.sum(diffIDF)/8760*100
    moyCOR = np.sum(diffCOR)/8760*100

    moyAbsOCC = np.sum(np.abs(diffOCC))/8760*100
    moyAbsNA = np.sum(np.abs(diffNA))/8760*100
    moyAbsBRE = np.sum(np.abs(diffBRE))/8760*100
    moyAbsHDF = np.sum(np.abs(diffHDF))/8760*100
    moyAbsPDL = np.sum(np.abs(diffPDL))/8760*100
    moyAbsARA = np.sum(np.abs(diffARA))/8760*100
    moyAbsGE = np.sum(np.abs(diffGE))/8760*100
    moyAbsNOR = np.sum(np.abs(diffNOR))/8760*100
    moyAbsBFC = np.sum(np.abs(diffBFC))/8760*100
    moyAbsCVL = np.sum(np.abs(diffCVL))/8760*100
    moyAbsPAC = np.sum(np.abs(diffPAC))/8760*100
    moyAbsIDF = np.sum(np.abs(diffIDF))/8760*100
    moyAbsCOR = np.sum(np.abs(diffCOR))/8760*100



    nbS = 0
    nbP = 0

    listeSurplusQuotidien = [0] * 365
    listeSurplusHoraire = [0] * 24

    listePenuriesQuotidien = [0] * 365
    listePenuriesHoraire = [0] * 24

    for i in range(len(s)):
        if s[i] > 0:
            nbS += 1
            listeSurplusQuotidien[i//24] += 1
            listeSurplusHoraire[i%24] += 1
        if p[i] > 0:
            nbP += 1
            listePenuriesQuotidien[i//24] += 1
            listePenuriesHoraire[i%24] += 1


    consoGaz = G.stored[0] - G.stored[8759]
    prodGazFossile = 0 if consoGaz < gazBiomasse else (consoGaz-gazBiomasse)*G.etaout
    save["prodGazFossile"][str(mix["annee"])] = prodGazFossile

    EmissionCO2 = prodOn*10 + prodOff*9 + prodPv*55 + prodEau*10 + prodNuc*6 + prodGazFossile*443 #variable EmissionCO2

    #Carte politique B
    if mix["politique"] == "CPB2" :
        save["varEmissions"] -= 2.1
        EmissionCO2 += save["varEmissions"]
    
    save["co2"].append(EmissionCO2)
    demande = np.sum(scenario) #variable demande
    

    prixGaz = 324.6e-6 #prix de l'electricite produite à partir du gaz/charbon --> moyenne des deux (35€ le MWh)
    prixNuc = 7.6e-6 #part du combustible dans le prix de l'electricite nucleaire (7.6€ le MWh)

    #carte alea MEGC (lance 1 / 3)
    if mix["alea"] == "MEGC1" or mix["alea"] == "MEGC2" or mix["alea"] == "MEGC3":
        prixGaz *= 1.5 #alea1
    
    
    if mix["alea"] == "MEGC3":
        prixNuc *= 1.4 #alea3


    #carte alea MEMP (lance 3)
    if mix["alea"] == "MEMP3":
        prixGaz *= 1.3
        prixNuc *= 1.2

    #variable cout (Md€) --> pour le tour titre

    nucProlong = 0
    onshoreRemplac = 0
    offshoreRemplac = 0

    for reg in save["capacite"]:
        listNuc = save[reg]["centraleNuc"]
        listOn = save[reg]["eolienneON"]
        listOff = save[reg]["eolienneOFF"]

        for n in listNuc :
            if n == mix["annee"] - 40 :
                nucProlong += 1

        for n in listOn :
            if n == mix["annee"] - 15 :
                onshoreRemplac += 1

        for n in listOff :
            if n == mix["annee"] - 15 :
                offshoreRemplac += 1

    cout = ((nvPions["eolienneON"] + onshoreRemplac) * 3.5 + 
            (nvPions["eolienneOFF"] + offshoreRemplac) * 6 + 
            nvPions["panneauPV"] * 3.6 + 
            nvPions["EPR2"]*8.6 + 
            nucProlong*2 +
            nvPions["biomasse"] * 0.12 +
            nvPions["methanation"] * 4.85 +
            (B.Q * 0.0012) / 0.003 + 
            (P.Q * 0.455) / 0.91 + 
            (prodNuc * prixNuc) +
            (prodGazFossile * prixGaz))

    if mix["annee"]!=2030 :
        cout +=  (10 - nucProlong) *0.5

    #budget à chaque tour sauf si carte evènement bouleverse les choses
    budget = 70

    #carte alea MEVUAPV : lance 3
    if mix["alea"] == "MEVUAPV3":
        budget -= 10

    #carte MEMDA : lance 1 / 2
    if mix["alea"] == "MEMDA1" or mix["alea"] == "MEMDA2" or mix["alea"] == "MEMDA3":
        budget += 3.11625

    if mix["alea"] == "MEMDA2" or mix["alea"] == "MEMDA3":
        cout -= 1.445
    
    #carte MEGDT : lance 1 / 3
    if mix["alea"] == "MEGDT1" or mix["alea"] == "MEGDT2" or mix["alea"] == "MEGDT3":
        cout += 1/3*nvPionsReg["pac"]["panneauPV"]*3.6

    if mix["alea"] == "MEGDT3":
        cout += nvPionsReg["pll"]["eolienneOFF"]*1.2

    
    Sol = (nbPions["eolienneON"]*300 + nbPions["eolienneOFF"]*400 + nbPions["panneauPV"]*26 + 
            nbPions["centraleNuc"]*1.5 + nbPions["biomasse"]*0.8) #occupation au sol de toutes les technologies (km2)


    Uranium = save["scores"]["Uranium"] #disponibilite Uranium initiale
    if nbPions["centraleNuc"] > 0 or nbPions["EPR2"] :
        Uranium -= 10 #à chaque tour où on maintient des technos nucleaires
    if nvPions["EPR2"] > 0:
        Uranium -= nvPions["EPR2"] 
    #carte alea MEGC (lance 2)
    if mix["alea"] == "MEGC2" or mix["alea"] == "MEGC3":
        Uranium -= 10 
    
    save["scores"]["Uranium"] = Uranium #actualisation du score Uranium


    Hydro = save["scores"]["Hydro"]#disponibilite Hydrocarbures et Charbon
    if prodGazFossile > 0:
        Hydro -= 20 #à chaque tour où on consomme du gaz fossile
    
    #carte alea MEMP (lance 2)
    if mix["alea"] == "MEMP2" or mix["alea"] == "MEMP3":
        Hydro -= 20

    save["scores"]["Hydro"] = Hydro #actualisation du score Hydro
    

    Bois = save["scores"]["Bois"]#disponibilite Bois
    recup = save["scores"]["totstockbois"] - Bois 

    if nbPions["biomasse"] > 0:
        Bois -= nbPions["biomasse"] 
    if nbPions["biomasse"] > 0 and recup >= 0 :
        Bois+= 1/2*recup #au nombre de centrales Biomasse on enlève 1 quantite de bois --> au tour suivant 1/2 des stocks sont recuperes
    #carte alea MEMP (lance 1)
    if mix["alea"] == "MEMP1" or mix["alea"] == "MEMP2" or mix["alea"] == "MEMP3":
        Bois -= 20
    
    #carte alea MEVUAPV  (lance de 1 / 2)
    if mix["alea"] == "MEVUAPV1" or mix["alea"] == "MEVUAPV2" or mix["alea"] == "MEVUPV3": 
        Bois -= 10
        save["scores"]["totstockbois"] -= 10

    save["scores"]["Bois"] = Bois #actualisation du score Bois
        

    dechet = save["scores"]["Dechet"]
    # dechet += nbTherm*2 + nbNuc*1 #dechets generes par les technologies Nucleaires et Thermiques
    dechet += nbPions["centraleNuc"] + nbPions["EPR2"]
    save["scores"]["Dechet"] = dechet

    capmax_info = save["capacite"]
    #carte alea MECS (lance 1 / 2)
    if mix["alea"] == "MECS1" or mix["alea"] == "MECS2" or mix["alea"] == "MECS3":
        for k in capmax_info:
            capmax_info[k]["eolienneON"] = int(capmax_info[k]["eolienneON"] * 0.4)

    if mix["alea"] == "MECS2" or mix["alea"] == "MECS3":
        capmax_info["occ"]["eolienneON"] *= 2
        capmax_info["occ"]["panneauPV"] *= 2

    #carte alea MEGDT (lance 2)
    if mix["alea"] == "MEGDT2" or mix["alea"] == "MEGDT3":
        capmax_info["naq"]["eolienneOFF"] += 1
        capmax_info["pac"]["eolienneOFF"] += 1
    
    save["capacite"] = capmax_info

    for k in capmax_info : 
        if (nbPions["eolienneON"] > capmax_info[k]["eolienneON"] 
            or nbPions["eolienneOFF"] > capmax_info[k]["eolienneOFF"] 
            or nbPions["panneauPV"] > capmax_info[k]["panneauPV"]-11*nbPions["eolienneON"]
            or nbPions["biomasse"] > capmax_info[k]["biomasse"]-33*nbPions["eolienneON"]-3*nbPions["panneauPV"]) :
            pass
            # AVERTISSEMENT


    replaceList = []
    nbReplace = 0
    for reg in save["capacite"]:
        for p in save[reg]:
            nbReplace = 0

            if p == "centraleNuc":
                for y in save[reg][p]:
                    if y == save["annee"] - 40:
                        nbReplace += 1

            elif p == "eolienneON" or p == "eolienneOFF":
                for y in save[reg][p]:
                    if y == save["annee"] - 15:
                        nbReplace += 1

            if nbReplace > 0:
                replaceList.append([nbReplace, p, reg])


    #modification du fichier save
    with open(dataPath+"game_data/{}/{}/save_tmp.json".format(group, team), "w") as output:
        json.dump(save, output)


    result = {"carte":mix["carte"], 
                "annee":mix["annee"], 
                "alea":mix["alea"], 
                "cout":round(cout), 
                "budget":round(budget),
                "sol":round((Sol/551695)*100, 4),
                "stockGaz":list(G.stored),
                "biogaz": round(gazBiomasse),
                "prodGazFossile": save["prodGazFossile"],
                "demande":int(demande), "production":prodTotale,
                "scoreUranium":Uranium, "scoreHydro":Hydro, "scoreBois":Bois, "scoreDechets":dechet,
                "prodOnshore":save["prodOnshore"], "puissanceEolienneON":round(nbPions["eolienneON"]*powOnshore, 2),
                "prodOffshore":save["prodOffshore"], "puissanceEolienneOFF":round(nbPions["eolienneOFF"]*powOffshore, 2),
                "prodPv":save["prodPv"], "puissancePV":round(nbPions["panneauPV"]*powPV, 2),
                "prodEau":save["prodEau"],
                "prodNucleaire":save["prodNucleaire"], "puissanceNucleaire":round(N.Q, 2),
                "prodGaz":save["prodGaz"], "puissanceGaz":round(G.Q, 2),
                "prodPhs":save["prodPhs"], "puissancePhs":round(P.Q, 2),
                "prodBatterie":save["prodBatterie"], "puissanceBatterie":round(B.Q, 2),
                "co2":save["co2"],
                "remplacement":replaceList,
                "nbSurplus":nbS, "nbPenuries":nbP,
                "surplusQuotidien":listeSurplusQuotidien, "surplusHoraire":listeSurplusHoraire,
                "penuriesQuotidien":listePenuriesQuotidien, "penuriesHoraire":listePenuriesHoraire,
                "transfert":{"occ":int(round(moyOCC)),
                                "naq":int(round(moyNA)),
                                "bre":int(round(moyBRE)),
                                "hdf":int(round(moyHDF)),
                                "pll":int(round(moyPDL)),
                                "ara":int(round(moyARA)),
                                "est":int(round(moyGE)),
                                "nor":int(round(moyNOR)),
                                "bfc":int(round(moyBFC)),
                                "cvl":int(round(moyCVL)),
                                "pac":int(round(moyPAC)),
                                "idf":int(round(moyIDF)),
                                "cor":int(round(moyCOR))
                }
    }


    return result



# Fonction principale
#
# @params
# mix (dict) : donnees du plateau
# save (dict) : donnees du tour precedent
# nbPions (dict) : nombre de pions total pour chaque techno
# nvPions (dict) : nombre de nouveaux pions total pour chaque techno ce tour-ci
# nvPionsReg (dict) : nombre de pions total pour chaque techno
# group (str) : groupe de TD de l'equipe qui joue
# team (int) : numero de l'equipe qui joue dans ce groupe      
def strat_stockage_main(mix, save, nbPions, nvPions, nvPionsReg, group, team):

    # Infos sur les unites de data :
    # eolienneON --> 1 unite = 10 parcs = 700 eoliennes
    # eolienneOFF --> 1 unite = 5 parcs = 400 eoliennes
    # panneauPV --> 1 unite = 10 parcs = 983 500 modules
    # centraleTherm --> 1 unite = 1 centrale
    # centraleNuc --> 1 unite = 1 reacteur
    # biomasse --> 1 unite = une fraction de flux E/S en methanation


    # Definition des scenarios (Negawatt, ADEME, RTE pour 2050)
    # Les autres scenarios sont faits mains à partir des donnees de Quirion

    ADEME = pd.read_csv(dataPath+"mix_data/ADEME_25-50.csv", header=None)
    ADEME.columns = ["heures", "d2050", "d2045", "d2040", "d2035", "d2030", "d2025"]

    # # RTE = pd.read_csv(dataPath+"mix_data/RTE_25-50.csv", header=None)
    # # RTE.columns = ["heures", "d2050", "d2045", "d2040", "d2035", "d2030", "d2025"]

    # # NEGAWATT = pd.read_csv(dataPath+"mix_data/NEGAWATT_25-50.csv", header=None)
    # # NEGAWATT.columns = ["heures", "d2050", "d2045", "d2040", "d2035", "d2030", "d2025"]


    result = simulation(ADEME.d2025, mix, save, nbPions, nvPions, nvPionsReg, group, team)


    with open(dataPath+'game_data/{}/{}/resultats.json'.format(group, team), 'r') as src:
        resultatGlobal = json.load(src)

    resultatGlobal[str(mix["annee"])] = result

    with open(dataPath+'game_data/{}/{}/resultats.json'.format(group, team), 'w') as dst:
        json.dump(resultatGlobal, dst)