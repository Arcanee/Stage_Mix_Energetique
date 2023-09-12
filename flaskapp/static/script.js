$(function() {

    const maps = {
        "France" : [["hdf", "Hauts-de-France"],
                    ["bre", "Bretagne"],
                    ["nor", "Normandie"],
                    ["idf", "Ile-de-France"],
                    ["est", "Grand Est"],
                    ["cvl", "Centre-Val de Loire"],
                    ["pll", "Pays de la Loire"],
                    ["bfc", "Bourgogne-Franche-Comté"],
                    ["naq", "Nouvelle-Aquitaine"],
                    ["ara", "Auvergne-Rhône-Alpes"],
                    ["occ", "Occitanie"],
                    ["pac", "Provence-Alpes-Côte d'Azur"],
                    ["cor", "Corse"]]
    };

    const pions = [ ["eolienneON", "Eoliennes on."],
                    ["eolienneOFF", "Eoliennes off."],
                    ["panneauPV", "Panneaux PV"],
                    ["centraleNuc", "Centrales nuc."],
                    ["methanation", "Méthanation"],
                    ["biomasse", "Biomasse"],
    ];

    const aleas = ["", "MEGC1", "MEGC2", "MEGC3", "MEMFDC1", "MEMFDC2", "MEMFDC3",
                    "MECS1", "MECS2", "MECS3", "MEVUAPV1", "MEVUAPV2", "MEVUAPV3",
                    "MEMDA1", "MEMDA2", "MEMDA3", "MEMP1", "MEMP2", "MEMP3",
                    "MEGDT1", "MEGDT2", "MEGDT3"
    ];

    let exitConfirm = false; // METTRE A TRUE LORS DU DEPLOIEMENT

    onbeforeunload = function() {
        if (exitConfirm) return "Etes-vous sûr(e) de vouloir quitter cette page ? Vos modifications seront perdues."
    }




    if (document.title == "Jeu mix énergétique") {

        function displayError(reason) {
            let msg;
            const modal = new bootstrap.Modal($("#errModal"));

            switch (reason) {
                case "input":
                    msg = "Veuillez choisir votre groupe et votre équipe.";
                    break;

                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;

                default:
                    break;
            }

            $("#errorMsg").html(msg);
            modal.toggle();
        }

        $(".logInBtn").click((e) => {
            const data = [$("#grpInput").val(), $("#teamInput").val(), e.target.id];

            if (data[0] != "default" && data[1] != "default") {
                $.ajax({
                    url: "/set_group",
                    type: "POST",
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data, textStatus, jqXHR) {
                        if (data[0] == "log_in_success") {
                            location.href = "/photo";
                        } else {
                            displayError("http");
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        displayError("http");
                    }
                    });

            } else {
                displayError("input");
            }
        });

        $("#sous-titre").fadeIn(function() {
            $("#submit").fadeIn();
        });
    }



    if (document.title == "Détection photo - Jeu mix énergétique") {

        const imgData = document.createElement('img');

        let processing = false;

        $("#sous-titre").fadeIn(function() {
            $("#noPhoto").fadeIn();
        });
        

        function displayError(reason) {
            let msg;
            const modal = new bootstrap.Modal($("#errModal"));

            switch (reason) {
                case "img":
                    msg = "Le plateau n'a pas été correctement détecté. Essayez de faire en sorte que tout le plateau soit visible et vu du dessus.";
                    break;
                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;
                case "input":
                    msg = "Vous n'avez rien envoyé. Prenez une photo ou choisissez-en une dans votre bibliothèque.";
                    break;

                default:
                    break;
            }

            $("#errorMsg").html(msg);
            modal.toggle();
        }


        function sendImg(img) {            
            processing = true;
            $('#imgOutput').html('<span class="spinner-border spinner-border-sm"></span>&nbsp;&nbsp;Chargement...');
            
            $.ajax({
            url: "/detector",
            type: "POST",
            data: JSON.stringify({image: img}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                $('#imgOutput').html('Envoyer');
                processing = false;
                if (data[0] == "success") {
                    location.href = "/detection";
                } else {
                    displayError("img");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                processing = false;
                $('#imgOutput').html('Envoyer');
                displayError("http");
            }
            });
        }
       
        
        $('#imgOutput').click(() => {
            if (!processing) {
                const fichier = document.getElementById("imgInput").files[0];
                if (fichier) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        sendImg(reader.result);
                    }
                    reader.readAsDataURL(fichier);
                } 
                
                else {
                    displayError("input");
                }
            }
        });

        $('#noPhotoBtn').click(() => {
            location.href = "/manual";
        });
    
    }



    if (document.title == "Vérification - Jeu mix énergétique") {

        let detectionData = null;
        let mixData = null;

        function btnCallbacks(plus, minus, nb) {
            minus.click(() => {
                nb.val((parseInt(nb.val()) > 0 ? parseInt(nb.val())-1 : 0));
            });

            plus.click(() => {
                nb.val((parseInt(nb.val()) < 100 ? parseInt(nb.val())+1 : 100));
            });        
        }

        function initContent(map) {
            let divStr = "";

            for (const reg of maps[map]) {
                divStr += `<h3 class="row mt-5 ps-2 bg-info rounded bg-opacity-50 justify-content-center" id="${reg[0]}">${reg[1]}</h3>`;
                for (const pion of pions) {
                    divStr +=
                    `<div class="row justify-content-around">

                        <div class="col-5 mt-2">${pion[1]}</div>
                        
                        <div class="col-6 mt-2">
                            <div class="row justify-content-end">
                                <div class="form-outline col-6">
                                    <input value="0" min="0" max="100" type="number" id="${reg[0]}_${pion[0]}" class="form-control"/>
                                </div>
                                <button class="btn btn-basic col-2" type="button" id="${reg[0]}_${pion[0]}_minus">➖</button>
                                <button class="btn btn-basic col-2" type="button" id="${reg[0]}_${pion[0]}_plus">➕</button>
                            </div>
                        </div>

                    </div>`;
                }
            }

            $("#mid").html(divStr);

            for (const reg of maps[$("#carte").val()]) {
                for (const pion of pions) {
                    minusBtn = $(`#${reg[0]}_${pion[0]}_minus`);
                    plusBtn = $(`#${reg[0]}_${pion[0]}_plus`);
                    nb = $(`#${reg[0]}_${pion[0]}`);
                    
                    btnCallbacks(plusBtn, minusBtn, nb);
                }
            }
        }

        function displayError(reason, details) {
            let msg;
            const modal = new bootstrap.Modal($("#errModal"));

            switch (reason) {
                case "err":
                    msg = "Une erreur inattendue est survenue.";
                    break;
                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;
                case "errAnnee":
                    msg = `L'année sélectionnée ne correspond pas au tour actuel (valeur attendue: ${details}).`;
                    break;
                case "errStock":
                    msg = `Vous ne pouvez pas enlever de batteries (valeur minimale: ${details}).`;
                    break;
                case "errCarte":
                    msg = `Vous ne pouvez pas changer de carte au milieu d'une partie (carte actuelle: ${details}).`;
                    break;
                case "errSol":
                    msg = `Vous avez placé trop de ${details[1]} en ${details[0]} (maximum: ${details[2]}).`;
                    break;
                case "errNuc":
                    msg = `La crise sociale en cours vous empêche de placer plus de réacteurs nucléaires (vous en avez ajouté ${details}).`;
                    break;
                default:
                    break;
            }

            $("#errorMsg").html(msg);
            modal.toggle();
        }

        function saveData() {
            let err = 0;
            let result;
            const data = {};
            const stockStr = $("#stock").val();
            const stock = parseFloat(stockStr);

            if ($("#carte").val() == "default") {
                alert("Veuillez sélectionner une carte");
                err = 1;

            } else if ($("#annee").val() == "default") {
                alert("Veuillez sélectionner une année");
                err = 1;

            } else if (!(aleas.includes($("#alea").val()))) {
                alert("Le code aléa est invalide");
                err = 1;

            } else if (stockStr == "" || stock < 1 || stock > 10 || !(Number.isInteger(stock))) {
                alert("Veuillez entrer une valeur entière de stock entre 1 et 10");
                err = 1;

            } else {
                data["actif"] = true;
                data["carte"] = $("#carte").val();
                data["annee"] = parseInt($("#annee").val());
                data["stock"] = parseInt($("#stock").val());
                data["alea"] = $("#alea").val();


                for (const reg of maps[$("#carte").val()]) {
                    data[reg[0]] = {};
                    for (const p of pions) {
                        const str = $(`#${reg[0]}_${p[0]}`).val();
                        const nb = parseFloat(str);
                        if (str == "" || nb < 0 || nb > 100 || !(Number.isInteger(nb))) {
                            alert("Veuillez entrer des nombres entiers entre 0 et 100 seulement.");
                            err = 1;
                        }
                        data[reg[0]][p[0]] = nb;
                    }
                }
            }

            result = err ? false : JSON.stringify(data);
            return result;
        }

        function fillPage() {
            if (!mixData.actif) {
                $('#carte').val(detectionData.carte);
                $("#stock").val(detectionData.stock.toString());
                $("#annee").val(detectionData.annee.toString());

                // Squelette de la page pour la carte qui a été détectée
                initContent(detectionData.carte);

                // Remplissage de la page avec les valeurs récupérées
                for (const reg in detectionData) {
                    if (reg!="carte" && reg!="annee" && reg!="stock") {
                        for (const p in detectionData[reg]) {
                            $(`#${reg}_${p}`).val(detectionData[reg][p]);
                        }
                    }
                }
            }

            else {
                $("#carte").val(mixData.carte);
                $("#annee").val(mixData.annee.toString());
                $("#stock").val(mixData.stock.toString());
                $("#alea").val(mixData.alea);
                initContent(mixData.carte);
    
                for (const reg of maps[mixData.carte]) {
                    for (const pion of pions) {
                        $(`#${reg[0]}_${pion[0]}`).val(mixData[reg[0]][pion[0]]);
                    }
                }
            }
        }


        $("#carte").change(() => {
            const val = $("#carte").val();
            if (val != "default") {
                initContent(val);
                $("#mid").hide();
                $("#bot").hide();
                $("#mid").fadeIn();
                $("#bot").fadeIn();
            }
        });

        $('#computeResults').click(() => {
            const dataProd = saveData();

            if (dataProd != false) {
                $('#computeResults').html('<span class="spinner-border spinner-border-sm"></span>&nbsp;&nbsp;Chargement...');
                exitConfirm = false;
                $.ajax({
                    url: "/production",
                    type: "POST",
                    data: dataProd,
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data, textStatus, jqXHR) {
                        $('#computeResults').html('Valider');
                        if (data[0] == "success") {
                            location.href = "/results";
                        } else {
                            displayError(data[0], data[1]);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        $('#computeResults').html('Valider');
                        displayError("http", null);
                    }
                });
            }
        });

        $(".backHome").click(() => {
            location.href = "/photo";
        });



        // DEBUT EXECUTION PAGE

        $.ajax({
            url: "/get_detection",
            type: "GET",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                detectionData = data;
                $.ajax({
                    url: "/get_mix",
                    type: "GET",
                    dataType: "json",
                    success: function (data, textStatus, jqXHR) {
                        mixData = data;
                        fillPage();
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        displayError("http");
                    }
                });
            },
            error: function(jqXHR, textStatus, errorThrown) {
                displayError("http");
            }
        });

        

        $("#top").fadeIn();
        $("#mid").fadeIn();
        $("#bot").fadeIn();    
    }



    if (document.title == "Entrée manuelle - Jeu mix énergétique") {

        let mixData = null;

        function btnCallbacks(plus, minus, nb) {
            minus.click(() => {
                nb.val((parseInt(nb.val()) > 0 ? parseInt(nb.val())-1 : 0));
            });

            plus.click(() => {
                nb.val((parseInt(nb.val()) < 100 ? parseInt(nb.val())+1 : 100));
            });        
        }

        function initContent(map) {
            let divStr = "";

            for (const reg of maps[map]) {
                divStr += `<h3 class="row mt-5 ps-2 bg-info rounded bg-opacity-50 justify-content-center" id="${reg[0]}">${reg[1]}</h3>`;
                for (const pion of pions) {
                    divStr +=
                    `<div class="row justify-content-around">

                        <div class="col-4 mt-2">${pion[1]}</div>

                        <div class="col-6 mt-2">
                            <div class="row justify-content-end">
                                <div class="form-outline col-6">
                                    <input value="0" min="0" max="100" type="number" id="${reg[0]}_${pion[0]}" class="form-control"/>
                                </div>
                                <button class="btn btn-basic col-2" type="button" id="${reg[0]}_${pion[0]}_minus">➖</button>
                                <button class="btn btn-basic col-2" type="button" id="${reg[0]}_${pion[0]}_plus">➕</button>
                            </div>
                        </div>

                    </div>`;
                }
            }

            $("#mid").html(divStr);

            for (const reg of maps[$("#carte").val()]) {
                for (const pion of pions) {
                    minusBtn = $(`#${reg[0]}_${pion[0]}_minus`);
                    plusBtn = $(`#${reg[0]}_${pion[0]}_plus`);
                    nb = $(`#${reg[0]}_${pion[0]}`);
                    
                    btnCallbacks(plusBtn, minusBtn, nb);
                }
            }
        }

        function displayError(reason, details) {
            let msg;
            const modal = new bootstrap.Modal($("#errModal"));

            switch (reason) {
                case "err":
                    msg = "Une erreur inattendue est survenue.";
                    break;
                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;
                case "errAnnee":
                    msg = `L'année sélectionnée ne correpond pas au tour actuel (valeur attendue: ${details}).`;
                    break;
                case "errStock":
                    msg = `Vous ne pouvez pas enlever de batteries (valeur minimale: ${details}).`;
                    break;
                case "errCarte":
                    msg = `Vous ne pouvez pas changer de carte au milieu d'une partie (carte actuelle: ${details}).`;
                    break;
                case "errSol":
                    msg = `Vous avez placé trop de ${details[1]} en ${details[0]} (maximum: ${details[2]}).`;
                    break;
                case "errNuc":
                    msg = `La crise sociale en cours vous empêche de placer plus de réacteurs nucléaires (vous en avez ajouté ${details}).`;
                    break;
                default:
                    break;
            }

            $("#errorMsg").html(msg);
            modal.toggle();
        }

        function saveData() {
            let err = 0;
            let result;
            const data = {};
            const stockStr = $("#stock").val();
            const stock = parseFloat(stockStr);

            if ($("#carte").val() == "default") {
                alert("Veuillez sélectionner une carte");
                err = 1;

            } else if ($("#annee").val() == "default") {
                alert("Veuillez sélectionner une année");
                err = 1;

            } else if (!(aleas.includes($("#alea").val()))) {
                alert("Le code aléa est invalide");
                err = 1;

            } else if (stockStr == "" || stock < 1 || stock > 10 || !(Number.isInteger(stock))) {
                alert("Veuillez entrer une valeur entière de stock entre 1 et 10");
                err = 1;

            } else {
                data["actif"] = true;
                data["carte"] = $("#carte").val();
                data["annee"] = parseInt($("#annee").val());
                data["stock"] = parseInt($("#stock").val());
                data["alea"] = $("#alea").val();

                for (const reg of maps[$("#carte").val()]) {
                    data[reg[0]] = {};
                    for (const p of pions) {
                        const str = $(`#${reg[0]}_${p[0]}`).val();
                        const nb = parseFloat(str);
                        if (str == "" || nb < 0 || nb > 100 || !(Number.isInteger(nb))) {
                            alert("Veuillez entrer des nombres entiers entre 0 et 100 seulement.");
                            err = 1;
                        }
                        data[reg[0]][p[0]] = nb;
                    }
                }
            }

            result = err ? false : JSON.stringify(data);
            return result;
        }

        function fillPage() {
            if (!mixData.actif) {
                $("#carte").val("default");
                $("#annee").val("default");
                $("#stock").val("1");
                $("#alea").val("");
            } 
            
            else {
                $("#carte").val(mixData.carte);
                $("#annee").val(mixData.annee.toString());
                $("#stock").val(mixData.stock.toString());
                $("#alea").val(mixData.alea);
                initContent(mixData.carte);
    
                for (const reg of maps[mixData.carte]) {
                    for (const pion of pions) {
                        $(`#${reg[0]}_${pion[0]}`).val(mixData[reg[0]][pion[0]]);
                    }
                }

                $("#mid").hide();
                $("#bot").hide();
                $("#mid").fadeIn();
                $("#bot").fadeIn();
            }
        }

        $("#carte").change(() => {
            const val = $("#carte").val();
            if (val != "default") {
                initContent(val);
                $("#mid").hide();
                $("#bot").hide();
                $("#mid").fadeIn();
                $("#bot").fadeIn();
            }
        });

        $('.backHome').click(() => {
            location.href = "/photo";
        });

        $('#computeResults').click(() => {
            const dataProd = saveData();

            if (dataProd != false) {
                $('#computeResults').html('<span class="spinner-border spinner-border-sm"></span>&nbsp;&nbsp;Chargement...');
                exitConfirm = false;
                $.ajax({
                    url: "/production",
                    type: "POST",
                    data: dataProd,
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data, textStatus, jqXHR) {
                        $('#computeResults').html('Valider');
                        if (data[0] == "success") {
                            location.href = "/results";
                        } else {
                            displayError(data[0], data[1]);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        $('#computeResults').html('Valider');
                        displayError("http", null);
                    }
                });
            }
        });
    


        // DEBUT EXECUTION PAGE

        $.ajax({
            url: "/get_mix",
            type: "GET",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                mixData = data;
                fillPage();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                displayError("http");
            }
        });

        $("#top").fadeIn();
    }



    if (document.title == "Résultats - Jeu mix énergétique") {
        
        let resultsData = null;
        let resultsHistory = null;
        let mixData = null;

        function displayError(reason) {
            let msg;
            const modal = new bootstrap.Modal($("#errModal"));

            switch (reason) {
                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;
                default:
                    break;
            }

            $("#errorMsg").html(msg);
            modal.toggle();
        }

        
        function PuissanceInst() {
            // Define the chart to be drawn.
            const TotalP = (resultsData.puissanceBatterie +
                            resultsData.puissanceEolienneOFF +
                            resultsData.puissanceEolienneON +
                            resultsData.puissanceGaz +
                            resultsData.puissanceNucleaire +
                            resultsData.puissancePV +
                            resultsData.puissancePhs);


            let result1 = google.visualization.arrayToDataTable([['Technologie', 'Pourcentage'],
                ['EON', resultsData.puissanceEolienneON/TotalP],
                ['EOFF', resultsData.puissanceEolienneOFF/TotalP],
                ['Batterie', resultsData.puissanceBatterie/TotalP],
                ['Nucléaire', resultsData.puissanceNucleaire/TotalP],
                ['PV', resultsData.puissancePV/TotalP],
                ['Phs', resultsData.puissancePhs/TotalP],
                ['Gaz', resultsData.puissanceGaz/TotalP]
            ]);

            let options = {
                title: 'Puissance installée'
            };

            // Concaténez la valeur à la chaîne 'Puissance Installée' et affichez-la dans l'élément <div>
            let powStr = options.title + " : " + Math.round(TotalP) + " GW";
            $("#output").text(powStr);

        
            // Instantiate and draw the chart.
            let chart = new google.visualization.PieChart(document.getElementById('Chart_div'));
            chart.draw(result1, options);
        }
        function Prod(){
            let result2 = google.visualization.arrayToDataTable([
                ['Technologie', 'Production'],
                ['EON', resultsData.prodEolienneON],            // RGB value
                ['EOFF', resultsData.prodEolienneOFF],            // English color name
                ['Batterie', resultsData.prodBatterie],
                ['Hydraulique', resultsData.prodHydraulique], 
                ['Gaz', resultsData.prodGaz],
                ['Nucléaire', resultsData.prodNucleaire,],
                ['PV', resultsData.prodPV],
                ['Phs', resultsData.prodPhs],
                // CSS-style declaration
            ]);

            let options = {
                title: 'Production', 
                legend : 'none'
            };

            let chart = new google.visualization.ColumnChart(document.getElementById("Bar_div"));
            chart.draw(result2, options);
        }
        function EmCO2() {
            let co2Array = [];
            for (let i = 0; i < 5; i++) {
                co2Array.push((resultsData.co2[i]===undefined) ? 0 : resultsData.co2[i]);
            }

            let result3 = google.visualization.arrayToDataTable([
                ['Année', 'Emissions CO2', { role: "style" }],
                ['2030',  co2Array[0], 'color : green'],
                ['2035',  co2Array[1], 'color : green'],
                ['2040',  co2Array[2], 'color : green'],
                ['2045',  co2Array[3], 'color : green'],
                ['2050', co2Array[4], 'color : green']
            ]);

            let options = {
                title: 'Emissions de CO2',
                hAxis: {title: 'Année',  titleTextStyle: {color: 'black'}},
                vAxis: {minValue: 0},
                legend: 'none'
            };

            let chart = new google.visualization.AreaChart(document.getElementById('line_div'));
            chart.draw(result3, options);


        }
        function PenSurBar1() {
            let result4 = new google.visualization.arrayToDataTable([
                ['Heures', 'nombre de pénuries', 'nombre de surplus'],
                [{v: [0, 0, 0], f: '0 am'}, resultsData.penuriesHoraire[0], resultsData.surplusHoraire[0]],
                [{v: [1, 0, 0], f: '1 am'}, resultsData.penuriesHoraire[1], resultsData.surplusHoraire[1]],
                [{v: [2, 0, 0], f: '2 am'}, resultsData.penuriesHoraire[2], resultsData.surplusHoraire[2]],
                [{v: [3, 0, 0], f: '3 am'}, resultsData.penuriesHoraire[3], resultsData.surplusHoraire[3]],
                [{v: [4, 0, 0], f: '4 am'}, resultsData.penuriesHoraire[4], resultsData.surplusHoraire[4]],
                [{v: [5, 0, 0], f: '5 am'}, resultsData.penuriesHoraire[5], resultsData.surplusHoraire[5]],
                [{v: [6, 0, 0], f: '6 am'}, resultsData.penuriesHoraire[6], resultsData.surplusHoraire[6]],
                [{v: [7, 0, 0], f: '7 am'}, resultsData.penuriesHoraire[7], resultsData.surplusHoraire[7]],
                [{v: [8, 0, 0], f: '8 am'}, resultsData.penuriesHoraire[8], resultsData.surplusHoraire[8]],
                [{v: [9, 0, 0], f: '9 am'}, resultsData.penuriesHoraire[9], resultsData.surplusHoraire[9]],
                [{v: [10, 0, 0], f: '10 am'}, resultsData.penuriesHoraire[10], resultsData.surplusHoraire[10]],
                [{v: [11, 0, 0], f: '11 am'}, resultsData.penuriesHoraire[11], resultsData.surplusHoraire[11]], 
                [{v: [12, 0, 0], f: '12 am'}, resultsData.penuriesHoraire[12], resultsData.surplusHoraire[12]],
                [{v: [13, 0, 0], f: '1 pm'}, resultsData.penuriesHoraire[13], resultsData.surplusHoraire[13]],
                [{v: [14, 0, 0], f: '2 pm'}, resultsData.penuriesHoraire[14], resultsData.surplusHoraire[14]],
                [{v: [15, 0, 0], f: '3 pm'}, resultsData.penuriesHoraire[15], resultsData.surplusHoraire[15]],
                [{v: [16, 0, 0], f: '4 pm'}, resultsData.penuriesHoraire[16], resultsData.surplusHoraire[16]],
                [{v: [17, 0, 0], f: '5 pm'}, resultsData.penuriesHoraire[17], resultsData.surplusHoraire[17]],
                [{v: [18, 0, 0], f: '6 pm'}, resultsData.penuriesHoraire[18], resultsData.surplusHoraire[18]],
                [{v: [19, 0, 0], f: '7 pm'}, resultsData.penuriesHoraire[19], resultsData.surplusHoraire[19]],
                [{v: [20, 0, 0], f: '8 pm'}, resultsData.penuriesHoraire[20], resultsData.surplusHoraire[20]],
                [{v: [21, 0, 0], f: '9 pm'}, resultsData.penuriesHoraire[21], resultsData.surplusHoraire[21]],
                [{v: [22, 0, 0], f: '10 pm'}, resultsData.penuriesHoraire[22], resultsData.surplusHoraire[22]],
                [{v: [23, 0, 0], f: '11 pm'}, resultsData.penuriesHoraire[23], resultsData.surplusHoraire[23]]
            ]);

            let options = {
                title: 'Pénuries et Surplus au fil des heures',
                colors: ['#9575cd', '#33ac71'],
                hAxis: {
                    title: 'Heures',
                    format: 'h:mm a',
                    viewWindow: {
                    min: [0, 0, 0],
                    max: [23, 30, 0]}
                },
                vAxis: {
                    title: 'Rating (scale of 1-100)'
                } 
            };

            let chart = new google.visualization.ColumnChart(document.getElementById('chartcolumn_div'));
            chart.draw(result4, options);
            
        }
        function PenSurBar2() {           
            let result5 = new google.visualization.arrayToDataTable([]);
            result5.addColumn('number', "Jours de l'année");
            result5.addColumn('number', 'nombre de pénuries');
            result5.addColumn('number', 'nombre de surplus');

            for (let i = 0; i < 365; i++) {
                result5.addRow([i+1, resultsData.penuriesQuotidien[i], resultsData.surplusQuotidien[i]]);
            }

            let options = {
                title: 'Pénuries et Surplus au fil des jours',
                colors: ['#9575cd', '#33ac71'],
                hAxis: {
                    title: 'Jours',
                    viewWindow: {
                        min: [0, 0, 0],
                        max: [365, 100, 0]
                    }
                },
                vAxis: {
                    title: 'Rating (scale of 1-100)'
                } 
            };

            let chart = new google.visualization.ColumnChart(document.getElementById('chartcolumn2_div'));
            chart.draw(result5, options);
            
        }
        function Resultats() {
            let result6 = new google.visualization.arrayToDataTable([]);
            result6.addColumn('string', 'Bilan');
            result6.addColumn('number', '');
            result6.addRows([
                ['Dépense (en Md€)',  {v :resultsData.cout, f : resultsData.cout + ' €'}],
                ['Demande',   {v:resultsData.demande,   f: resultsData.demande + ' Gwh'}],
                ['Production', {v: resultsData.production, f: resultsData.production + ' GWh'}],
                ['Production - Demande',   {v: resultsData.production - resultsData.demande,  f: resultsData.production - resultsData.demande + ' GWh'}],
                ['Nb Pénuries', {v : resultsData.nbPenuries}], 
                ['Nb Surplus', {v : resultsData.nbSurplus}], 
                ['Stock Gaz (fin - debut)', {v : resultsData.stockGaz[8759]-resultsData.stockGaz[0]}],
                ['Biogaz généré', {v: resultsData.biogaz}]
            ]);

            let table = new google.visualization.Table(document.getElementById('table_div'));
            table.draw(result6, {showRowNumber: true, width: '100%', height: '100%'});
        }
        function Score(){
            let result7 = google.visualization.arrayToDataTable([
                ['Matières Premières', 'Score', {role : 'style' }],
                ['Uranium', resultsData.scoreUranium, 'gold'],            // RGB value
                ['Hydrocarburants/Gaz', resultsData.scoreHydro, 'silver'],            // English color name
                ['Bois', resultsData.scoreBois, '#33ac71'],
                ['Déchets', resultsData.scoreDechets, 'color : brown'],
                // CSS-style declaration
            ]);

            let options = {
                title: 'Matières Premières', 
                legend : 'none'
            };

            let chart = new google.visualization.ColumnChart(document.getElementById("Score_div"));
            chart.draw(result7, options);
        }

        

        function fillPage() {
            google.charts.load('current', {'packages':['table']});
            google.charts.load('current', {'packages': ['corechart']});
            google.charts.load('current', {'packages':['geochart']}, {mapsApiKey: 'AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY'});

            google.charts.setOnLoadCallback(PuissanceInst);
            google.charts.setOnLoadCallback(Prod);
            google.charts.setOnLoadCallback(EmCO2);
            google.charts.setOnLoadCallback(PenSurBar1);
            google.charts.setOnLoadCallback(PenSurBar2);
            google.charts.setOnLoadCallback(Resultats);
            google.charts.setOnLoadCallback(Score);

            let map = document.querySelector('#map')

            let paths = map.querySelectorAll('.map__image a')


            //POlyfill du foreach
            if (NodeList.prototype.forEach === undefined) {
                NodeList.prototype.forEach = function (callback) {
                    [].forEach.call(this, callback);
                };
            } 

            let activeArea = function (id) {
                map.querySelectorAll('.is-active').forEach(function (item){
                    item.classList.remove('is-active');
                });

                if (id !== undefined){
                    document.querySelector("#"+id).classList.add('is-active');
                }
            }

            paths.forEach(function (path){
                path.addEventListener('mouseenter', function () {
                    activeArea(this.id);
                });
            });

        
            map.addEventListener('mouseover', function() {
                activeArea();
            });


            let listeTransfert = [];
            let couleurs = ["#ffffcc", "#d9f0a3", "#addd8e", "#78c679", "#5ace7d", "#5b8615"];
            for (const k in resultsData.transfert) {
                listeTransfert.push(resultsData.transfert[k]);
            }
            let min = Math.min(...listeTransfert);
            let max = Math.max(...listeTransfert);
            let coeff = (max-min)/6;


            for (const k in resultsData.transfert) {
                let v = resultsData.transfert[k];

                for (let i = 0; i < 6; i++) {
                    if (v >= min + i*coeff && v <= min + (i+1)*coeff) {
                        $(`#${k}`).css("fill", couleurs[i]);
                    }
                }
            }
        }


        $('#commitResults').click(() => {
            $.ajax({
                url: "/commit",
                type: "GET",
                error: function(jqXHR, textStatus, errorThrown) {
                    displayError("http");
                }
            });
        });



        // DEBUT EXECUTION PAGE

        $.ajax({
            url: "/get_mix",
            type: "GET",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                mixData = data;
                $.ajax({
                    url: "/get_results",
                    type: "GET",
                    dataType: "json",
                    success: function (data, textStatus, jqXHR) {
                        resultsHistory = data;
                        resultsData = data[mixData.annee.toString()];
                        fillPage();
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        displayError("http");
                    }
                });
            },
            error: function(jqXHR, textStatus, errorThrown) {
                displayError("http");
            }
        });

        $("#results").fadeIn();
    }

});