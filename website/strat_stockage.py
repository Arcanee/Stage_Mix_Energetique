import numpy as np
from collections import Counter
import sys
import json
import pandas as pd
import boto3
import os


def initFiles():
    # Les lignes suivantes permettent d'avoir accès à un dépôt de données de manière chiffrée
    s3_endpoint_url = 'https://object-rook-ceph.apps.math.cnrs.fr/'
    s3_access_key_id = '26R58AYH5Z1X4IUNF1NQ' # le contenu de secrets/dossal
    s3_secret_access_key = 'ODX7fukdCQTZ67n8fKLPwrup9OcQVU45RtnxfFHT' # le contenu de secrets/dossal
    s3_bucket = 'dossal-enr2050'
    s3 = boto3.client('s3','',endpoint_url = s3_endpoint_url,aws_access_key_id = s3_access_key_id,
                    aws_secret_access_key = s3_secret_access_key)

    # File DL : (key, file to dl, location)
    if not os.path.isfile('data/demand2050_negawatt.csv'):
        s3.download_file(s3_bucket, "demand2050_negawatt.csv", "data/demand2050_negawatt.csv")
        s3.download_file(s3_bucket, "demand2050_RTE.csv", "data/demand2050_RTE.csv")
        s3.download_file(s3_bucket, "demand2050_ADEME.csv", "data/demand2050_ADEME.csv")
        s3.download_file(s3_bucket, "vre_profiles2006.csv", "data/vre_profiles2006.csv")
        s3.download_file(s3_bucket, "run_of_river.csv", "data/run_of_river.csv")
        s3.download_file(s3_bucket, "lake_inflows.csv", "data/lake_inflows.csv")


# Definition de la classe Techno
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


# Definition des fonctions de charge et décharge d'une technologie
def load(tec,k,astocker):
    if astocker==0:
        out=0
    else:
        temp=min(astocker*tec.etain,tec.vol-tec.stored[k-1],tec.S*tec.etain)
        tec.stored[k:]=tec.stored[k-1]+temp
        out=astocker-temp/tec.etain
    return out


def unload(tec,k,aproduire, endmonthlake, prod=True):
    if aproduire==0:
        out=0
    else:
        temp=min(aproduire/tec.etaout,tec.stored[k],tec.Q/tec.etaout)
        if tec.name=='Lake':
            tec.stored[k:int(endmonthlake[k])]=tec.stored[k]-temp
        else:
            tec.stored[k:]=tec.stored[k]-temp
        if prod:
            tec.prod[k]=temp*tec.etaout
        out=aproduire-temp*tec.etaout
    return out


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
def cycle(k):
    N = 8
    n = 1/N
    
    # Intervalles des 3 parties importantes du cycle, pour chaque groupe
    A_ranges = [((2180+6570)%8760,(2180+8030)%8760), ((2920+6570)%8760,(2920+8030)%8760), 
               ((3650+6570)%8760,(3650+8030)%8760), ((4400+6570)%8760,(4400+8030)%8760),
               ((5130+6570)%8760,(5130+8030)%8760), ((5900+6570)%8760,(5900+8030)%8760),
               ((6732+6570)%8760,(6732+8030)%8760), ((7580+6570)%8760,(7580+8030)%8760)]
    
    B_ranges = [((2180+8030)%8760,2180), ((2920+8030)%8760,2920), ((3650+8030)%8760,3650),
               ((4400+8030)%8760,4400), ((5130+8030)%8760,5130), ((5900+8030)%8760,5900),
               ((6732+8030)%8760,6732), ((7580+8030)%8760,7580)]
    
    C_ranges = [(2180, (2180+730)%8760), (2920, (2920+730)%8760), (3650, (3650+730)%8760),
               (4400, (4400+730)%8760), (5130, (5130+730)%8760), (5900, (5900+730)%8760),
               (6732, (6732+730)%8760), (7580, (7580+730)%8760)]

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


# Si la demande est trop faible ou nulle, on produit quand même à hauteur de 20%
def nucProd(tec, k, aproduire):
    MinMax = cycle(k)
    Pmin = MinMax[0]
    Pmax = MinMax[1]
    
    if aproduire > tec.Q/tec.etaout * Pmin:
        temp=min(aproduire/tec.etaout,tec.Q*Pmax/tec.etaout)
        tec.prod[k]=temp*tec.etaout
    else:
        tec.prod[k] = tec.Q/tec.etaout * Pmin
    
    out = aproduire - tec.prod[k]
    
    return out


# Centrales thermiques
def thermProd(tec, k, aproduire):
    temp=min(aproduire/tec.etaout,tec.Q/tec.etaout)
    tec.prod[k]=temp*tec.etaout
    out=aproduire-tec.prod[k]
    
    return out


# Méthode 1 : intervalles de confiance
def certitudeglobal(y1,y2,y3):
    
    ##distribution écretage : min, max, moyenne et écart-type 
    emoy = np.mean(y1[y1!=-1]) ##moyenne de l'échantillon //
    eetype = np.std(y1[y1!=-1]) ##ecart-type de l'échantillon //

    ##distribution pénurie : min, max, moyenne, écart-type
    pmoy = np.mean(y2[y2!=-1])
    petype = np.std(y2[y2!=-1])

    certitude_interval = np.zeros(3)
    certitude_interval[0] = pmoy + (1.76)*(petype)/np.sqrt(len(y2[y2!=-1])) ##98% sur pénurie (valeur sup de l'IC)
    certitude_interval[1] = emoy - (2.33)*(eetype)/np.sqrt(len(y1[y1!=-1])) ##99% sur écretage (valeur inf de l'IC)
    certitude_interval[2] = (certitude_interval[0] + certitude_interval[1])/2 ##valeur moyenne entre 98% et 99% 

    return certitude_interval

    
# Méthode 2 : recherche itérative du meilleur seuil
# Cette fonction regarde la proportion de pénuries parmi les points au-dessus/sous du seuil, pour chaque seuil
# Et choisit le seuil à la proportion la plus proche du critère voulu

# Ecretage / Penurie / Ok
def seuil(a,b,c, crit, mode):
        
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


def StratStockage(prodres,n,Phs,Battery,Methanation,Lake,Thermal,Nuclear, endmonthlake):
    Surplus=np.zeros(n)
    ##Ajout paramètre Penurie
    Manque = np.zeros(n)
    #Definition d'un ordre sur les differentes technologies de stockage et destockage
    Tecstock= {"Phs" : Phs,"Battery" : Battery, "Methanation": Methanation}
    Tecstock2= {"Methanation": Methanation,"Phs" : Phs,"Battery" : Battery}
        
    Tecdestock= {"Battery" : Battery,"Phs" : Phs,"Methanation": Methanation,"Lake" : Lake}
    
    for k in np.arange(1,n):
        if prodres[k]>0:
            
            # La production min de nucléaire s'ajoute à la qté d'énergie à stocker
            nucMin = nucProd(Nuclear, k, 0)
            Astocker = prodres[k] + abs(nucMin)
            
            for tec in Tecstock:
                Astocker=load(Tecstock[tec],k,Astocker)
            Surplus[k]=Astocker

        else:
            Aproduire=-prodres[k]
            
            Aproduire = nucProd(Nuclear, k, Aproduire)
            
            for tec in Tecdestock:
                Aproduire=unload(Tecdestock[tec],k,Aproduire, endmonthlake)
                
            # Si le nucléaire n'a pas suffi, on fait tourner les centrales thermiques
            if Aproduire > 0:
                Aproduire = thermProd(Thermal, k, Aproduire)
                
            ##liste penurie --> pour savoir si il y a pénurie dans la production d'électricité 
            Manque[k]=Aproduire
                
    return Surplus,Manque


def StratStockagev2(prodres,n,Phs,Battery,Methanation,Lake,Thermal,Nuclear, I0, I1, I2, endmonthlake):
    Surplus=np.zeros(n)
    ##Ajout paramètre Penurie
    Manque = np.zeros(n)
    
    #Definition d'un ordre sur les differentes technologies de stockage et destockage
    Tecstock2= {"Methanation": Methanation,"Phs" : Phs,"Battery" : Battery} ##on stocke du gaz zone 1,2
    Tecstock3= {"Phs" : Phs,"Battery" : Battery, "Methanation": Methanation} ## zone 3
    Tecstock4 = {"Battery" : Battery, "Phs" : Phs,"Methanation": Methanation} ## zone 4
        
    Tecdestock1= {"Battery" : Battery,"Phs" : Phs,"Methanation": Methanation,"Lake" : Lake} #zone 1
    Tecdestock2 = {"Phs": Phs, "Battery": Battery, "Methanation" : Methanation, "Lake" : Lake} ## zone 2
    Tecdestock3 = {"Methanation" : Methanation, "Battery" : Battery, "Phs": Phs, "Lake" : Lake} ## zone 3,4
    
    for k in np.arange(1,n):
        stock_PB = Phs.stored[k-1] + Battery.stored[k-1]
        
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
                Astocker=load(strat_stock[tec],k,Astocker)
            Surplus[k]=Astocker

        else:
            Aproduire=-prodres[k]

            Aproduire = nucProd(Nuclear, k, Aproduire)

            for tec in strat_destock:
                Aproduire=unload(strat_destock[tec],k,Aproduire, endmonthlake)

            # Si le nucléaire n'a pas suffi, on fait tourner les centrales thermiques
            if Aproduire > 0:
                Aproduire = thermProd(Thermal, k, Aproduire)
            
            ##liste penurie --> pour savoir si il y a pénurie dans la production d'électricité 
            Manque[k]=Aproduire
            
                
    return Surplus,Manque


## Etude d'Optimisation de stratégie de stockage et de déstockage du Mix énergetique 
def mix(scenario, on, off, pvol, th, nuc):
    Conso = scenario
    onshore= on
    offshore = off
    
    thermique = th
    nucleaire = nuc
    
    pv= pvol

    
    # Profils de production sur l'année 2006 pour les différentes technologies
    vre2006 = pd.read_csv("data/vre_profiles2006.csv", header=None)
    vre2006.columns = ["vre", "heure", "prod2"]

    #Production électrique en 2006 pour toutes les technologies
    prod2006=vre2006.prod2

    # Production par technologie
    N=8760
    prod2006_offshore=prod2006[0:N]
    prod2006_onshore=prod2006[N:2*N]
    prod2006_pv=prod2006[2*N:3*N]
    heures=vre2006.heure[0:N]


    # Definition des productions électriques des rivières et lacs 
    coefriv = 13
    river = pd.read_csv("data/run_of_river.csv", header=None)
    river.columns = ["heures", "prod2"]
    rivprod=river.prod2

    lake = pd.read_csv("data/lake_inflows.csv", header=None)
    lake.columns = ["month", "prod2"]
    lakeprod=lake.prod2

    # Calcul de ce qui est stocké dans les lacs pour chaque mois
    horlake=np.array([0,31,31+28,31+28+31,31+28+31+30,31+28+31+30+31,31+28+31+30+31+30,31+28+31+30+31+30+31\
                ,31+28+31+30+31+30+31+31,31+28+31+30+31+30+31+31+30,31+28+31+30+31+30+31+31+30+31\
                ,31+28+31+30+31+30+31+31+30+31+30,31+28+31+30+31+30+31+31+30+31+30+31])*24

    storedlake=np.zeros(8760)
    endmonthlake=np.zeros(8760)
    for k in np.arange(12):
        storedlake[horlake[k]:horlake[k+1]]=1000*lakeprod[k]
    for k in np.arange(12):
        endmonthlake[horlake[k]:horlake[k+1]]=int(horlake[k+1])


    # Calcul de la production residuelle
    prodresiduelle=np.array(prod2006_offshore)*offshore\
                +np.array(prod2006_onshore)*onshore\
                +np.array(prod2006_pv)*pv+coefriv*rivprod-Conso

    
    # Puissance centrales territoire : 18.54 GWe répartis sur 24 centrales (EDF)
    # Rendement méca (inutile ici) : ~35% généralement (Wiki)
    T = Techno('Centrale thermique', None, np.zeros(8760), None, 1, 0.7725*thermique, None, None)
    # Puissance : 1.08 GWe (EDF)
    # Même rendement
    N = Techno('Réacteur nucléaire', None, np.zeros(8760), None, 1, 1.08*nucleaire, None, None)
    
    # Definition des differentes technologies
    P=Techno('Phs', np.ones(8760)*90, np.zeros(8760), 0.95, 0.9, 9.3, 9.3, 180)
    B=Techno('Battery', np.ones(8760)*37.07, np.zeros(8760), 0.9, 0.95, 20.08, 20.08, 74.14)
    M=Techno('Methanation', np.ones(8760)*62500, np.zeros(8760), 0.59, 0.45, 32.93, 7.66, 125000)    
    L=Techno('Lake', storedlake, np.zeros(8760), 1, 1, 10, 10, 2000)   

        
    # résultats de la strat initiale
    # Renvoie Surplus,Pénurie et met à jour Phs,Battery,Methanation,Lake,Therm,Nuc
    s,p=StratStockage(prodresiduelle,8760,P,B,M,L,T,N, endmonthlake)
    
    
    #############################
    ## NUAGES DE POINTS POUR OPTIMISER LE STOCKAGE
    
    stockage_PB = np.zeros(365) ##liste qui va servir à enregister les stockages Phs + Battery à l'heure H pour tous les jours
    
    stockmax=180+74.14 ##stockage maximum total = max total stockage Phs + max total stockage Battery
    x = np.arange(365) ##nombre de jours sur l'année --> va de 1 à 365
    x0 = np.arange(8760)
    
    
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
    ##Cetitude interval pour toutes les heures
    certitude_interval0 = np.zeros(24)
    certitude_interval1 = np.zeros(24)
    certitude_interval2 = np.zeros(24)
    
    seuils_top = np.zeros(24)
    seuils_mid = np.zeros(24)
    seuils_bot = np.zeros(24)
    
    for h in range(24):
    
        for jour in range(365): ##on regarde tous les jours de l'année
        
            stockage_PB[jour]=StockPB[jour*24+h] #Au jour jour, valeur du stock Phs + Battery
        
            ##on regarde dans les 24h qui suivent si il y a écrêtage, pénurie ou aucun des deux
            for heure in range(24): 
                t = (jour * 24 + h + heure) % 8760
                
                if s[t] > 0 and StockPB[t] == stockmax : ##cas écrêtage
                    x1[jour]=jour+1 ##on note le jour précèdant jour avec écrêtage
                    y1[jour]=stockage_PB[jour] ##on note le stock du jour précèdant jour avec écrêtage
            
                elif p[t] > 0 : ##cas pénurie
                    x2[jour]=jour+1 ##mêmes explications mais pour pénurie
                    y2[jour]=stockage_PB[jour]
                
                else : ##cas ni écrêtage, ni pénurie
                    x3[jour]=jour+1 ##mêmes explications mais avec ni écrêtage, ni pénurie
                    y3[jour]=stockage_PB[jour]
                
                if x1[jour]==x2[jour]: ##si écretage et pénurie le même jour, on considère que c'est une pénurie 
                    x1[jour]=-1
                    y1[jour]=-1
            
            
        certitude_interval0[h] = certitudeglobal(y1,y2,y3)[0]
        certitude_interval1[h] = certitudeglobal(y1,y2,y3)[1]
        certitude_interval2[h] = certitudeglobal(y1,y2,y3)[2]
        
        seuils_top[h] = seuil(y1,y2,y3, 0.02, "u")
        seuils_bot[h] = seuil(y1,y2,y3, 0.9, "d")
        seuils_mid[h] = (seuils_top[h] + seuils_bot[h]) / 2
        
    
        
        
    # Renvoie Surplus,Pénurie, et met à jour les technos
    
    #Décommenter pour méthode 1 (intervalles de confiance)
    s,p=StratStockagev2(prodresiduelle,8760,P,B,M,L,T,N,
                                    certitude_interval0,certitude_interval2,certitude_interval1, endmonthlake)
    
    #Décommenter pour méthode 2 (recherche itérative du meilleur seuil)
    #s,p,P,B,M,L,T,N=StratStockagev2(prodresiduelle,N,Phs,Battery,Methanation,Lake,Thermal,Nuclear,
    #                               seuils_bot, seuils_mid, seuils_top)
    

    prod_Meth=np.array(M.prod)
    prod_Phs=np.array(P.prod)       
    prod_Lake=np.array(L.prod)
    prod_Battery=np.array(B.prod)
    prod_Thermal=np.array(T.prod)
    prod_Nuclear=np.array(N.prod)
    
    

    # Infos qu'on peut retourner (plusieurs axes temporels et 2 stratégies sont possibles):
    # - Stock PHS / Batteries 
    # - Combien de surpus / pénurie ***
    # - Evolution des seuils
    # - (Mix des 2 premiers points)
    # - Stocks de gaz ***
    # - Courbes de production X demande ***
    # - Prod résiduelle
        
    nbS = 0
    nbP = 0

    for i in range(len(s)):
        if s[i] > 0:
            nbS += 1
        if p[i] > 0:
            nbP += 1
        
                                        
    result = ["Delta gaz : {}".format(M.stored[8759]-M.stored[0]),
            "Demande : {} / Production : {}".format(np.sum(Conso), np.sum(prod_Meth+prod_Phs+prod_Lake+prod_Battery+prod_Thermal+prod_Nuclear+
                                                np.array(prod2006_offshore)*off+np.array(prod2006_onshore)*on+np.array(prod2006_pv)*pvol+rivprod*coefriv)),
            "{} surplus, {} pénuries".format(nbS, nbP)
            ]

    for r in result:
        print(r)

    return 0




def main(tour, nbOn, nbOff, nbPv, nbTherm, nbNuc):
    initFiles()

    #Definition des scenarios (Negawatt, ADEME, RTE)
    ADEME = pd.read_csv("data/demand2050_ADEME.csv", header=None)
    ADEME.columns = ["heures", "demande"]

    RTE = pd.read_csv("data/demand2050_RTE.csv", header=None)
    RTE.columns = ["heures", "demande"]

    Negawatt = pd.read_csv("data/demand2050_negawatt.csv", header=None)
    Negawatt.columns = ["heures", "demande"]

    T1 = pd.read_csv("data/T1.csv", header=None, sep=';', decimal=',')
    T1.columns = ["heures", "d2025", "d2026", "d2027" ,"d2028", "d2029"]

    T2 = pd.read_csv("data/T2.csv", header=None, sep=';', decimal=',')
    T2.columns = ["heures", "d2030", "d2031", "d2032" ,"d2033", "d2034"]

    T3 = pd.read_csv("data/T3.csv", header=None, sep=';', decimal=',')
    T3.columns = ["heures", "d2035", "d2036", "d2037" ,"d2038", "d2039"]

    T4 = pd.read_csv("data/T4.csv", header=None, sep=';', decimal=',')
    T4.columns = ["heures", "d2040", "d2041", "d2042" ,"d2043", "d2044"]

    T5 = pd.read_csv("data/T5.csv", header=None, sep=';', decimal=',')
    T5.columns = ["heures", "d2045", "d2046", "d2047" ,"d2048", "d2049"]

    Scenario= {"RTE":RTE.demande, "ADEME":ADEME.demande, "Negawatt":Negawatt.demande,
            "T1_1":T1.d2025, "T1_2":T1.d2026, "T1_3":T1.d2027, "T1_4":T1.d2028, "T1_5":T1.d2029,
            "T2_1":T2.d2030, "T2_2":T2.d2031, "T2_3":T2.d2032, "T2_4":T2.d2033, "T2_5":T2.d2034,
            "T3_1":T3.d2035, "T3_2":T3.d2036, "T3_3":T3.d2037, "T3_4":T3.d2038, "T3_5":T3.d2039,
            "T4_1":T4.d2040, "T4_2":T4.d2041, "T4_3":T4.d2042, "T4_4":T4.d2043, "T4_5":T4.d2044,
            "T5_1":T5.d2045, "T5_2":T5.d2046, "T5_3":T5.d2047, "T5_4":T5.d2048, "T5_5":T5.d2049}

    # Les scenarios faits mains sont basés sur les données de Quirion

    

    # Entrée : scenario, nb technos
    #print(mix(Scenario["T{}_1".format(tour)], nbOn, nbOff, nbPv, nbTherm, nbNuc))
    mix(ADEME.demande, nbOn, nbOff, nbPv, nbTherm, nbNuc)

    return 0



main(1, 75, 13, 122, 0, 12)