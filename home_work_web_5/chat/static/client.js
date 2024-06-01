console.log('Hello world!');

const ws = new WebSocket('ws://localhost:8081');

const formChat = document.getElementById('formChat');
const textField = document.getElementById('textField');
const subscribe = document.getElementById('subscribe');

formChat.addEventListener('submit', (e) => {
    e.preventDefault();
    ws.send(textField.value);
    textField.value = '';
});

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
