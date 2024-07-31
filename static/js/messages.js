// Fill the data of messaging box with sender and receiver
function open_messages(receiver_avatar, receiver_fname) {
    document.getElementById("messageAvatar").setAttribute("src", receiver_avatar);

    if (receiver_fname.length > 10) {
        receiver_fname = receiver_fname.substring(0, 10) + "...";
    }
    document.getElementById("messageFname").innerHTML = receiver_fname;
}