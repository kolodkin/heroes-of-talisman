const ReconnectWebSocket = ({url, onopen, onclose, onmessage, onerror, interval, maxRetries, onMaxRetries}) => {
    let ws;
    let reconnectTimeout = null;
    let closing = false;

    const connect = (retries = 0) => {
        if (retries == maxRetries){
            onMaxRetries();
            return;
        }
        ws = new WebSocket(url);

        ws.onopen = () => {
            onopen();
        };
    
        ws.onmessage = (event) => {
            onmessage(event);
        };
    
        ws.onerror = (event) => {
            onerror(event);
        };
        
        ws.onclose = (event) => {
            onclose(closing, event);
    
            if (closing){
                return;
            }

            // reconnect attempt
            reconnectTimeout = setTimeout(() => connect(retries+1), interval);
        };
    };

    const send = (data) => {
        if (ws?.readyState === WebSocket.OPEN){            
            ws.send(data);
        }
        else {
            // should never get here, should be handled on upper lair identifiying onopen and onclose
            console.error(`WebSocket is not open, cannot send data - ${data}`);
        }        
    }

    const close = () => {
        closing = true;
        clearTimeout(reconnectTimeout);
        ws.close();
    }

    // initial connect attempt
    connect();

    return {
        send,
        close,
    };
}

export default ReconnectWebSocket