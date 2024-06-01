console.log('Hello world!');

let ws;
const formChat = document.getElementById('formChat');
const textField = document.getElementById('textField');
const subscribe = document.getElementById('subscribe');

function connect() {
    ws = new WebSocket('ws://localhost:8081');

    ws.onopen = (e) => {
        console.log('Hello WebSocket!');
    };

    ws.onmessage = (e) => {
        console.log(e.data);
        const text = e.data;

        const elMsg = document.createElement('div');
        elMsg.textContent = text;
        subscribe.appendChild(elMsg);
    };

    ws.onclose = (e) => {
        console.log('WebSocket closed: ', e);
        setTimeout(connect, 1000); // Повернути підключення через 1 секунду
    };

    ws.onerror = (e) => {
        console.error('WebSocket error: ', e);
    };
}

formChat.addEventListener('submit', (e) => {
    e.preventDefault();
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(textField.value);
        textField.value = '';
    } else {
        console.error('WebSocket is not open: readyState is ' + ws.readyState);
    }
});

connect();
