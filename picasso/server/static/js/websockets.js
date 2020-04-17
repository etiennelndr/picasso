function connect(host) {
    ws = new WebSocket(host);
    ws.onopen = function () {
        console.log('connected');
    };
    ws.onclose = function () {
        console.log('socket closed');
    };
    ws.onerror = function (evt) {
        console.log('<span style="color: red;">ERROR:</span> ' + evt.data);
    };
    ws.onmessage = function(evt) {
        console.log('Received data: ' + evt.data);
    }
};

function send(msg){ 
    if (ws != null) { 
        if(ws.readyState === 1) {
            ws.send(msg);
        }       
    } else {
        console.log('not ready yet');
    }
};
