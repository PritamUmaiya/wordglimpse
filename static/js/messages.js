let sendMessageBtn;

document.addEventListener('DOMContentLoaded', function() {
    sendMessageBtn = document.getElementById('sendMessageBtn');
});

const socket = io();

function loadChat(userId, profileId) {
    fetch('/load_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: parseInt(userId), profile_id: parseInt(profileId) }),
    })
    .then(response => response.json())
    .then(data => {
        const chatBody = document.getElementById('chatBody');
        chatBody.innerHTML = '';
        data.forEach(msg => {
            const messageElement = document.createElement('p');
            messageElement.innerHTML = `<strong>${msg.sender_id}:</strong> ${msg.message}`;
            chatBody.appendChild(messageElement);
        });

        const room = userId < profileId ? `${userId}-${profileId}` : `${profileId}-${userId}`;
        socket.emit('join', { room: room });

        sendMessageBtn.setAttribute('onclick', `sendMessage(${userId}, ${profileId})`);
    });
}

function sendMessage(userId, profileId) {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (message === '') return;

    const room = userId < profileId ? `${userId}-${profileId}` : `${profileId}-${userId}`;
    socket.emit('send_message', { user_id: userId, profile_id: profileId, message: message, room: room });
    messageInput.value = '';
}

socket.on('message', function(data) {
    const chatBody = document.getElementById('chatBody');
    const messageElement = document.createElement('p');
    messageElement.innerHTML = `<strong>${data.user_id}:</strong> ${data.message}`;
    chatBody.appendChild(messageElement);
});