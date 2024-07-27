document.addEventListener('DOMContentLoaded', () => {
    let inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            document.querySelector('#fname').classList.remove('is-invalid');
            document.querySelector('#lname').classList.remove('is-invalid');
            document.querySelector('#email').classList.remove('is-invalid');
            document.querySelector('#password').classList.remove('is-invalid');
            document.querySelector('#confirmation').classList.remove('is-invalid');
            document.querySelector('#fnameError').classList.add('d-none');
            document.querySelector('#lnameError').classList.add('d-none');
            document.querySelector('#emailError').classList.add('d-none');
            document.querySelector('#passwordError').classList.add('d-none');
            document.querySelector('#confirmationError').classList.add('d-none');
        });
    });
    document.querySelector('form').addEventListener('submit', async function(e) {
        e.preventDefault();
        // Get form data
        let formData = new FormData(this);
        // Send data to the server
        let response = await fetch('/validate_signup', {
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
                    if (field == 'email') {
                        document.querySelector('#email').classList.add('is-invalid');
                        document.querySelector('#emailError').classList.remove('d-none');
                        document.querySelector('#emailError').innerHTML = error[field];
                    }
                    if (field == 'password') {
                        document.querySelector('#password').classList.add('is-invalid');
                        document.querySelector('#passwordError').classList.remove('d-none');
                        document.querySelector('#passwordError').innerHTML = error[field];
                    }
                    if (field == 'confirmation') {
                        document.querySelector('#confirmation').classList.add('is-invalid');
                        document.querySelector('#confirmationError').classList.remove('d-none');
                        document.querySelector('#confirmationError').innerHTML = error[field];
                    }
                }
            });
        }
    });
});