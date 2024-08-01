function initializeSocketConnection(currentUserId) {
    // Initialize socket connection
    const socket = io.connect(window.location.origin);
    socket.emit('join', { user_id: currentUserId });

    function sendMessage() {
        const messageText = document.getElementById('messageInput').value;
        const receiverId = document.getElementById('sendMessageBtn').getAttribute('data-receiver-id');

        const messageData = {
            receiver_id: receiverId,
            message_text: messageText,
        };
        // Add the message to the chat window
        const chatWindow = document.getElementById('messageBody');
        const newMessage = document.createElement('div');
        const datetime = formatDateTime(new Date());
        
        newMessage.classList.add('message', 'justify-content-end');
        newMessage.innerHTML = `
            <div class="message-content">
                <p class="message-text">${messageText}</p>
                <small class="text-body-secondary text-end">${datetime}</small>
            </div>
        `;
        chatWindow.appendChild(newMessage);

        // Send the message to the server
        socket.emit('send_message', messageData);
        document.getElementById('messageInput').value = '';  // Clear input field
    }

    socket.on('receive_message', function(data) {
        const chatWindow = document.getElementById('messageBody');
        const newMessage = document.createElement('div');
        newMessage.classList.add('message', 'justify-content-start');
        const datetime = formatDateTime(new Date());
        newMessage.innerHTML = `
            <div class="message-content">
                <p class="message-text">${data.message_text}</p>
                <small class="text-body-secondary">${datetime}</small>
            </div>
        `;
        chatWindow.appendChild(newMessage);
    });

    // Attach the sendMessage function to the send button
    document.getElementById('sendMessageBtn').onclick = sendMessage;
}

// Fill the data of messaging box with sender and receiver
function open_messages(receiverId, receiver_avatar, receiver_fname) {
    if (receiver_avatar == null) {
        document.getElementById("messageAvatar").setAttribute("src", receiver_avatar);
    }

    if (receiver_fname.length > 10) {
        receiver_fname = receiver_fname.substring(0, 10) + "...";
    }
    document.getElementById("messageFname").innerHTML = receiver_fname;

    // Set the receiver ID as a data attribute on the send button
    document.getElementById("sendMessageBtn").setAttribute("data-receiver-id", receiverId);
}

// Call the function after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', (event) => {
    const currentUserId = document.getElementById("currentUserId").value;
    initializeSocketConnection(currentUserId);
});
