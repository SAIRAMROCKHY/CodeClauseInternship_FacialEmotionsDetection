// CSS Script

const blob = document.getElementById("blob");

window.onpointermove = event => {
    const { clientX, clientY } = event;

    blob.animate({
        left: `${clientX}px`,
        top: `${clientY}px`
    }, { duration: 3000, fill: "forwards" });
}


// Webcam Script

const video = document.getElementById('webcam');
const canvas = document.getElementById('snapshot-canvas');
const finalCapturedImage = document.getElementById('image-id');
const snapshotButton = document.getElementById('snapshot');
const snapshotAgainButton = document.getElementById('snapshot-again');
const stopWebcamButton = document.getElementById('stop-webcam');
const startWebcamButton = document.getElementById('start-webcam');
const predictButton = document.getElementById('predict-btn');

startWebcamButton.style.scale = '2';
startWebcamButton.style.transform = "translate(0%, -200%)";

let stream;

function startWebcam() {
    startWebcamButton.style.scale = '1';
    startWebcamButton.style.transform = "translate(0%, 0%)";
    canvas.style.zIndex = "-1";
    video.style.zIndex = "10";
    if(finalCapturedImage){
        finalCapturedImage.style.zIndex = "-1";
    }
    navigator.mediaDevices
        .getUserMedia({ video: true })
        .then(s => {
            stream = s;
            video.srcObject = stream;
            snapshotButton.style.display = "block";
            stopWebcamButton.style.display = "block";
            snapshotAgainButton.style.display = "none";
            startWebcamButton.style.display = "none";
        })
        .catch(error => {
            console.error(error);
        });
}

function stopWebcam() {
    stream.getVideoTracks()[0].stop();
    snapshotButton.style.display = "none";
    stopWebcamButton.style.display = "none";
    startWebcamButton.style.display = "block";
}

startWebcamButton.addEventListener('click', startWebcam);
snapshotAgainButton.addEventListener('click', startWebcam);
stopWebcamButton.addEventListener('click', stopWebcam);

snapshotButton.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL();
    $.ajax({
        type: 'POST',
        url: '/save-snapshot',
        data: {
            snapshot: dataURL
        },
        success: function (response) {
            // const image = new Image();
            // image.src = '/' + response;
            // capturedImage.src = response
            canvas.style.zIndex = "10";
            video.style.zIndex = "-1";
            if(finalCapturedImage){
                finalCapturedImage.style.zIndex = "-1";
            }
            snapshotButton.style.display = "none";
            snapshotAgainButton.style.display = "block";
            predictButton.style.display = "block";
            stream.getVideoTracks()[0].stop();
        }
    });
});

