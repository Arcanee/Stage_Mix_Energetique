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
        
        
        function photoCheck(data) {
               
        }


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

            <h2 class="container-fluid pb-5 mb-4 text-center">Vérifiez les informations, corrigez si nécessaire</h2>

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
            if ($("#carte").val() == "default") {
                alert("Veuillez slectionner une carte");
            } else {
                const map = $("#carte").val();
                const pions_hdf = {
                    eolienneON : $("#hdf_eolienneON").val(),
                    eolienneOFF : $("#hdf_eolienneOFF").val(),
                    panneauPV : $("#hdf_panneauPV").val(),
                    barrage : $("#hdf_barrage").val(),
                    centrale : $("#hdf_centrale").val(),
                    usineCharbon : $("#hdf_usineCharbon").val(),
                    usinegaz : $("#hdf_usinegaz").val(),
                    stockageGaz : $("#hdf_stockageGaz").val(),
                    batterie : $("#hdf_batterie").val(),
                };
                const pions_bre = {
                    eolienneON : $("#bre_eolienneON").val(),
                    eolienneOFF : $("#bre_eolienneOFF").val(),
                    panneauPV : $("#bre_panneauPV").val(),
                    barrage : $("#bre_barrage").val(),
                    centrale : $("#bre_centrale").val(),
                    usineCharbon : $("#bre_usineCharbon").val(),
                    usinegaz : $("#bre_usinegaz").val(),
                    stockageGaz : $("#bre_stockageGaz").val(),
                    batterie : $("#bre_batterie").val(),
                };
                const pions_nor = {
                    eolienneON : $("#nor_eolienneON").val(),
                    eolienneOFF : $("#nor_eolienneOFF").val(),
                    panneauPV : $("#nor_panneauPV").val(),
                    barrage : $("#nor_barrage").val(),
                    centrale : $("#nor_centrale").val(),
                    usineCharbon : $("#nor_usineCharbon").val(),
                    usinegaz : $("#nor_usinegaz").val(),
                    stockageGaz : $("#nor_stockageGaz").val(),
                    batterie : $("#nor_batterie").val(),
                };
                const pions_idf = {
                    eolienneON : $("#idf_eolienneON").val(),
                    eolienneOFF : $("#idf_eolienneOFF").val(),
                    panneauPV : $("#idf_panneauPV").val(),
                    barrage : $("#idf_barrage").val(),
                    centrale : $("#idf_centrale").val(),
                    usineCharbon : $("#idf_usineCharbon").val(),
                    usinegaz : $("#idf_usinegaz").val(),
                    stockageGaz : $("#idf_stockageGaz").val(),
                    batterie : $("#idf_batterie").val(),
                };
                const pions_est = {
                    eolienneON : $("#est_eolienneON").val(),
                    eolienneOFF : $("#est_eolienneOFF").val(),
                    panneauPV : $("#est_panneauPV").val(),
                    barrage : $("#est_barrage").val(),
                    centrale : $("#est_centrale").val(),
                    usineCharbon : $("#est_usineCharbon").val(),
                    usinegaz : $("#est_usinegaz").val(),
                    stockageGaz : $("#est_stockageGaz").val(),
                    batterie : $("#est_batterie").val(),
                };
                const pions_cvl = {
                    eolienneON : $("#cvl_eolienneON").val(),
                    eolienneOFF : $("#cvl_eolienneOFF").val(),
                    panneauPV : $("#cvl_panneauPV").val(),
                    barrage : $("#cvl_barrage").val(),
                    centrale : $("#cvl_centrale").val(),
                    usineCharbon : $("#cvl_usineCharbon").val(),
                    usinegaz : $("#cvl_usinegaz").val(),
                    stockageGaz : $("#cvl_stockageGaz").val(),
                    batterie : $("#cvl_batterie").val(),
                };
                const pions_pll = {
                    eolienneON : $("#pll_eolienneON").val(),
                    eolienneOFF : $("#pll_eolienneOFF").val(),
                    panneauPV : $("#pll_panneauPV").val(),
                    barrage : $("#pll_barrage").val(),
                    centrale : $("#pll_centrale").val(),
                    usineCharbon : $("#pll_usineCharbon").val(),
                    usinegaz : $("#pll_usinegaz").val(),
                    stockageGaz : $("#pll_stockageGaz").val(),
                    batterie : $("#pll_batterie").val(),
                };
                const pions_bfc = {
                    eolienneON : $("#bfc_eolienneON").val(),
                    eolienneOFF : $("#bfc_eolienneOFF").val(),
                    panneauPV : $("#bfc_panneauPV").val(),
                    barrage : $("#bfc_barrage").val(),
                    centrale : $("#bfc_centrale").val(),
                    usineCharbon : $("#bfc_usineCharbon").val(),
                    usinegaz : $("#bfc_usinegaz").val(),
                    stockageGaz : $("#bfc_stockageGaz").val(),
                    batterie : $("#bfc_batterie").val(),
                };
                const pions_naq = {
                    eolienneON : $("#naq_eolienneON").val(),
                    eolienneOFF : $("#naq_eolienneOFF").val(),
                    panneauPV : $("#naq_panneauPV").val(),
                    barrage : $("#naq_barrage").val(),
                    centrale : $("#naq_centrale").val(),
                    usineCharbon : $("#naq_usineCharbon").val(),
                    usinegaz : $("#naq_usinegaz").val(),
                    stockageGaz : $("#naq_stockageGaz").val(),
                    batterie : $("#naq_batterie").val(),
                };
                const pions_ara = {
                    eolienneON : $("#ara_eolienneON").val(),
                    eolienneOFF : $("#ara_eolienneOFF").val(),
                    panneauPV : $("#ara_panneauPV").val(),
                    barrage : $("#ara_barrage").val(),
                    centrale : $("#ara_centrale").val(),
                    usineCharbon : $("#ara_usineCharbon").val(),
                    usinegaz : $("#ara_usinegaz").val(),
                    stockageGaz : $("#ara_stockageGaz").val(),
                    batterie : $("#ara_batterie").val(),
                };
                const pions_occ = {
                    eolienneON : $("#occ_eolienneON").val(),
                    eolienneOFF : $("#occ_eolienneOFF").val(),
                    panneauPV : $("#occ_panneauPV").val(),
                    barrage : $("#occ_barrage").val(),
                    centrale : $("#occ_centrale").val(),
                    usineCharbon : $("#occ_usineCharbon").val(),
                    usinegaz : $("#occ_usinegaz").val(),
                    stockageGaz : $("#occ_stockageGaz").val(),
                    batterie : $("#occ_batterie").val(),
                };
                const pions_pac = {
                    eolienneON : $("#pac_eolienneON").val(),
                    eolienneOFF : $("#pac_eolienneOFF").val(),
                    panneauPV : $("#pac_panneauPV").val(),
                    barrage : $("#pac_barrage").val(),
                    centrale : $("#pac_centrale").val(),
                    usineCharbon : $("#pac_usineCharbon").val(),
                    usinegaz : $("#pac_usinegaz").val(),
                    stockageGaz : $("#pac_stockageGaz").val(),
                    batterie : $("#pac_batterie").val(),
                };
                const pions_cor = {
                    eolienneON : $("#cor_eolienneON").val(),
                    eolienneOFF : $("#cor_eolienneOFF").val(),
                    panneauPV : $("#cor_panneauPV").val(),
                    barrage : $("#cor_barrage").val(),
                    centrale : $("#cor_centrale").val(),
                    usineCharbon : $("#cor_usineCharbon").val(),
                    usinegaz : $("#cor_usinegaz").val(),
                    stockageGaz : $("#cor_stockageGaz").val(),
                    batterie : $("#cor_batterie").val(),
                };

                const result = {
                    carte : map,
                    hdf : pions_hdf,
                    bre : pions_bre,
                    nor : pions_nor,
                    idf : pions_idf,
                    est : pions_est,
                    cvl : pions_cvl,
                    pll : pions_pll,
                    bfc : pions_bfc,
                    naq : pions_naq,
                    ara : pions_ara,
                    occ : pions_occ,
                    pac : pions_pac,
                    cor : pions_cor
                };


                return JSON.stringify(result);
            }
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
    
                if ($("#carte").val() != "default") {
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
        initContent(`${data["carte"]}`);

        // Remplissage de la page avec les valeurs récupérées
        $('#carte').val(`${data["carte"]}`);
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
            if ($("#carte").val() == "default") {
                alert("Veuillez slectionner une carte");
            } else {
                const map = $("#carte").val();
                const pions_hdf = {
                    eolienneON : $("#hdf_eolienneON").val(),
                    eolienneOFF : $("#hdf_eolienneOFF").val(),
                    panneauPV : $("#hdf_panneauPV").val(),
                    barrage : $("#hdf_barrage").val(),
                    centrale : $("#hdf_centrale").val(),
                    usineCharbon : $("#hdf_usineCharbon").val(),
                    usinegaz : $("#hdf_usinegaz").val(),
                    stockageGaz : $("#hdf_stockageGaz").val(),
                    batterie : $("#hdf_batterie").val(),
                };
                const pions_bre = {
                    eolienneON : $("#bre_eolienneON").val(),
                    eolienneOFF : $("#bre_eolienneOFF").val(),
                    panneauPV : $("#bre_panneauPV").val(),
                    barrage : $("#bre_barrage").val(),
                    centrale : $("#bre_centrale").val(),
                    usineCharbon : $("#bre_usineCharbon").val(),
                    usinegaz : $("#bre_usinegaz").val(),
                    stockageGaz : $("#bre_stockageGaz").val(),
                    batterie : $("#bre_batterie").val(),
                };
                const pions_nor = {
                    eolienneON : $("#nor_eolienneON").val(),
                    eolienneOFF : $("#nor_eolienneOFF").val(),
                    panneauPV : $("#nor_panneauPV").val(),
                    barrage : $("#nor_barrage").val(),
                    centrale : $("#nor_centrale").val(),
                    usineCharbon : $("#nor_usineCharbon").val(),
                    usinegaz : $("#nor_usinegaz").val(),
                    stockageGaz : $("#nor_stockageGaz").val(),
                    batterie : $("#nor_batterie").val(),
                };
                const pions_idf = {
                    eolienneON : $("#idf_eolienneON").val(),
                    eolienneOFF : $("#idf_eolienneOFF").val(),
                    panneauPV : $("#idf_panneauPV").val(),
                    barrage : $("#idf_barrage").val(),
                    centrale : $("#idf_centrale").val(),
                    usineCharbon : $("#idf_usineCharbon").val(),
                    usinegaz : $("#idf_usinegaz").val(),
                    stockageGaz : $("#idf_stockageGaz").val(),
                    batterie : $("#idf_batterie").val(),
                };
                const pions_est = {
                    eolienneON : $("#est_eolienneON").val(),
                    eolienneOFF : $("#est_eolienneOFF").val(),
                    panneauPV : $("#est_panneauPV").val(),
                    barrage : $("#est_barrage").val(),
                    centrale : $("#est_centrale").val(),
                    usineCharbon : $("#est_usineCharbon").val(),
                    usinegaz : $("#est_usinegaz").val(),
                    stockageGaz : $("#est_stockageGaz").val(),
                    batterie : $("#est_batterie").val(),
                };
                const pions_cvl = {
                    eolienneON : $("#cvl_eolienneON").val(),
                    eolienneOFF : $("#cvl_eolienneOFF").val(),
                    panneauPV : $("#cvl_panneauPV").val(),
                    barrage : $("#cvl_barrage").val(),
                    centrale : $("#cvl_centrale").val(),
                    usineCharbon : $("#cvl_usineCharbon").val(),
                    usinegaz : $("#cvl_usinegaz").val(),
                    stockageGaz : $("#cvl_stockageGaz").val(),
                    batterie : $("#cvl_batterie").val(),
                };
                const pions_pll = {
                    eolienneON : $("#pll_eolienneON").val(),
                    eolienneOFF : $("#pll_eolienneOFF").val(),
                    panneauPV : $("#pll_panneauPV").val(),
                    barrage : $("#pll_barrage").val(),
                    centrale : $("#pll_centrale").val(),
                    usineCharbon : $("#pll_usineCharbon").val(),
                    usinegaz : $("#pll_usinegaz").val(),
                    stockageGaz : $("#pll_stockageGaz").val(),
                    batterie : $("#pll_batterie").val(),
                };
                const pions_bfc = {
                    eolienneON : $("#bfc_eolienneON").val(),
                    eolienneOFF : $("#bfc_eolienneOFF").val(),
                    panneauPV : $("#bfc_panneauPV").val(),
                    barrage : $("#bfc_barrage").val(),
                    centrale : $("#bfc_centrale").val(),
                    usineCharbon : $("#bfc_usineCharbon").val(),
                    usinegaz : $("#bfc_usinegaz").val(),
                    stockageGaz : $("#bfc_stockageGaz").val(),
                    batterie : $("#bfc_batterie").val(),
                };
                const pions_naq = {
                    eolienneON : $("#naq_eolienneON").val(),
                    eolienneOFF : $("#naq_eolienneOFF").val(),
                    panneauPV : $("#naq_panneauPV").val(),
                    barrage : $("#naq_barrage").val(),
                    centrale : $("#naq_centrale").val(),
                    usineCharbon : $("#naq_usineCharbon").val(),
                    usinegaz : $("#naq_usinegaz").val(),
                    stockageGaz : $("#naq_stockageGaz").val(),
                    batterie : $("#naq_batterie").val(),
                };
                const pions_ara = {
                    eolienneON : $("#ara_eolienneON").val(),
                    eolienneOFF : $("#ara_eolienneOFF").val(),
                    panneauPV : $("#ara_panneauPV").val(),
                    barrage : $("#ara_barrage").val(),
                    centrale : $("#ara_centrale").val(),
                    usineCharbon : $("#ara_usineCharbon").val(),
                    usinegaz : $("#ara_usinegaz").val(),
                    stockageGaz : $("#ara_stockageGaz").val(),
                    batterie : $("#ara_batterie").val(),
                };
                const pions_occ = {
                    eolienneON : $("#occ_eolienneON").val(),
                    eolienneOFF : $("#occ_eolienneOFF").val(),
                    panneauPV : $("#occ_panneauPV").val(),
                    barrage : $("#occ_barrage").val(),
                    centrale : $("#occ_centrale").val(),
                    usineCharbon : $("#occ_usineCharbon").val(),
                    usinegaz : $("#occ_usinegaz").val(),
                    stockageGaz : $("#occ_stockageGaz").val(),
                    batterie : $("#occ_batterie").val(),
                };
                const pions_pac = {
                    eolienneON : $("#pac_eolienneON").val(),
                    eolienneOFF : $("#pac_eolienneOFF").val(),
                    panneauPV : $("#pac_panneauPV").val(),
                    barrage : $("#pac_barrage").val(),
                    centrale : $("#pac_centrale").val(),
                    usineCharbon : $("#pac_usineCharbon").val(),
                    usinegaz : $("#pac_usinegaz").val(),
                    stockageGaz : $("#pac_stockageGaz").val(),
                    batterie : $("#pac_batterie").val(),
                };
                const pions_cor = {
                    eolienneON : $("#cor_eolienneON").val(),
                    eolienneOFF : $("#cor_eolienneOFF").val(),
                    panneauPV : $("#cor_panneauPV").val(),
                    barrage : $("#cor_barrage").val(),
                    centrale : $("#cor_centrale").val(),
                    usineCharbon : $("#cor_usineCharbon").val(),
                    usinegaz : $("#cor_usinegaz").val(),
                    stockageGaz : $("#cor_stockageGaz").val(),
                    batterie : $("#cor_batterie").val(),
                };

                const result = {
                    carte : map,
                    hdf : pions_hdf,
                    bre : pions_bre,
                    nor : pions_nor,
                    idf : pions_idf,
                    est : pions_est,
                    cvl : pions_cvl,
                    pll : pions_pll,
                    bfc : pions_bfc,
                    naq : pions_naq,
                    ara : pions_ara,
                    occ : pions_occ,
                    pac : pions_pac,
                    cor : pions_cor
                };

                return JSON.stringify(result);
            }
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
    
                if ($("#carte").val() != "default") {
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

        txtCorresp = {
            "eolienneON" : "Eol. onshore",
            "eolienneOFF" : "Eol. offshore",
            "barrage" : "Barrages",
            "centrale" : "Centrales",
            "panneauPV" : "Panneaux",
            "usineCharbon" : "Usines charbon",
            "usineGaz" : "Usines gaz",
            "batterie" : "Batteries",
            "stockageGaz" : "Stockages gaz"
        }

        for (const reg in dataProd) {
            if (reg == "carte") {
                $('#carte').html(`Carte: ${dataProd[reg]}`);
            }
        }

        for (const reg in dataProd) {
            if (reg != "carte") {
                for (const p in dataProd[reg]) {
                    $(`#${reg}_${p}`).html(txtCorresp[p] + ": " + dataProd[reg][p]);
                }
            }
        }



        $("#results").fadeIn();

        $(".backHome").click(() => { 
            location.href = "index.html";
        });
    }

});