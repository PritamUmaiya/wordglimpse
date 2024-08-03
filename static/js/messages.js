let sendMessageBtn;
let currentUserId;

document.addEventListener('DOMContentLoaded', function() {
    sendMessageBtn = document.getElementById('sendMessageBtn');
});

const socket = io();

function loadChat(avatar, fname, userId, profileId) {
    currentUserId = parseInt(userId);

    fetch('/load_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: currentUserId, profile_id: parseInt(profileId) }),
    })
    .then(response => response.json())
    .then(data => {
        const chatBody = document.getElementById('chatBody');
        chatBody.innerHTML = '';

        // Keep track of the last date printed
        let lastDatePrinted = '';

        data.forEach(msg => {
            let time = formatTime(`${msg.created_at}`);
            let dateLabel = formatDateLabel(new Date(msg.created_at));

            if (dateLabel !== lastDatePrinted) {
                lastDatePrinted = dateLabel;
                const dateElement = document.createElement('p');
                dateElement.setAttribute('class', 'text-center text-body-secondary p-2');
                dateElement.innerHTML = `${dateLabel}`;
                chatBody.appendChild(dateElement);
            }

            const messageElement = document.createElement('div');
            messageElement.setAttribute('class', 'd-flex flex-row mb-2');
            if (msg.sender_id == currentUserId) {
                messageElement.classList.add('justify-content-end');
            }
            let textAlign = '';
            if (msg.sender_id == currentUserId) {
                textAlign = 'text-end';
            }
            messageElement.innerHTML = `
                <div class="card rounded px-3 py-2 d-flex flex-column" style="max-width:90%;">
                    <span class="d-block">${msg.message} </span>
                    <small class="d-block ${textAlign}">${time}</small>
                </div>
            `;
            chatBody.appendChild(messageElement);
        });

        // Scroll to bottom after loading chat
        scrollToBottom();

        // Fill the receivers details 
        if (avatar != 'None') {
            document.getElementById('messageAvatar').setAttribute('src', avatar);
        }

        document.getElementById('messageFname').innerText = fname;

        const room = currentUserId < profileId ? `${currentUserId}-${profileId}` : `${profileId}-${currentUserId}`;
        socket.emit('join', { room: room });

        sendMessageBtn.setAttribute('onclick', `sendMessage(${currentUserId}, ${profileId})`);
    });
}

function sendMessage(userId, profileId) {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (message === '') return;

    const room = userId < profileId ? `${userId}-${profileId}` : `${profileId}-${userId}`;
    const date = new Date();
    const time = formatTime(date);
    socket.emit('send_message', { user_id: userId, profile_id: profileId, message: message, room: room, time: time });

    messageInput.value = '';
}

socket.on('message', function(data) {
    const chatBody = document.getElementById('chatBody');
    const messageElement = document.createElement('div');

    // Check if the message is from the current user
    const isCurrentUser = data.user_id === currentUserId;

    messageElement.setAttribute('class', 'd-flex flex-row mb-2');
    
    if (isCurrentUser) {
        messageElement.classList.add('justify-content-end');
    }

    const textAlign = isCurrentUser ? 'text-end' : '';

    messageElement.innerHTML = `
        <div class="card rounded px-3 py-2 d-flex flex-column" style="max-width:90%;">
            <span class="d-block">${data.message} </span>
            <small class="d-block ${textAlign}">${data.time}</small>
        </div>
    `;
    chatBody.appendChild(messageElement);

    // Scroll to bottom after appending new message
    scrollToBottom();
});

function scrollToBottom() {
    const chatBody = document.getElementById('chatBody');
    chatBody.scrollTop = chatBody.scrollHeight;
}
