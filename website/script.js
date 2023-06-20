window.onload = function() {

    const imgData = document.createElement('img');
    const imgInput = document.getElementById('imgInput');
    const button = document.getElementById('imgOutput');




    if (document.title == "Jeu mix énergétique") {

        function displayResults(data) {
            for (const k in data) {
                if (k == "Carte") {
                    const p = document.getElementById(k);
                    p.innerHTML = `Carte détectée : ${data[k]}`;
                }
            }

            for (const k in data) {
                if (k != "Carte") {
                    const p = document.getElementById(k);
                    p.innerHTML = `${k} :`;

                    const ul = document.createElement('ul');
                    for (a of data[k]) {
                        const li = document.createElement('li');
                        li.innerHTML = `${a.nombre} ${a.nom}`;
                        ul.appendChild(li);
                    }
                    p.appendChild(ul);
                }
            }
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
            const request = new XMLHttpRequest(),
            path = "http://127.0.0.1:5000/receiver";
            data = JSON.stringify({image: img});

            request.onreadystatechange = function() {
                if (request.readyState === XMLHttpRequest.DONE) {
                    if (request.status === 200) {
                      const response = JSON.parse(request.responseText);
                      console.log(response);
                      displayResults(response);
                    } else {
                      console.log('Un problème est survenu avec la requête.');
                    }
                }
            }

            request.open("POST", path, true);
            request.setRequestHeader('Content-Type', 'application/json');
            request.send(data);
        }

        



        imgInput.addEventListener('change', () =>   {
            const file = imgInput.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                imgData.src = e.target.result;
            }

            reader.readAsDataURL(file);           
        })
        
        
        button.addEventListener('click', () => {
            if (imgData.src) {
               toBase64(imgData.src, function(data){sendImg(data);})
            }
        })
    }

}