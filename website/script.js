$(function() {

    const imgData = document.createElement('img');


    if (document.title == "Jeu mix énergétique") {
        $("#sous-titre").fadeIn();
        

        function photoCheck(data) {
            let eolienneON;
            let eolienneOFF;
            let barrage;
            let centrale;
            let panneauPV;
            let usineCharbon;
            let usineGaz;
            let batterie;
            let stockageGaz;

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
                        $(`#${reg}_${c}`).html(c + ": " + colors[c]);
                    }
                }
            }
            
            $("#inputError").hide();
            $("#sous-titre").hide();
            $("#noPhoto").hide();
            $("#validation").fadeIn();
            
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

        $('#retakePhoto').click(() => {
            $("#validation").hide();
            $("#sous-titre").fadeIn();
        })
    
        $('#noPhotoBtn').click(() => {
            $('#sous-titre').hide();
            $('#noPhoto').hide();
            $('#spacing').hide();
            $('#inputError').hide();
            $('#manualInput').fadeIn();
        })
    
        $('.backHome').click(() => {
            $('#manualInput').hide();
            $('#sous-titre').fadeIn();
            $('#noPhoto').fadeIn();
            $('#spacing').fadeIn();
        })
    
    
    
    }

});