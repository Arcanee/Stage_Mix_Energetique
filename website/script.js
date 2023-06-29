$(function() {


    if (document.title == "Jeu mix énergétique") {
        const imgData = document.createElement('img');

        $("#sous-titre").fadeIn(function() {
            $("#noPhoto").fadeIn();
        });
        
        
        function photoCheck(data) {
            window.sessionStorage.setItem("photoDetection", data);
            window.location.href = "detection.html";   
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
            $("#inputError").css('visibility', 'visible');
            $("#inputError").css('display', 'none');
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
                    photoCheck(data[1]);
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
        })
        
        $('#imgOutput').click(() => {
            if (imgData.src) {
               toBase64(imgData.src, function(data){sendImg(data);})
            } else {
                displayError("input");
            }
        })

        $('#noPhotoBtn').click(() => {
            window.location.href = "manual.html";
        })
    
    }



    if (document.title == "Entrée manuelle - Jeu mix énergétique") {
        $("#manualInput").fadeIn();


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



        $('.backHome').click(() => {
            window.location.href = "index.html";
        })

        $('#computeResults').click(() => {
            const data = saveData();
            console.log(data);
            console.log(typeof(data));
            sessionStorage.setItem("test", data);
            const x = sessionStorage.getItem("test");
            console.log(x);
            //window.location.href = "results.html";
        })
    }



    if (document.title == "Vérification - Jeu mix énergétique") {

        const data = JSON.parse(window.sessionStorage.getItem("photoDetection"));

        txtCorresp = {
            "eolienneON" : "Eoliennes on.",
            "eolienneOFF" : "Eoliennes off.",
            "barrage" : "Barrages",
            "centrale" : "Centrales",
            "panneauPV" : "Panneaux",
            "usineCharbon" : "Usines charbon",
            "usineGaz" : "Usines gaz",
            "batterie" : "Batteries",
            "stockageGaz" : "Stockages gaz"
        }

        for (const reg in data) {
            if (reg == "carte") {
                $('#carte').html(`Carte: ${data[reg]}`);
            }
        }

        for (const reg in data) {
            if (reg != "Carte") {
                colors = {
                    "eolienneON" : 0,
                    "eolienneOFF" : 0,
                    "barrage" : 0,
                    "centrale" : 0,
                    "panneauPV" : 0,
                    "usineCharbon" : 0,
                    "usineGaz" : 0,
                    "batterie" : 0,
                    "stockageGaz" : 0
                }

                for (a of data[reg]) {
                    colors[a] ++;
                }

                for (const c in colors) {
                    $(`#${reg}_${c}`).html(txtCorresp[c] + ": " + colors[c]);
                }
            }
        }
         
        $("#validation").fadeIn();


        $('#computeResults').click(() => {
            window.location.href = "results.html";
        })

        $('#retakePhoto').click(() => {
            window.location.href = "index.html";
        })

        $('#noPhotoBtn').click(() => {
            window.location.href = "manual.html";
        })
    }



    if (document.title == "Résultats - Jeu mix énergétique") {

        function displayResults(data) {
            console.log(data);
        }

        $.ajax({
            url: "http://127.0.0.1:5000/production",
            type: "GET",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                if (data[0] == "detection_success") {
                    displayResults(data[1]);
                } else {
                    console.log("error prod computation");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("network error");
            }
        });



        $("#results").fadeIn();
    }

});