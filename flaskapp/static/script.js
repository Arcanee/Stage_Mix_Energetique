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
                    msg = "Veuillez choisir votre groupe.";
                    break;

                case "httpOutput":
                    msg = "Le serveur n'a pas su interpréter cette requête.";
                    break;

                case "httpRuntime":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;

                default:
                    break;
            }

            $("#errorMsg").html(msg);
            modal.toggle();
        }

        $(".logInBtn").click((e) => {
            console.log("youhouu");
            const data = [$("#grpInput").val(), e.target.id];

            if (data[0] != "default") {
                $.ajax({
                    url: "http://apps-gei.insa-toulouse.fr/set_group",
                    type: "POST",
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data, textStatus, jqXHR) {
                        if (data[0] == "log_in_success") {
                            location.href = "http://apps-gei.insa-toulouse.fr/photo";
                        } else {
                            displayError("httpOutput");
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        displayError("httpRuntime");
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


        function toBase64 (url, callback){
            const img = document.createElement('img');
            canvas = document.createElement('canvas');
            ctx = canvas.getContext('2d');
            data = '';
        
            img.crossOrigin = 'Anonymous';
        
            img.onload = function(){
                canvas.height = this.height;
                canvas.width = this.width;
                ctx.drawImage(this, 0, 0);
                data = canvas.toDataURL();
                callback(data)
            };

            img.src = url;
        };


        function sendImg(img) {
            $.ajax({
            url: "http://apps-gei.insa-toulouse.fr/detector",
            type: "POST",
            data: JSON.stringify({image: img}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                $('#imgOutput').html('Envoyer');
                processing = false;
                if (data[0] == "detection_success") {
                    sessionStorage.setItem("photoDetection", JSON.stringify(data[1]));
                    location.href = "http://apps-gei.insa-toulouse.fr/detection";
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
        

        $('#imgInput').change(() => {
            const file = imgInput.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                imgData.src = e.target.result;
            }

            reader.readAsDataURL(file);           
        });
        
        $('#imgOutput').click(() => {
            if (imgData.src && !processing) {
                processing = true;
                $('#imgOutput').html('<span class="spinner-border spinner-border-sm"></span>&nbsp;&nbsp;Chargement...');
                toBase64(imgData.src, function(data){sendImg(data);})
            } else if (!processing) {
                displayError("input");
            }
        });

        $('#noPhotoBtn').click(() => {
            location.href = "http://apps-gei.insa-toulouse.fr/manual";
        });
    
    }



    if (document.title == "Vérification - Jeu mix énergétique") {

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
                    msg = `La crise sociale en cours vous empêche de placer plus de réacteurs nucléaires (maximum: ${details}).`;
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
            console.log(data);

            result = err ? false : JSON.stringify(data);
            return result;
        }

        function initCallbacks() {
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
                        url: "http://apps-gei.insa-toulouse.fr/production",
                        type: "POST",
                        data: dataProd,
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data, textStatus, jqXHR) {
                            if (data[0] == "success") {
                                $('#computeResults').html('Valider');
                                sessionStorage.setItem("prodInput", JSON.stringify(data[1]));
                                location.href = "http://apps-gei.insa-toulouse.fr/results";
                            } else {
                                $('#computeResults').html('Valider');
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
                location.href = "http://apps-gei.insa-toulouse.fr/photo";
            });
        }

        const data = JSON.parse(sessionStorage.getItem("photoDetection"));
        $('#carte').val(data.carte);
        $("#stock").val(data.stock.toString());
        $("#annee").val(data.annee.toString());

        // Squelette de la page pour la carte qui a été détectée
        initContent(data.carte);

        // Remplissage de la page avec les valeurs récupérées
        for (const reg in data) {
            if (reg!="carte" && reg!="annee" && reg!="stock") {
                for (const p in data[reg]) {
                    $(`#${reg}_${p}`).val(data[reg][p]);
                }
            }
        }

        // Init évènements
        initCallbacks();

        $("#top").fadeIn();
        $("#mid").fadeIn();
        $("#bot").fadeIn();    
    }



    if (document.title == "Entrée manuelle - Jeu mix énergétique") {

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
                    msg = `La crise sociale en cours vous empêche de placer plus de réacteurs nucléaires (maximum: ${details}).`;
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

        function initCallbacks() {
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
                location.href = "http://apps-gei.insa-toulouse.fr/photo";
            });
    
            $('#computeResults').click(() => {
                const dataProd = saveData();
    
                if (dataProd != false) {
                    $('#computeResults').html('<span class="spinner-border spinner-border-sm"></span>&nbsp;&nbsp;Chargement...');
                    exitConfirm = false;
                    $.ajax({
                        url: "http://apps-gei.insa-toulouse.fr/production",
                        type: "POST",
                        data: dataProd,
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data, textStatus, jqXHR) {
                            if (data[0] == "success") {
                                $('#computeResults').html('Valider');
                                sessionStorage.setItem("prodInput", JSON.stringify(data[1]));
                                location.href = "http://apps-gei.insa-toulouse.fr/results";
                            } else {
                                $('#computeResults').html('Valider');
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
        }

        $("#carte").val("default");
        $("#annee").val("default");
        $("#stock").val("1");
        $("#alea").val("");

        initCallbacks();
        $("#top").fadeIn();
    }



    if (document.title == "Résultats - Jeu mix énergétique") {
        
        const data = JSON.parse(sessionStorage.getItem("prodInput"));
        console.log(data);


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
        // google.charts.setOnLoadCallback(Regions);

        // Puissance installée
        function PuissanceInst() {
            // Define the chart to be drawn.
            const TotalP = (data.puissanceBatterie +
                            data.puissanceEolienneOFF +
                            data.puissanceEolienneON +
                            data.puissanceGaz +
                            data.puissanceNucleaire +
                            data.puissancePV +
                            data.puissancePhs);


            let result1 = google.visualization.arrayToDataTable([['Technologie', 'Pourcentage'],
                ['EON', data.puissanceEolienneON/TotalP],
                ['EOFF', data.puissanceEolienneOFF/TotalP],
                ['Batterie', data.puissanceBatterie/TotalP],
                ['Nucléaire', data.puissanceNucleaire/TotalP],
                ['PV', data.puissancePV/TotalP],
                ['Phs', data.puissancePhs/TotalP],
                ['Gaz', data.puissanceGaz/TotalP]
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


        // Production
        function Prod(){
            let result2 = google.visualization.arrayToDataTable([
                ['Technologie', 'Production'],
                ['EON', data.prodEolienneON],            // RGB value
                ['EOFF', data.EolienneOFF],            // English color name
                ['Batterie', data.prodBatterie],
                ['Hydraulique', data.prodHydraulique], 
                ['Gaz', data.prodGaz],
                ['Nucléaire', data.prodNucleaire,],
                ['PV', data.prodPV],
                ['Phs', data.prodPhs],
                // CSS-style declaration
            ]);

            let options = {
                title: 'Production', 
                legend : 'none'
            };

            let chart = new google.visualization.ColumnChart(document.getElementById("Bar_div"));
            chart.draw(result2, options);
        }

        //Emission CO2
        function EmCO2() {
            let co2Array = [];
            for (let i = 0; i < 5; i++) {
                co2Array.push((data.co2[i]===undefined) ? 0 : data.co2[i]);
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
                [{v: [0, 0, 0], f: '0 am'}, data.penuriesHoraire[0], data.surplusHoraire[0]],
                [{v: [1, 0, 0], f: '1 am'}, data.penuriesHoraire[1], data.surplusHoraire[1]],
                [{v: [2, 0, 0], f: '2 am'}, data.penuriesHoraire[2], data.surplusHoraire[2]],
                [{v: [3, 0, 0], f: '3 am'}, data.penuriesHoraire[3], data.surplusHoraire[3]],
                [{v: [4, 0, 0], f: '4 am'}, data.penuriesHoraire[4], data.surplusHoraire[4]],
                [{v: [5, 0, 0], f: '5 am'}, data.penuriesHoraire[5], data.surplusHoraire[5]],
                [{v: [6, 0, 0], f: '6 am'}, data.penuriesHoraire[6], data.surplusHoraire[6]],
                [{v: [7, 0, 0], f: '7 am'}, data.penuriesHoraire[7], data.surplusHoraire[7]],
                [{v: [8, 0, 0], f: '8 am'}, data.penuriesHoraire[8], data.surplusHoraire[8]],
                [{v: [9, 0, 0], f: '9 am'}, data.penuriesHoraire[9], data.surplusHoraire[9]],
                [{v: [10, 0, 0], f: '10 am'}, data.penuriesHoraire[10], data.surplusHoraire[10]],
                [{v: [11, 0, 0], f: '11 am'}, data.penuriesHoraire[11], data.surplusHoraire[11]], 
                [{v: [12, 0, 0], f: '12 am'}, data.penuriesHoraire[12], data.surplusHoraire[12]],
                [{v: [13, 0, 0], f: '1 pm'}, data.penuriesHoraire[13], data.surplusHoraire[13]],
                [{v: [14, 0, 0], f: '2 pm'}, data.penuriesHoraire[14], data.surplusHoraire[14]],
                [{v: [15, 0, 0], f: '3 pm'}, data.penuriesHoraire[15], data.surplusHoraire[15]],
                [{v: [16, 0, 0], f: '4 pm'}, data.penuriesHoraire[16], data.surplusHoraire[16]],
                [{v: [17, 0, 0], f: '5 pm'}, data.penuriesHoraire[17], data.surplusHoraire[17]],
                [{v: [18, 0, 0], f: '6 pm'}, data.penuriesHoraire[18], data.surplusHoraire[18]],
                [{v: [19, 0, 0], f: '7 pm'}, data.penuriesHoraire[19], data.surplusHoraire[19]],
                [{v: [20, 0, 0], f: '8 pm'}, data.penuriesHoraire[20], data.surplusHoraire[20]],
                [{v: [21, 0, 0], f: '9 pm'}, data.penuriesHoraire[21], data.surplusHoraire[21]],
                [{v: [22, 0, 0], f: '10 pm'}, data.penuriesHoraire[22], data.surplusHoraire[22]],
                [{v: [23, 0, 0], f: '11 pm'}, data.penuriesHoraire[23], data.surplusHoraire[23]]
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
                result5.addRow([i+1, data.penuriesQuotidien[i], data.surplusQuotidien[i]]);
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
                ['Dépense (en Md€)',  {v :data.cout, f : data.cout + ' €'}],
                ['Demande',   {v:data.demande,   f: data.demande + ' Gwh'}],
                ['Production', {v: data.production, f: data.production + ' GWh'}],
                ['Production - Demande',   {v: data.production - data.demande,  f: data.production - data.demande + ' GWh'}],
                ['Nb Pénuries', {v : data.nbPenuries}], 
                ['Nb Surplus', {v : data.nbSurplus}], 
                ['Stock Gaz (fin - debut)', {v : data.stockGaz[8759]-data.stockGaz[0]}],
                ['Biogaz généré', {v: data.biogaz}]
            ]);

            let table = new google.visualization.Table(document.getElementById('table_div'));
            table.draw(result6, {showRowNumber: true, width: '100%', height: '100%'});
        }

        function Score(){
            let result7 = google.visualization.arrayToDataTable([
                ['Matières Premières', 'Score', {role : 'style' }],
                ['Uranium', data.scoreUranium, 'gold'],            // RGB value
                ['Hydrocarburants/Gaz', data.scoreHydro, 'silver'],            // English color name
                ['Bois', data.scoreBois, '#33ac71'],
                ['Déchets', data.scoreDechets, 'color : brown'],
                // CSS-style declaration
            ]);

            let options = {
                title: 'Matières Premières', 
                legend : 'none'
            };

            let chart = new google.visualization.ColumnChart(document.getElementById("Score_div"));
            chart.draw(result7, options);
        }

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
        for (const k in data.transfert) {
            listeTransfert.push(data.transfert[k]);
        }
        let min = Math.min(...listeTransfert);
        let max = Math.max(...listeTransfert);
        let coeff = (max-min)/6;


        for (const k in data.transfert) {
            let v = data.transfert[k];

            for (let i = 0; i < 6; i++) {
                if (v >= min + i*coeff && v <= min + (i+1)*coeff) {
                    $(`#${k}`).css("fill", couleurs[i]);
                }
            }
        }


        $('#commitResults').click(() => {
            location.href = "http://apps-gei.insa-toulouse.fr/commit";
        });


        $("#results").fadeIn();
    }

});