import numpy as np
from collections import Counter
import sys
import json
import pandas as pd
#import boto3
import os
import datetime

                                #########################
                                ### TOUT EST EN GW(h) ###
                                #########################

np.seterr('raise') # A ENLEVER SUR LE CODE FINAL



# Telecharge certains fichiers de donnees necessaires au fonctionnement du programme
def initFiles():
    # Les lignes suivantes permettent d'avoir accès à un dépôt de données de manière chiffrée
    # s3_endpoint_url = 'https://object-rook-ceph.apps.math.cnrs.fr/'
    # s3_access_key_id = '26R58AYH5Z1X4IUNF1NQ' # le contenu de secrets/dossal
    # s3_secret_access_key = 'ODX7fukdCQTZ67n8fKLPwrup9OcQVU45RtnxfFHT' # le contenu de secrets/dossal
    # s3_bucket = 'dossal-enr2050'
    # s3 = boto3.client('s3','',endpoint_url = s3_endpoint_url,aws_access_key_id = s3_access_key_id,
    #                 aws_secret_access_key = s3_secret_access_key)

    # # File DL : (key, file to dl, location)
    # if not os.path.isfile('mix_data/run_of_river.csv'):
    #     # s3.download_file(s3_bucket, "demand2050_negawatt.csv", "data/demand2050_negawatt.csv")
    #     # s3.download_file(s3_bucket, "demand2050_RTE.csv", "data/demand2050_RTE.csv")
    #     # s3.download_file(s3_bucket, "demand2050_ADEME.csv", "data/demand2050_ADEME.csv")
    #     # s3.download_file(s3_bucket, "vre_profiles2006.csv", "data/vre_profiles2006.csv")
    #     s3.download_file(s3_bucket, "run_of_river.csv", "mix_data/run_of_river.csv")
    #     s3.download_file(s3_bucket, "lake_inflows.csv", "mix_data/lake_inflows.csv")
    pass


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
        self.stored = stored # ce qui est stocké
        self.prod = prod     # ce qui est produit
        self.etain = etain     # coefficient de rendement à la charge
        self.etaout = etaout   # coefficient de rendement à la décharge
        self.Q=Q             # capacité installée (flux sortant)
        self.S=S             # capacité de charge d'une techno de stockage (flux entrant)
        self.vol=Vol         # Capacité maximale de stockage de la techno (Volume max)


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

    # Sur ATH : pas de pénurie avec 56 centrales min.
    # Sur ATL : 28 centrales min. (50%)
    # Diviser en 4 ou 8 groupes (plutôt 8 pour les besoins humains)
    # 1/8 = 0.125, 7/8 = 0.875
    # 2180, 2920, 3650, 4400, 5130, 5900, 6732, 7580
    # Tiers de 8760 : 2920(4*730), 5840, 8460
    # DANS le dernier tiers : 50% croissance linéaire min, 25% baisse de 20% prod min/max, 25% arrêt

    # La production nucléaire est divisée en 8 groupes, chacun a son cycle d'arrêt. 
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


# Lance la production des centrales nucléaires
#
# @params
# tec : objet à utiliser pour la production  (ici, Techno Nucleaire)
# k (int) : heure courante
# aproduire (float) : qte d'energie a fournir
def nucProd(tec, k, aproduire):
    if aproduire <= 0:
        out = 0

    else:
        # Si la demande est trop faible ou nulle, on produit quand même à hauteur de 20%
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
    
    ##distribution écretage : min, max, moyenne et écart-type
    if y1[y1!=-1].size > 0:
        emoy = np.mean(y1[y1!=-1]) ##moyenne de l'échantillon //
        eetype = np.std(y1[y1!=-1]) ##ecart-type de l'échantillon //
        certitude_interval[1] = emoy - 2.33 * eetype / np.sqrt(len(y1[y1!=-1])) ##99% sur écretage (valeur sup de l'IC)
    else:
        # Si jamais de surplus
        certitude_interval[1] = stockmax - 10

    ##distribution pénurie : min, max, moyenne, écart-type
    if y2[y2!=-1].size > 0:
        pmoy = np.mean(y2[y2!=-1])
        petype = np.std(y2[y2!=-1])
        certitude_interval[0] = pmoy + 1.76 * petype / np.sqrt(len(y2[y2!=-1])) ##98% sur pénurie (valeur inf de l'IC)
    else:
        # Si jamais de pénurie
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
def StratStockage(prodres, H, Phs, Battery, Methanation, Lake, Thermal, Nuclear, endmonthlake):
    Surplus=np.zeros(H)
    ##Ajout paramètre Penurie
    Manque = np.zeros(H)
    #Definition d'un ordre sur les differentes technologies de stockage et destockage
    Tecstock= {"Phs":Phs , "Battery":Battery , "Methanation":Methanation}
    Tecstock2= {"Methanation":Methanation , "Phs":Phs , "Battery":Battery}
        
    Tecdestock= {"Battery":Battery , "Phs":Phs , "Methanation":Methanation , "Lake":Lake}
    
    for k in range(1,H):
        if prodres[k]>0:
            
            # La production min de nucléaire s'ajoute à la qté d'énergie à stocker
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
                
            # Si le nucléaire n'a pas suffi, on fait tourner les centrales thermiques
            if Aproduire > 0:
                Aproduire = thermProd(Thermal, k, Aproduire)
                
            ##liste penurie --> pour savoir si il y a pénurie dans la production d'électricité 
            Manque[k] = Aproduire
                
    return Surplus, Manque


# Strat de stockage optimisee
#
# @params
# prodres (array) : production residuelle sur l'annee
# H (int) : nombre d'heures dans l'annee
# Battery - Nuclear : objets de la classe Techno
# I0, I1, I2 (array) : seuils de stockage dirigeant la strat de stockage, et déduits de la strat naive
# endmonthlake (array) : contient la qte d'energie restante dans les lacs jusqu'a la fin de chaque mois
def StratStockagev2(prodres, H, Phs, Battery, Methanation, Lake, Thermal, Nuclear, I0, I1, I2, endmonthlake):
    Surplus=np.zeros(H)
    ##Ajout paramètre Penurie
    Manque = np.zeros(H)
    
    #Definition d'un ordre sur les differentes technologies de stockage et destockage
    Tecstock2= {"Methanation":Methanation , "Phs":Phs , "Battery":Battery} ##on stocke du gaz zone 1,2
    Tecstock3= {"Phs":Phs , "Battery":Battery , "Methanation":Methanation} ## zone 3
    Tecstock4 = {"Battery":Battery , "Phs":Phs , "Methanation":Methanation} ## zone 4
        
    Tecdestock1= {"Battery":Battery , "Phs":Phs , "Methanation":Methanation , "Lake":Lake} #zone 1
    Tecdestock2 = {"Phs":Phs , "Battery":Battery , "Methanation":Methanation , "Lake":Lake} ## zone 2
    Tecdestock3 = {"Methanation":Methanation , "Battery":Battery , "Phs":Phs , "Lake":Lake} ## zone 3,4
    
    for k in range(H):
        stock_PB = Phs.stored[k] + Battery.stored[k]
        
        # Suivant le niveau de stock, on change l'ordre de dé/stockage et on fait du power2gaz ou
        # gaz2power si besoin
        
        if 0 <= stock_PB < I0[k%24] :
            strat_stock = Tecstock4
            strat_destock = Tecdestock3
            qteInit = min(Methanation.Q, Phs.S+Battery.S)
            reste = unload(Methanation, k, qteInit, endmonthlake, prod=False)
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
            qteInit = min(Phs.Q+Battery.Q, Methanation.S)
            reste = unload(Battery, k, qteInit, endmonthlake, prod=False)
            reste = unload(Phs, k, reste, endmonthlake, prod=False)
            load(Methanation, k, qteInit-reste)
            
            
        
        if prodres[k]>0 :
            # La production min de nucléaire s'ajoute à la qté d'énergie à stocker
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

            # Si le nucléaire n'a pas suffi, on fait tourner les centrales thermiques
            if Aproduire > 0:
                Aproduire = thermProd(Thermal, k, Aproduire)
            
            ##liste penurie --> pour savoir si il y a pénurie dans la production d'électricité 
            Manque[k]=Aproduire
            
                
    return Surplus, Manque


#Quantification des émissions de CO2 et de la consommation d'électricité dues aux usages
#tour (int): tour de jeu : 1,2,3,4,5
#agr (char): réponse A,B,C,D ou "" à la question sur le type d'alimentation/agriculture
#mob (char): réponse A,B,C,D ou "" à la question sur le type de mobilités
#bat (char): réponse A,B,C,D ou "" à la question sur le type de bâtiment
#ind (char): réponse A,B,C,D ou "" à la question sur le type d'industrie/biens de consommation
#voit (char): réponse A,B,C ou "" à la question catégorie voiture
#pl (char): réponse A ou "" à la question catégorie poids lourds
#avi (char): réponse A,B,C,D ou "" à la question catégorie avion

#vos (int): nombre de kilomètres effectués par une personne dans une année en voiture essence
#voe (int): nombre de kilomètres effectués par une personne dans une année en voiture électrique
#tra (int): nombre de kilomètres effectués par une personne dans une année en train
#vel (int): nombre de kilomètres effectués par une personne dans une année en vélo électrique
#met (int): nombre de kilomètres effectués par une personne dans une année en métro
#bus (int): nombre de kilomètres effectués par une personne dans une année en bus
#bue (int): nombre de kilomètres effectués par une personne dans une année en bus électrique
#voli (int): nombre de vols intérieurs effectués par une personne dans une année
#vole (int): nombre de vols en europe effectués par une personne dans une année
#volin (int): nombre de vols internationnaux effectués par une personne dans une année
#pm (int): nombre de petits meubles neufs achetés par an par une personne
#gm (int): nombre de gros meubles neufs achetés par an par une personne
#pee (int) : nombre de petits équipements électroménagers neufs achetés par an par une personne
#gee (int): nombre de gros équipements électroménagers neufs achetés par an par une personne
#smart (int): nombre de smartphones neufs achetés par an par une personne
#eei (int): nombre d'équipements électroniques intermédiaires neufs achetés par an par une personne
#geel (int) : nombre de gros équipements électroniques neufs achetés par an par une personne

def Usages(tour, agr, mob, bat, ind, voit, pl, avi, vos, voe, tra, vel, met, bus, bue, voli, vole, volin, pm, gm, pee, gee, smart, eei, geel):

    demande = 0 #(en TWh)
    emission = 0 #(en tonnes de CO2)

    #réponse 1 : agr 
    if agr == "A":
        demande += 10
        emission +=0.72
    if agr == "B":
        demande += 29
        emission += 0.89
    if agr == "C":
        demande += 62
        emission += 1.24
    if agr == "D":
        demande += 72
        emission += 1.4
    
    #réponse 2 : mob 
    if mob == "A":
        demande += 150
    if mob == "B":
        demande += 150
    if mob == "C":
        demande += 200
    if mob == "D":
        demande += 225
    
     #réponse 3 : bat 
    if bat == "A":
        demande += 220
    if bat == "B":
        demande += 250
    if bat == "C":
        demande += 300
    if bat == "D":
        demande += 375
    
     #réponse 3 : ind 
    if ind == "A":
        demande += 250
    if ind == "B":
        demande += 250
    if ind == "C":
        demande += 300
    if ind == "D":
        demande += 400

    #réponse voit
    if voit == "A":
        demande += 66
    if ind == "B":
        demande += 90
   
   #réponse pl
    if voit == "A":
        demande += 4.92
 
    #réponse avi
    if avi == "D":
        demande += 2.450

    emission += vos*2e-4 + voe*1e-4 + vel*1e-5 + bus*1e-4 + voli*0.26 + vole*0.47 + volin*1.82 + pm*0.1 + gm*0.3 + pee*0.04 + gee*0.25 + smart*0.03 + eei*0.1 + geel*0.4
    demande += vel*5.3136e-6*(660000)*(tour) + met*1.5e-3 + bue*1.3e-9

    return demande, emission



# Optimisation de stratégie de stockage et de déstockage du Mix énergetique
#
# @params
# scenario (array) : scenario de consommation heure par heure
# titre (int) : annee de deroulement du scenario (25, 30, 35, 40, 45, 50)
# est - cor (dict) : contient le nombre d'installations pour la region concernee
# nbOn - nbBio (int) : nombre de pions eoliennes onshore, offshore, ..., de biomasse
# factStock (float) : facteur de qte de stockage, entre 0 et 1
# cout (int) : cout cumulé des tours précédent
# alea (str) : code d'une carte alea
def mix(scenario, titre, hdf, idf, est, nor, occ, pac, bre, cvl, pll, naq, ara, bfc, cor, 
        nbOn, nbOff, nbPv, nbNuc, nbTherm, nbBio, factStock, alea, jeu):

    H = 8760

    #actualisation : pour chaque technologie --> nombre posé à ce tour (titre)
    jeu[0]["nbeolON"] = nbOn - jeu[0]["nbeolON"]
    jeu[0]["nbeolOFF"] = nbOff - jeu[0]["nbeolOFF"]
    jeu[0]["nbPV"] = nbPv - jeu[0]["nbPV"]
    
    jeu[0]["nbNuc"] = nbNuc - jeu[0]["nbNuc"] - 47
    jeu[0]["nbTherm"] = nbTherm - jeu[0]["nbTherm"] - 22
    jeu[0]["nbBio"] = nbBio - jeu[0]["nbBio"]

    #carte alea MECS (lancé 3)
    if alea == "MECS3":
        jeu[0]["nbNuc"] = 0

    #carte aléa MEVUAPV  (lancé dé 1 / 2)
    if alea == "MEVUAPV1" or alea == "MEVUAPV2" or alea == "MEVUPV3": 
        jeu[1] = 9e4
        scenario += np.ones(H) * (9e4/H)
    
    if alea == "MEVUAPV2" or alea == "MEVUAPV3":
        jeu[2] = 0.15

    #carte aléa MEMDA (lancé 3)
    if alea == "MEMDA3":
        scenario = 0.95 * scenario

    fdc_on = pd.read_csv("mix_data/fdc_on.csv")
    fdc_off = pd.read_csv("mix_data/fdc_off.csv")
    fdc_pv = pd.read_csv("mix_data/fdc_pv.csv")
    
    prodOnshore = np.zeros(H)
    prodOffshore = np.zeros(H)
    prodPV = np.zeros(H)

    # Puissance d'un pion
    powOnshore = 1.4
    powOffshore = 2.4
    powPV = 3

    # On fait la somme des prods par region pour chaque techno (FacteurDeCharge * NbPions * PuissanceParPion)
    prodOffshore += np.array(fdc_off.occ) * occ["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.occ) * occ["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.occ) * occ["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.naq) * naq["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.naq) * naq["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.naq) * naq["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.bre) * bre["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.bre) * bre["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.bre) * bre["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.hdf) * hdf["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.hdf) * hdf["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.hdf) * hdf["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.pll) * pll["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.pll) * pll["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.pll) * pll["panneauPV"] * powPV

    prodOnshore += np.array(fdc_on.ara) * ara["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.ara) * ara["panneauPV"] * powPV

    prodOnshore += np.array(fdc_on.est) * est["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.est) * est["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.nor) * nor["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.nor) * nor["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.nor) * nor["panneauPV"] * powPV

    prodOnshore += np.array(fdc_on.bfc) * bfc["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.bfc) * bfc["panneauPV"] * powPV

    #carte aléa MEMFDC (lancé 1)
    if alea == "MEMFDC1" or alea == "MEMFDC2" or alea == "MEMFDC3":
        prodOnshore += (np.array(fdc_on.cvl) * cvl["eolienneON"] * powOnshore) * 54/60
    else:
        prodOnshore += np.array(fdc_on.cvl) * cvl["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.cvl) * cvl["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.pac) * pac["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.pac) * pac["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.pac) * pac["panneauPV"] * powPV

    prodOffshore += np.array(fdc_off.cor) * cor["eolienneOFF"] * powOffshore
    prodOnshore += np.array(fdc_on.cor) * cor["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.cor) * cor["panneauPV"] * powPV

    prodOnshore += np.array(fdc_on.idf) * idf["eolienneON"] * powOnshore
    prodPV += np.array(fdc_pv.idf) * idf["panneauPV"] * powPV




    # Definition des productions électriques des rivières et lacs 
    coefriv = 13
    river = pd.read_csv("mix_data/run_of_river.csv", header=None)
    river.columns = ["heures", "prod2"]
    rivprod = np.array(river.prod2) * coefriv

    lake = pd.read_csv("mix_data/lake_inflows.csv", header=None)
    lake.columns = ["month", "prod2"]
    lakeprod = np.array(lake.prod2)

    # Calcul de ce qui est stocké dans les lacs pour chaque mois
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

    # Definition des differentes technologies
    P=Techno('Phs', np.ones(H)*16, np.zeros(H), 0.95, 0.9, factStock*9.3, factStock*9.3, factStock*180)
    B=Techno('Battery', np.ones(H)*2, np.zeros(H), 0.9, 0.95, factStock*20.08, factStock*20.08, factStock*74.14)
    M=Techno('Methanation', np.ones(H)*62500, np.zeros(H), 0.59, 0.45, 32.93*(nbBio/219), 7.66*(nbBio/219), 125000)    
    L=Techno('Lake', storedlake, np.zeros(H), 1, 1, 10, 10, 2000)

    # Puissance centrales territoire : 18.54 GWe répartis sur 24 centrales (EDF)
    # Rendement méca (inutile ici) : ~35% généralement (Wiki)
    T = Techno('Centrale thermique', None, np.zeros(H), None, 1, 0.7725*nbTherm, None, None)
    
    # Puissance : 1.08 GWe (EDF)
    # Même rendement
    #réacteurs nucléaires effectifs qu'après 1 tour
    nbprodNuc = (nbNuc-jeu[0]["nbNuc"])
    N = Techno('Réacteur nucléaire', None, np.zeros(H), None, 1, 1.08*nbprodNuc, None, None)

        
    # résultats de la strat initiale
    # Renvoie Surplus,Pénurie et met à jour Phs,Battery,Methanation,Lake,Therm,Nuc
    s,p=StratStockage(prodresiduelle,H,P,B,M,L,T,N, endmonthlake)
    
    
    #############################
    ## NUAGES DE POINTS POUR OPTIMISER LE STOCKAGE
    
    stockage_PB = np.zeros(365) ##liste qui va servir à enregister les stockages Phs + Battery à l'heure H pour tous les jours
    
    stockmax = B.vol + P.vol ##stockage maximum total = max total stockage Phs + max total stockage Battery    
    
    ##listes pour écrêtage : x1 enregistre les jours où le lendemain il y a écrêtage
    ##y1 enregistre la valeur du stock Phs + Battery où le lendemain il y a écrêtage
    x1 = np.ones(365)*(-1)
    y1 = np.ones(365)*(-1)
    
    ##pareil que précèdemment mais pour lendemains avec pénurie
    x2 = np.ones(365)*(-1)
    y2 = np.ones(365)*(-1)
    
    ##pareil que précèdemment mais pour lendemains avec demande satisfaite et sans perte
    x3 = np.ones(365)*(-1)
    y3 = np.ones(365)*(-1)
    
    ##on enlevera les -1 des listes x1, x2, x3, y1, y2, y3 pour ne récupérer que les points essentiels
        
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
        for jour in range(365): ##on regarde tous les jours de l'année
        
            stockage_PB[jour]=StockPB[jour*24 + h1] #Au jour jour, valeur du stock Phs + Battery
        
            ##on regarde dans les 24h qui suivent si il y a écrêtage, pénurie ou aucun des deux
            for h2 in range(24): 
                t = (jour*24 + h1 + h2) % H
                
                if s[t] > 0 and StockPB[t] >= stockmax : ##cas écrêtage
                    x1[jour] = jour + 1 ##on note le jour précèdant jour avec écrêtage
                    y1[jour] = stockage_PB[jour] ##on note le stock du jour précèdant jour avec écrêtage
            
                elif p[t] > 0 : ##cas pénurie
                    x2[jour] = jour + 1 ##mêmes explications mais pour pénurie
                    y2[jour] = stockage_PB[jour]
                
                else : ##cas ni écrêtage, ni pénurie
                    x3[jour] = jour + 1 ##mêmes explications mais avec ni écrêtage, ni pénurie
                    y3[jour] = stockage_PB[jour]
                
                if x1[jour] == x2[jour]: ##si écretage et pénurie le même jour, on considère que c'est une pénurie 
                    x1[jour] = -1
                    y1[jour] = -1
            
            
        int_glob = certitudeglobal(y1, y2, y3, stockmax)
        certitude_interval_inf[h1] = int_glob[0]
        certitude_interval_sup[h1] = int_glob[1]
        certitude_interval_med[h1] = int_glob[2]
        
        seuils_top[h1] = seuil(y1, y2, y3, 0.02, "u")
        seuils_bot[h1] = seuil(y1, y2, y3, 0.9, "d")
        seuils_mid[h1] = (seuils_top[h1] + seuils_bot[h1]) / 2
        
    
        
        
    # Renvoie Surplus,Pénurie, et met à jour les technos
    
    #Décommenter pour méthode 1 (intervalles de confiance)
    s,p=StratStockagev2(prodresiduelle, H, P, B, M, L, T, N,
                        certitude_interval_inf, certitude_interval_med, certitude_interval_sup, endmonthlake)
    
    #Décommenter pour méthode 2 (recherche itérative du meilleur seuil)
    #s,p=StratStockagev2(prodresiduelle, H, P, B, M, L, T, N,
    #                    seuils_bot, seuils_mid, seuils_top, endmonthlake)
    
    
    ####Demande des choix de la fiche Usage à l'utilisateur
    # choix_utilisateur = input("Entrez les valeurs séparées par des espaces : ")

    # # Diviser la chaîne en valeurs individuelles
    # liste = choix_utilisateur.split(',')

    # valeurs = [float(valeur) for valeur in liste]

    # # Appeler la fonction avec les valeurs fournies par l'utilisateur
    # d, e = Usages(valeurs)

    

    # Infos qu'on peut retourner (plusieurs axes temporels et 2 stratégies sont possibles):
    # - Stock PHS / Batteries 
    # - Combien de surpus / pénurie ***
    # - Evolution des seuils
    # - (Mix des 2 premiers points)
    # - Stocks de gaz ***
    # - Courbes de production X demande ***
    # - Prod résiduelle
    # - CO2 ***
        
    

    print("\t\t####################################")
    print("\t\t\t     {}           ".format(titre))
    print("\t\t\t   BILAN PAR TECHNO   ")
    print("\t\t####################################\n")

    prodOn = int(np.sum(prodOnshore))
    prodOff = int(np.sum(prodOffshore))
    prodPv = int(np.sum(prodPV+jeu[2]*prodPV))
    prodEau = int(np.sum(L.prod + rivprod))
    prodNuc = int(np.sum(N.prod))
    prodTherm = int(np.sum(T.prod))
    prodMeth = int(np.sum(M.prod))
    prodPhs = int(np.sum(P.prod))
    prodBat = int(np.sum(B.prod))

    #carte aléa MEMFDC (lancé 2 / 3)
    if alea == "MEMFDC2" or alea == "MEMFDC3":
        prodMeth -= (prodMeth * naq["biomasse"]/nbBio)/5
    
    if alea == "MEMFDC3" :
        prodNuc = prodNuc*45/60


    prodTotale = prodOn + prodOff + prodPv + prodEau + prodNuc + prodTherm + prodMeth + prodPhs + prodBat


    print("---------------------------------------------------------------------------------------------------------")
    print("| Techno\t\t| Puissance installée (GW)\t| Production (GWh)\t| Emissions CO2 (t) \t|")
    print("---------------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------------")
    print("| Eolien onshore\t| {}\t\t\t\t| {}\t\t\t| {}\t\t|".format(np.round(nbOn*powOnshore, 2), prodOn, prodOn * 10))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Eolien offshore\t| {}\t\t\t\t| {}\t\t\t| {}\t\t|".format(np.round(nbOff*powOffshore, 2), prodOff, prodOff * 9))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Solaire\t\t| {}\t\t\t\t| {}\t\t\t| {}\t\t|".format(np.round(nbPv*powPV, 2), prodPv, prodPv * 55))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Hydraulique\t\t| -\t\t\t\t| {}\t\t\t| {}\t\t|".format(prodEau, prodEau * 10))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Nucléaire\t\t| {}\t\t\t\t| {}\t\t| {}\t\t|".format(np.round(N.Q, 2), prodNuc, prodNuc * 6))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Thermique\t\t| {}\t\t\t\t| {}\t\t\t| {}\t\t\t|".format(np.round(T.Q, 2), prodTherm, prodTherm * 443))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Methanation\t\t| {}\t\t\t\t| {}\t\t\t| {}\t\t|".format(np.round(M.Q, 2), prodMeth, prodMeth * 32))
    print("---------------------------------------------------------------------------------------------------------")
    print("| PHS\t\t\t| {}\t\t\t\t| {}\t\t\t| -\t\t\t|".format(np.round(P.Q, 2), prodPhs))
    print("---------------------------------------------------------------------------------------------------------")
    print("| Batteries\t\t| {}\t\t\t\t| {}\t\t\t| -\t\t\t|".format(np.round(B.Q, 2), prodBat))
    print("---------------------------------------------------------------------------------------------------------\n\n")

    

    print("\t\t####################################")
    print("\t\t\t     {}           ".format(titre))
    print("\t\t\t   BILAN GLOBAL   ")
    print("\t\t####################################\n")

    nbS = 0
    nbP = 0

    for i in range(len(s)):
        if s[i] > 0:
            nbS += 1
        if p[i] > 0:
            nbP += 1


    
    EmissionCO2 = prodOn*10 + prodOff*9 + prodPv*55 + prodEau*10 + prodNuc*6 + prodTherm*443 + prodMeth*32 #variable EmissionCO2
    demande = np.sum(scenario) #variable demande

    

    print("Demande : {} GWh".format(int(demande)))
    print("Production : {} GWh".format(prodTotale))
    print("Résultat : {} GWh\n".format(prodTotale - int(np.sum(scenario))))

    print("Emissions CO2 : {} tonnes".format(EmissionCO2))
    print("Part des émissions CO2 dûes au mix énergétique: {0: .4f} %\n".format(((EmissionCO2/310e9)*100)))
    # a comparer avec 310 Md de tonnes au total pour la France

    print("{} surplus".format(nbS))    
    print("{} pénuries".format(nbP))

    dGaz = M.stored[8759]-M.stored[0]
    print("Gaz : {} -> {} ({}) GWh\n".format(int(M.stored[0]), int(M.stored[8759]), int(dGaz)))

    print("Capacités totales (GWh):")
    print("   Batteries:", int(B.vol))
    print("   PHS:", int(P.vol))
    print("   Gaz:", int(M.vol))
    print("\n")

    prixgazchar = 324.6e-6 #prix de l'électricité produite à partir du gaz/charbon --> moyenne des deux (35€ le MWh)
    prixNuc = 7.6e-6 #part du combustible dans le prix de l'électricité nucléaire (7.6€ le MWh)

    #carte alea MEGC (lancé 1 / 3)
    if alea == "MEGC1" or alea == "MEGC2" or alea == "MEGC3":
        prixgazchar *= 1.5 #alea1
    
    
    if alea == "MEGC3":
        prixNuc *= 1.4 #alea3


    #carte alea MEMP (lancé 3)
    if alea == "MEMP3":
        prixgazchar *= 1.3
        prixNuc *= 1.2

    #variable cout (Md€) --> pour le tour titre
    cout = (jeu[0]["nbeolON"] * 3.5 + 
            jeu[0]["nbeolOFF"] * 1.2 + 
            jeu[0]["nbPV"] * 3.6 + 
            jeu[0]["nbNuc"] * 8.6 +
            jeu[0]["nbBio"] * 0.12 +
            (B.Q * 0.0012) / 0.003 + 
            (P.Q * 0.455) / 0.91 + 
            (prodNuc * prixNuc) +
            (prodTherm * prixgazchar))


    #budget à chaque tour sauf si carte évènement bouleverse les choses
    budget = 80

    #carte alea MEVUAPV : lancé 3
    if alea == "MEVUAPV3":
        budget -= 10

    #carte MEMDA : lancé 1 / 2
    if alea == "MEMDA1" or alea == "MEMDA2" or alea == "MEMDA3":
        budget += 3.11625

    if alea == "MEMDA2" or alea == "MEMDA3":
        cout -= 1.445
    
    #carte MEGDT : lancé 1 / 3
    if alea == "MEGDT1" or alea == "MEGDT2" or alea == "MEGDT3":
        cout += 1/3*jeu[4]["pac"]["panneauPV"]*3.6

    if alea == "MEGDT3":
        cout += jeu[4]["pll"]["eolienneOFF"]*1.2

    

    print("Budget dépensé l'année {} : {} Md €".format(titre ,cout)) #affiche le montant dépensé au tour titre
    print("Etat des comptes {} :".format(budget - cout)) #affiche si il y a un déficit vis à vis du budget attribué en début de tour 
    print("\n")

    Sol = nbOn*300 + nbOff*400 + nbPv*26 + nbNuc*1.5 + nbBio*0.8 #occupation au sol de toutes les technologies (km2)

    #affiche la part du territoire fançais occupé par les technologies 
    print("Empreinte au sol vis à vis de la France : {} %".format((Sol/551695)*100)) 
    print("\n")


    Uranium = jeu[3]["Uranium"] #disponibilité Uranium initiale
    if nbNuc > 0:
        Uranium -= 10 #à chaque tour où on maintient des technos nucléaires
    if jeu[0]["nbNuc"] > 0:
        Uranium -= 5*jeu[0]["nbNuc"]/2 #à chaque paire de réacteurs posées sur le territoire
    #carte aléa MEGC (lancé 2)
    if alea == "MEGC2" or alea == "MEGC3":
        Uranium -= 10 
    
    jeu[3]["Uranium"] = Uranium #actualisation du score Uranium

    print("Score Uranium : {}".format(Uranium)) #affichage du score Uranium

    Hydro = jeu[3]["Hydro"]#disponibilité Hydrocarbures et Charbon
    if nbTherm>0:
        Hydro -= 20 #à chaque tour où on maintient des technos Hydros/Charbon
    
    #carte aléa MEMP (lancé 2)
    if alea == "MEMP2" or alea == "MEMP3":
        Hydro -= 20

    jeu[3]["Hydro"] = Hydro #actualisation du score Hydro
    
    print("Score HydroCarbures/Charbon : {}".format(Hydro)) #affichage du score Hydrocarbures/Charbon

    Bois = jeu[3]["Bois"]#disponibilité Bois
    if nbBio > 0:
        Bois -= nbBio + 1/2*Bois #au nombre de centrales Biomasse on enlève 1 quantité de bois --> au tour suivant 1/2 des stocks sont récupérés
    #carte aléa MEMP (lancé 1)
    if alea == "MEMP1" or alea == "MEMP2" or alea == "MEMP3":
        Bois -= 20

    jeu[3]["Bois"] = Bois #actualisation du score Bois
        
    print("Score Bois : {}".format(Bois)) #affichage du score Bois

    dechet = jeu[3]["Dechet"]
    dechet += nbTherm*2 + nbNuc*1 #déchets générés par les technologies Nucléaires et Thermiques
    print("Score déchets : {}".format(dechet)) #affichage du score déchet
    print("\n")
    jeu[3]["Dechet"] = dechet

    capmax_info = jeu[5]
    #carte alea MECS (lancé 1 / 2)
    if alea == "MECS1" or alea == "MECS2" or alea == "MECS3":
        for k in capmax_info:
            capmax_info[k]["eolienneON"] = 0.4*capmax_info[k]["eolienneON"]

    if alea == "MECS2" or alea == "MECS3":
        capmax_info["occ"]["eolienneON"]= 2*capmax_info["occ"]["eolienneON"]
        capmax_info["occ"]["panneauPV"]= 2*capmax_info["occ"]["panneauPV"]

    #carte alea MEGDT (lancé 2)
    if alea == "MEGDT2" or alea == "MEGDT3":
        capmax_info["naq"]["eolienneOFF"]+=1
        capmax_info["pac"]["eolienneOFF"]+=1
    
    jeu[5]=capmax_info

    for k in capmax_info : 
        if nbOn > capmax_info[k]["eolienneON"] or nbOff > capmax_info[k]["eolienneOFF"] or nbPv > capmax_info[k]["panneauPV"]-11*nbOn or nbBio > capmax_info[k]["biomasse"]-33*nbOn-3*nbPv :
            print("vous empiétez sur des territoires agricoles ou des surfaces maritimes --> mécontentement de la population : ATTENTION !!!")

    print("")

    #actualisation des nouvelles technologies renouvelables posées dans chaque région

    jeu[4]["hdf"]["eolienneON"] = hdf["eolienneON"] - jeu[4]["hdf"]["eolienneON"]
    jeu[4]["hdf"]["eolienneOFF"] = hdf["eolienneOFF"] - jeu[4]["hdf"]["eolienneOFF"]
    jeu[4]["hdf"]["panneauPV"] = hdf["panneauPV"] - jeu[4]["hdf"]["panneauPV"]

    jeu[4]["idf"]["eolienneON"] = idf["eolienneON"] - jeu[4]["idf"]["eolienneON"]
    jeu[4]["idf"]["eolienneOFF"] = idf["eolienneOFF"] - jeu[4]["idf"]["eolienneOFF"]
    jeu[4]["idf"]["panneauPV"] = idf["panneauPV"] - jeu[4]["idf"]["panneauPV"]

    jeu[4]["est"]["eolienneON"] = est["eolienneON"] - jeu[4]["est"]["eolienneON"]
    jeu[4]["est"]["eolienneOFF"] = est["eolienneOFF"] - jeu[4]["est"]["eolienneOFF"]
    jeu[4]["est"]["panneauPV"] = est["panneauPV"] - jeu[4]["est"]["panneauPV"]

    jeu[4]["nor"]["eolienneON"] = nor["eolienneON"] - jeu[4]["nor"]["eolienneON"]
    jeu[4]["nor"]["eolienneOFF"] = nor["eolienneOFF"] - jeu[4]["nor"]["eolienneOFF"]
    jeu[4]["nor"]["panneauPV"] = nor["panneauPV"] - jeu[4]["nor"]["panneauPV"]

    jeu[4]["occ"]["eolienneON"] = occ["eolienneON"] - jeu[4]["occ"]["eolienneON"]
    jeu[4]["occ"]["eolienneOFF"] = occ["eolienneOFF"] - jeu[4]["occ"]["eolienneOFF"]
    jeu[4]["occ"]["panneauPV"] = occ["panneauPV"] - jeu[4]["occ"]["panneauPV"]

    jeu[4]["pac"]["eolienneON"] = pac["eolienneON"] - jeu[4]["pac"]["eolienneON"]
    jeu[4]["pac"]["eolienneOFF"] = pac["eolienneOFF"] - jeu[4]["pac"]["eolienneOFF"]
    jeu[4]["pac"]["panneauPV"] = pac["panneauPV"] - jeu[4]["pac"]["panneauPV"]

    jeu[4]["bre"]["eolienneON"] = bre["eolienneON"] - jeu[4]["bre"]["eolienneON"]
    jeu[4]["bre"]["eolienneOFF"] = bre["eolienneOFF"] - jeu[4]["bre"]["eolienneOFF"]
    jeu[4]["bre"]["panneauPV"] = bre["panneauPV"] - jeu[4]["bre"]["panneauPV"]

    jeu[4]["cvl"]["eolienneON"] = cvl["eolienneON"] - jeu[4]["cvl"]["eolienneON"]
    jeu[4]["cvl"]["eolienneOFF"] = cvl["eolienneOFF"] - jeu[4]["cvl"]["eolienneOFF"]
    jeu[4]["cvl"]["panneauPV"] = cvl["panneauPV"] - jeu[4]["cvl"]["panneauPV"]

    jeu[4]["pll"]["eolienneON"] = pll["eolienneON"] - jeu[4]["pll"]["eolienneON"]
    jeu[4]["pll"]["eolienneOFF"] = pll["eolienneOFF"] - jeu[4]["pll"]["eolienneOFF"]
    jeu[4]["pll"]["panneauPV"] = pll["panneauPV"] - jeu[4]["pll"]["panneauPV"]

    jeu[4]["naq"]["eolienneON"] = naq["eolienneON"] - jeu[4]["naq"]["eolienneON"]
    jeu[4]["naq"]["eolienneOFF"] = naq["eolienneOFF"] - jeu[4]["naq"]["eolienneOFF"]
    jeu[4]["naq"]["panneauPV"] = naq["panneauPV"] - jeu[4]["naq"]["panneauPV"]

    jeu[4]["ara"]["eolienneON"] = ara["eolienneON"] - jeu[4]["ara"]["eolienneON"]
    jeu[4]["ara"]["eolienneOFF"] = ara["eolienneOFF"] - jeu[4]["ara"]["eolienneOFF"]
    jeu[4]["ara"]["panneauPV"] = ara["panneauPV"] - jeu[4]["ara"]["panneauPV"]

    jeu[4]["bfc"]["eolienneON"] = bfc["eolienneON"] - jeu[4]["bfc"]["eolienneON"]
    jeu[4]["bfc"]["eolienneOFF"] = bfc["eolienneOFF"] - jeu[4]["bfc"]["eolienneOFF"]
    jeu[4]["bfc"]["panneauPV"] = bfc["panneauPV"] - jeu[4]["bfc"]["panneauPV"]

    jeu[4]["cor"]["eolienneON"] = cor["eolienneON"] - jeu[4]["cor"]["eolienneON"]
    jeu[4]["cor"]["eolienneOFF"] = cor["eolienneOFF"] - jeu[4]["cor"]["eolienneOFF"]
    jeu[4]["cor"]["panneauPV"] = cor["panneauPV"] - jeu[4]["cor"]["panneauPV"]

    #modification du fichier savedata
    with open("game_data/savedata.json", "w") as output:
        json.dump(jeu, output)


    result = {"eolienON":{"capa":round(nbOn*powOnshore, 2), "prod":prodOn, "CO2":prodOn*10},
                "eolienOFF":{"capa":round(nbOff*powOffshore, 2), "prod":prodOff, "CO2":prodOff*9},
                "solaire":{"capa":round(nbPv*powPV, 2), "prod":prodPv, "CO2":prodPv*55},
                "hydraulique":{"capa":"", "prod":prodEau, "CO2":prodEau*10},
                "nucleaire":{"capa":round(N.Q, 2), "prod":prodNuc, "CO2":prodNuc*6},
                "thermique":{"capa":round(T.Q, 2), "prod":prodTherm, "CO2":prodTherm*443},
                "methanation":{"capa":round(M.Q, 2), "prod":prodMeth, "CO2":prodMeth*32},
                "phs":{"capa":round(P.Q, 2), "prod":prodPhs, "CO2":""},
                "batterie":{"capa":round(B.Q, 2), "prod":prodBat, "CO2":""},

                "demande":int(demande), "production":prodTotale, "resultat":prodTotale-int(demande),
                "emissions":EmissionCO2, "partEmissions":round(EmissionCO2/310e9*100, 2),

                "surplus":nbS, "penuries":nbP,

                "cout":round(cout), "sol":round(Sol/551695*100, 2),

                "scores":{"uranium":Uranium, "hydro":Hydro, "bois":Bois, "dechets":dechet}
                }

    return result



# Fonction principale
#
# @params
# scenario (str) : au choix entre ADEME, RTE et Negawatt
# tour (int) : valeur parmi 25, 30, .., 45, 50
# est - cor (dict) : contient le nombre d'installations pour la region concernee
# nbOn - nbBio (int) : nombre de pions eoliennes onshore, offshore, ..., de biomasse
# factStock (float) : facteur de qte de stockage, entre 0 et 1
# alea (str) : code d'une carte alea        
def strat_stockage_main(data):
    nbNuc = 0
    nbTherm = 0
    nbBio = 0
    nbOn = 0
    nbOff = 0
    nbPv = 0

    # Infos sur les unités de data :
    # eolienneON --> 1 unité = 10 parcs = 700 eoliennes
    # eolienneOFF --> 1 unité = 5 parcs = 400 eoliennes
    # panneauPV --> 1 unité = 10 parcs = 983 500 modules
    # centraleTherm --> 1 unité = 1 centrale
    # centraleNuc --> 1 unité = 1 réacteur
    # biomasse --> 1 unité = une fraction de flux E/S en méthanation

    for k in data:
        if k!="annee" and k!="alea" and k!="stock" and k!="carte":
            nbNuc += data[k]["centraleNuc"]
            nbTherm += data[k]["centraleTherm"]
            nbBio += data[k]["biomasse"]
            nbOn += data[k]["eolienneON"]
            nbOff += data[k]["eolienneOFF"]
            nbPv += data[k]["panneauPV"]

    initFiles()

    # Definition des scenarios (Negawatt, ADEME, RTE pour 2050)
    # Les autres scenarios sont faits mains à partir des données de Quirion

    ADEME = pd.read_csv("mix_data/ADEME_25-50.csv", header=None)
    ADEME.columns = ["heures", "d2050", "d2045", "d2040", "d2035", "d2030", "d2025"]

    RTE = pd.read_csv("mix_data/RTE_25-50.csv", header=None)
    RTE.columns = ["heures", "d2050", "d2045", "d2040", "d2035", "d2030", "d2025"]

    NEGAWATT = pd.read_csv("mix_data/NEGAWATT_25-50.csv", header=None)
    NEGAWATT.columns = ["heures", "d2050", "d2045", "d2040", "d2035", "d2030", "d2025"]

    ScenarList = {"ADEME":ADEME , "RTE":RTE , "NEGAWATT":NEGAWATT}

    #lecture du fichier savedata.json qui lit les données du tour précédent
    if data["annee"] == 2030:
        jeu = [{"nbeolON": 0, "nbeolOFF": 0, "nbPV": 0, "nbTherm": 0, "nbNuc": 0, "nbBio": 0}, 0, 0, 
                {"Uranium": 100, "Hydro": 100, "Bois": 100, "Dechet" : 0}, 
                {"hdf": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, "idf": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, 
                "est": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, "nor": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, 
                "occ": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, "pac": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, 
                "bre": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, "cvl": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, 
                "pll": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, "naq": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, 
                "ara": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, "bfc": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}, 
                "cor": {"eolienneON": 0, "eolienneOFF": 0, "panneauPV": 0}}, 
                {"hdf": {"eolienneON": 4, "eolienneOFF": 2, "panneauPV": 24, "biomasse": 27}, 
                "idf": {"eolienneON": 2, "eolienneOFF": 0, "panneauPV": 9, "biomasse": 7}, 
                "est": {"eolienneON": 8, "eolienneOFF": 0, "panneauPV": 44, "biomasse": 38}, 
                "nor": {"eolienneON": 4, "eolienneOFF": 5, "panneauPV": 23, "biomasse": 26}, 
                "occ": {"eolienneON": 10, "eolienneOFF": 4, "panneauPV": 56, "biomasse": 44}, 
                "pac": {"eolienneON": 4, "eolienneOFF": 3, "panneauPV": 24, "biomasse": 9}, 
                "bre": {"eolienneON": 4, "eolienneOFF": 12, "panneauPV": 21, "biomasse": 21}, 
                "cvl": {"eolienneON": 5, "eolienneOFF": 0, "panneauPV": 30, "biomasse": 30}, 
                "pll": {"eolienneON": 4, "eolienneOFF": 4, "panneauPV": 25, "biomasse": 27}, 
                "naq": {"eolienneON": 11, "eolienneOFF": 12, "panneauPV": 65, "biomasse": 53}, 
                "ara": {"eolienneON": 9, "eolienneOFF": 0, "panneauPV": 54, "biomasse": 38}, 
                "bfc": {"eolienneON": 6, "eolienneOFF": 0, "panneauPV": 37, "biomasse": 32}, 
                "cor": {"eolienneON": 1, "eolienneOFF": 3, "panneauPV": 7, "biomasse": 4}}]
    
    else:
        with open('game_data/savedata.json', 'r') as readOutput:
            jeu = json.load(readOutput)

    # Entrée : scenario, nb technos
    result = mix(RTE["d{}".format(data["annee"])],
            "RTE {}".format(data["annee"]),
            data["hdf"], data["idf"], data["est"], data["nor"], data["occ"], data["pac"], data["bre"], 
            data["cvl"], data["pll"], data["naq"], data["ara"], data["bfc"], data["cor"], 
            nbOn, nbOff, nbPv, nbNuc, nbTherm, nbBio, data["stock"]/10, data["alea"], jeu)

    with open('game_data/production_output.json', 'w') as f:
            json.dump(result, f)