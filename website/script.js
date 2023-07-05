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
                    ["barrage", "Barrages"],
                    ["centrale", "Centrales nuc."],
                    ["usineCharbon", "Usines charbon"],
                    ["usineGaz", "Usines Gaz"],
                    ["stockageGaz", "Stockages gaz"],
                    ["batterie", "Batteries"]
    ];



    if (document.title == "Jeu mix énergétique") {
        const imgData = document.createElement('img');

        $("#sous-titre").fadeIn(function() {
            $("#noPhoto").fadeIn();
        });
        

        function displayError(reason) {
            let msg;
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
            $("#inputError").hide();
            $("#inputError").fadeIn();
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
            url: "http://127.0.0.1:5000/detector",
            type: "POST",
            data: JSON.stringify({image: img}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                if (data[0] == "detection_success") {
                    sessionStorage.setItem("photoDetection", JSON.stringify(data[1]));
                    location.href = "detection.html";
                } else {
                    displayError("img");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
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
            if (imgData.src) {
               toBase64(imgData.src, function(data){sendImg(data);})
            } else {
                displayError("input");
            }
        });

        $('#noPhotoBtn').click(() => {
            location.href = "manual.html";
        });
    
    }



    if (document.title == "Vérification - Jeu mix énergétique") {

        function initContent(map) {
            let divStr =
            `<div class="container text-center mb-5">
                <button class="btn btn-outline-secondary backHome" type="button">Retour à l'accueil</button>
            </div>

            <h2 class="container-fluid pb-5 mb-4 text-center">Vérifiez les informations, et corrigez si nécessaire</h2>

            <div class="row justify-content-evenly bg-success bg-opacity-50 rounded pb-2">
                <div class="col-2 mt-2 h2">Carte</div>
                <div class="form-outline col-5 mt-2">
                    <form>
                        <select name="carte" id="carte" class="form-select form-select-lg">
                            <option value="default" selected>Choisir une carte...</option>
                            <option value="France">France</option>
                        </select>
                    </form>
                </div>
            </div>`;

            for (const reg of maps[map]) {
                divStr += `<h3 class="row mt-5 ps-2 bg-info rounded bg-opacity-50 justify-content-center" id=${reg[0]}>${reg[1]}</h3>`;
                for (const pion of pions) {
                    divStr +=
                    `<div class="row justify-content-between">
                        <div class="col-5 mt-2">${pion[1]}</div>
                        <div class="form-outline col-5 mt-2">
                            <input value="0" min="0" max="10" type="number" id=${reg[0]}_${pion[0]} class="form-control"/>
                        </div>
                    </div>`;
                }
            }

            divStr +=
            `<div class="mb-5" style="visibility: hidden;">SPACING</div>

            <div class="text-center pt-5 my-5">  
                <div class="row justify-content-evenly">
                    <button class="btn btn-success col-4" type="button" id="computeResults">Valider</button>
                    <button class="btn btn-danger col-4 backHome" type="button">Reprendre une photo</button>
                </div>
            </div>

            <div id="inputError" class="container my-5 p-5 bg-danger text-white rounded" style="display: none;">
                <h1>Oups...</h1>
                <p  id="errorMsg"></p>
            </div>`;

            $("#validation").html(divStr);
        }

        function displayError(reason) {
            let msg;
            switch (reason) {
                case "value":
                    msg = "Vous avez entré une ou plusieurs valeurs incorrectes. Veuillez vérifier avant de valider une nouvelle fois.";
                    break;
                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;
                default:
                    break;
            }

            $("#errorMsg").html(msg);
            $("#inputError").hide()
            $("#inputError").fadeIn();
        }

        function saveData() {
            let err = 0;
            let result;
            const data = {};

            if ($("#carte").val() == "default") {
                alert("Veuillez slectionner une carte");
                err = 1;
            } else {
                const map = $("#carte").val();
                data["carte"] = map;

                for (const reg of maps[map]) {
                    data[reg[0]] = {};
                    for (const p of pions) {
                        const str = $(`#${reg[0]}_${p[0]}`).val();
                        const nb = parseFloat(str);
                        if (str == "" || nb < 0 || nb > 10 || !(Number.isInteger(nb))) {
                            alert("Veuillez entrer des nombres entiers entre 0 et 10 seulement.");
                            err = 1;
                        }
                        data[reg[0]][p[0]] = str;
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
                    initCallbacks();
                    $("#carte").val(val);
                }
            });
    
            $('#computeResults').click(() => {
                const dataProd = saveData();
    
                if (dataProd != false) {
                    $.ajax({
                        url: "http://127.0.0.1:5000/production",
                        type: "POST",
                        data: dataProd,
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data, textStatus, jqXHR) {
                            if (data[0] == "production_success") {
                                sessionStorage.setItem("prodInput", JSON.stringify(data[1]));
                                location.href = "results.html";
                            } else {
                                displayError("value");
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            displayError("http");
                        }
                    });
                }
            });
    
            $(".backHome").click(() => {
                location.href = "index.html";
            });
        }

        const data = JSON.parse(sessionStorage.getItem("photoDetection"));

        // Squelette de la page pour la carte qui a été détectée
        initContent(data["carte"]);

        // Remplissage de la page avec les valeurs récupérées
        $('#carte').val(data["carte"]);
        for (const reg in data) {
            if (reg != "carte") {
                for (const p in data[reg]) {
                    $(`#${reg}_${p}`).val(data[reg][p]);
                }
            }
        }
         
        // Init évènements
        initCallbacks();

        $("#validation").fadeIn();       
    }



    if (document.title == "Entrée manuelle - Jeu mix énergétique") {

        $("#carte").val("default");

        function initContent(map) {
            let divStr =
            `<div class="container text-center mb-5">
                <button class="btn btn-outline-secondary backHome" type="button">Retour à l'accueil</button>
            </div>

            <h2 class="container-fluid pb-5 mb-4 text-center">Entrez les informations de votre plateau</h2>

            <div class="row justify-content-evenly bg-success bg-opacity-50 rounded pb-2">
                <div class="col-2 mt-2 h2">Carte</div>
                <div class="form-outline col-5 mt-2">
                    <form>
                        <select name="carte" id="carte" class="form-select form-select-lg">
                            <option value="default" selected>Choisir une carte...</option>
                            <option value="France">France</option>
                        </select>
                    </form>
                </div>
            </div>`;

            for (const reg of maps[map]) {
                divStr += `<h3 class="row mt-5 ps-2 bg-info rounded bg-opacity-50 justify-content-center" id=${reg[0]}>${reg[1]}</h3>`;
                for (const pion of pions) {
                    divStr +=
                    `<div class="row justify-content-between">
                        <div class="col-5 mt-2">${pion[1]}</div>
                        <div class="form-outline col-5 mt-2">
                            <input value="0" min="0" max="10" type="number" id=${reg[0]}_${pion[0]} class="form-control"/>
                        </div>
                    </div>`;
                }
            }

            divStr +=
            `<div class="mb-5" style="visibility: hidden;">SPACING</div>

            <div class="text-center pt-5 my-5">  
                <div class="row justify-content-evenly">
                    <button class="btn btn-success col-4" type="button" id="computeResults">Valider</button>
                    <button class="btn btn-danger col-4 backHome" type="button" id="retakePhoto">Reprendre une photo</button>
                </div>
            </div>

            <div id="inputError" class="container my-5 p-5 bg-danger text-white rounded" style="display: none;">
                <h1>Oups...</h1>
                <p  id="errorMsg"></p>
            </div>`;

            $("#manualInput").html(divStr);
        }

        function displayError(reason) {
            let msg;
            switch (reason) {
                case "value":
                    msg = "Vous avez entré une ou plusieurs valeurs incorrectes. Veuillez vérifier avant de valider une nouvelle fois.";
                    break;
                case "http":
                    msg = "Une erreur est survenue avec le serveur.";
                    break;
                default:
                    break;
            }

            $("#errorMsg").html(msg);
            $("#inputError").hide()
            $("#inputError").fadeIn();
        }

        function saveData() {
            let err = 0;
            let result;
            const data = {};

            if ($("#carte").val() == "default") {
                alert("Veuillez slectionner une carte");
                err = 1;
            } else {
                const map = $("#carte").val();
                data["carte"] = map;

                for (const reg of maps[map]) {
                    data[reg[0]] = {};
                    for (const p of pions) {
                        const str = $(`#${reg[0]}_${p[0]}`).val();
                        const nb = parseFloat(str);
                        if (str == "" || nb < 0 || nb > 10 || !(Number.isInteger(nb))) {
                            alert("Veuillez entrer des nombres entiers entre 0 et 10 seulement.");
                            err = 1;
                        }
                        data[reg[0]][p[0]] = str;
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
                    initCallbacks();
                    $("#carte").val(val);
                }
            });
    
            $('.backHome').click(() => {
                location.href = "index.html";
            });
    
            $('#computeResults').click(() => {
                const dataProd = saveData();
    
                if (dataProd != false) {
                    $.ajax({
                        url: "http://127.0.0.1:5000/production",
                        type: "POST",
                        data: dataProd,
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data, textStatus, jqXHR) {
                            if (data[0] == "production_success") {
                                sessionStorage.setItem("prodInput", JSON.stringify(data[1]));
                                location.href = "results.html";
                            } else {
                                displayError("value");
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            displayError("http");
                        }
                    });
                }
            });
        }

        $("#manualInput").fadeIn();
        initCallbacks();

        const carte = $("#carte").val();
        if (carte != "default") {
            initContent(carte);
            initCallbacks();    
            $("#carte").val(carte);
        }

        

    }



    if (document.title == "Résultats - Jeu mix énergétique") {
        
        const dataProd = JSON.parse(sessionStorage.getItem("prodInput"));

        function initContent(map) {
            let divStr =
            `<h2 class="container-fluid pb-3 text-center">Résultats de production annuelle en GWh</h2>`;

            for (const reg of maps[map]) {
                divStr += `<h3 class="row mt-5 ps-2 bg-info rounded bg-opacity-50 justify-content-center" id=${reg[0]}>${reg[1]}</h3>`;
                for (let i = 0; i < pions.length-1; i += 2) {
                    divStr +=
                    `<div class="row justify-content-between">
                        <div class="col-5 mt-2" id="${reg[0]}_${pions[i][0]}">${pions[i][1]}: ${dataProd[reg[0]][pions[i][0]]}</div>
                        <div class="col-5 mt-2" id="${reg[0]}_${pions[i+1][0]}">${pions[i+1][1]}: ${dataProd[reg[0]][pions[i+1][0]]}</div>
                    </div>`;
                }
                divStr +=
                    `<div class="row justify-content-between">
                        <div class="col-5 mt-2" id="${reg[0]}_${pions[pions.length-1][0]}">
                            ${pions[pions.length-1][1]}: ${dataProd[reg[0]][pions[pions.length-1][0]]}
                        </div>
                    </div>`;
            }

            divStr +=
            `<div class="container text-center my-5">
                <button class="btn btn-outline-secondary backHome" type="button">Retour à l'accueil</button>
            </div>`;

            $("#results").html(divStr);
        }

        function initCallbacks() {
            $(".backHome").click(() => { 
                location.href = "index.html";
            });
        }

        initContent(dataProd["carte"]);
        initCallbacks();

        $("#results").fadeIn();
    }

});