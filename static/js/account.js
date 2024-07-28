document.addEventListener('DOMContentLoaded', () => {

    let inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            document.querySelector('#fname').classList.remove('is-invalid');
            document.querySelector('#lname').classList.remove('is-invalid');
            document.querySelector('#username').classList.remove('is-invalid');
            document.querySelector('#fnameError').classList.add('d-none');
            document.querySelector('#lnameError').classList.add('d-none');
        });
    });
    // Validate Name
    document.querySelector('#nameForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        // Get form data
        let formData = new FormData(this);
        // Send data to the server
        let response = await fetch('/validate_name', {
            method: 'POST',
            body: formData
        });
        // Get the response as JSON
        let errors = await response.json();
        // If no errors, submit the form
        if (errors.length === 0) {
            this.submit();
        } else {
            // Handle errors
            errors.forEach(error => {
                for (let field in error) {
                    if (field == 'fname') {
                        document.querySelector('#fname').classList.add('is-invalid');
                        document.querySelector('#fnameError').classList.remove('d-none');
                        document.querySelector('#fnameError').innerHTML = error[field];
                    }
                    if (field == 'lname') {
                        document.querySelector('#lname').classList.add('is-invalid');
                        document.querySelector('#lnameError').classList.remove('d-none');
                        document.querySelector('#lnameError').innerHTML = error[field];
                    }
                }
            });
        }
    });

    // Validate Username
    let username = document.querySelector('#username');
    username.addEventListener('input', async function(e) {
        let has_username = document.querySelector('#has_username');
        let response;
        if (has_username) {
            response = await fetch('/validate_username?username=' + username.value + '&has_username=' + has_username.value);
        }
        else {
            response = await fetch('/validate_username?username=' + username.value);
        }
        let message = await response.json();

        if(message.length === 0) {
            document.querySelector('#usernameMessage').innerHTML = `<small class="text-success">Username available.</small>`;
        } else {
            document.querySelector('#usernameMessage').innerHTML = message[0];
        }
        document.querySelector('#usernamePreview').innerHTML = username.value.toLowerCase();
    });
});