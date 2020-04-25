function hasGetUserMedia() {
    return !!(
        navigator.mediaDevices && navigator.mediaDevices.getUserMedia
    );
}
if (hasGetUserMedia()) {
    // Good to go!
} else {
    alert('getUserMedia() is not supported by your browser');
}

const videoElement = document.querySelector('video');
const videoSelect = document.querySelector('select#videoSource');

navigator.mediaDevices
    .enumerateDevices()
    .then(gotDevices)
    .then(getStream)
    .catch(handleError);

videoSelect.onchange = getStream;

function gotDevices(deviceInfos) {
    for (let i = 0; i !== deviceInfos.length; ++i) {
        const deviceInfo = deviceInfos[i];
        const option = document.createElement('option');
        option.value = deviceInfo.deviceId;
        if (deviceInfo.kind === 'videoinput') {
            option.text =
                deviceInfo.label || 'camera ' + (videoSelect.length + 1);
            videoSelect.appendChild(option);
        } else {
            console.log('Found another kind of device: ', deviceInfo);
        }
    }
};

function getStream() {
    if (window.stream) {
        window.stream.getTracks().forEach(function (track) {
            track.stop();
        });
    }

    const constraints = {
        video: {
            deviceId: { exact: videoSelect.value },
        },
    };

    navigator.mediaDevices
        .getUserMedia(constraints)
        .then(gotStream)
        .catch(handleError);
}

function gotStream(stream) {
    window.stream = stream; // make stream available to console
    videoElement.srcObject = stream;
};

function handleError(error) {
    console.error('Error: ', error);
};


if('WebSocket' in window) {
    connect('wss://192.168.1.42:12500/');
} else {
    alert('Web sockets are not supported.');
}

var back = document.createElement('canvas');
var backcontext = back.getContext('2d');

var attempts = 0;
function checkFlag() {
    if (videoElement.videoWidth == 0 || videoElement.videoHeight == 0) {
        window.setTimeout(checkFlag, 100);
    } else {
        if (attempts++ < 10) {
            console.log(attempts)
            sendFrames();
        }
    }
}
checkFlag();

function sendFrames() {
    back.width = videoElement.videoWidth
    back.height = videoElement.videoHeight

    console.log(back.width, back.height)

    segmentedFrame = document.getElementById('segmentedFrame');
    console.log(segmentedFrame)
    console.log(segmentedFrame.width)
    console.log(segmentedFrame.height)
    segmentedFrame.width = videoElement.videoWidth
    segmentedFrame.height = videoElement.videoHeight

    setInterval(function() {
        backcontext.drawImage(videoElement, 0, 0);
        var stringData=back.toDataURL('image/jpeg');
        send(stringData);
    }, 50);
}
