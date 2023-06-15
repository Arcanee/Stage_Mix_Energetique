window.onload = function() {

    const qrImg = document.createElement('img');

    const img = document.getElementById('imgInput');
    img.addEventListener('change', () =>    {
                                                const file = img.files[0];
                                                const reader = new FileReader();
                                                reader.onload = function(e) {
                                                    qrImg.src = e.target.result;
                                                    qrImg.id = 'boardImg';
                                                }
                                                reader.readAsDataURL(file);           
                                            })
    
    const button = document.getElementById('imgOutput');
    button.addEventListener('click', () => {
        if (qrImg.src) {
            document.body.appendChild(qrImg);
            
            //DO SOMETHING WITH IMAGE
        }
    })

    function openCvReady() {
        cv['onRuntimeInitialized']=()=>{
            const test = new cv.QRCodeDetector();
        };
      }

    openCvReady();

}