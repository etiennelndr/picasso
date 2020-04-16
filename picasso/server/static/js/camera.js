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

const constraints = {
    video: true,
};

console.log(window);
console.log('WebSocket' in window);
if('WebSocket' in window){
    connect('wss://192.168.1.42:12500/');
} else {
    alert ('web sockets not supported');
}

function connect(host) {
    ws = new WebSocket(host);
    ws.onopen = function () {
        log('connected');
    };
    ws.onclose = function () {
        log('socket closed');
    };
    ws.onerror = function (evt) {
        log('<span style="color: red;">ERROR:</span> ' + evt.data);
    };
};

const video = document.querySelector('video');

navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
    video.srcObject = stream;
});

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
}

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
}

function handleError(error) {
    console.error('Error: ', error);
}