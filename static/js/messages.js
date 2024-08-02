let sendMessageBtn;

document.addEventListener('DOMContentLoaded', function() {
    sendMessageBtn = document.getElementById('sendMessageBtn');
});

const socket = io();

function loadChat(avatar, fname, userId, profileId) {
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
            if (msg.sender_id == userId) {
                messageElement.classList.add('justify-content-end');
            }
            let textAlign = '';
            if (msg.sender_id == userId) {
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

        // Fill the receivers details 
        if (avatar != 'None') {
            document.getElementById('messageAvatar').setAttribute('src', avatar);
        }

        document.getElementById('messageFname').innerText = fname;

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
    const messageElement = document.createElement('div');

    let time = formatTime(data.created_at);

    messageElement.setAttribute('class', 'd-flex flex-row mb-2');
    if (data.sender_id == data.user_id) {
        messageElement.classList.add('justify-content-end');
    }
    let textAlign = '';
    if (data.sender_id == data.user_id) {
        textAlign = 'text-end';
    }
    messageElement.innerHTML = `
        <div class="card rounded px-3 py-2 d-flex flex-column" style="max-width:90%;">
            <span class="d-block">${data.message} </span>
            <small class="d-block ${textAlign}">${time}</small>
        </div>
    `;
    chatBody.appendChild(messageElement);
});