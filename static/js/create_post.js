document.addEventListener('DOMContentLoaded', () => {
    
    // Remove errors form form
    let inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            document.querySelector('#imageError').classList.add('d-none');
            document.querySelector('#titleError').classList.add('d-none');
            document.querySelector('#categoryError').classList.add('d-none');
            document.querySelector('#contentError').classList.add('d-none');
        });
    });

    // Validate post form
    document.querySelector('#postForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        // Get form data
        let formData = new FormData(this);
        // Send data to the server
        let response = await fetch('/validate_post', {
            method: 'POST',
            body: formData
        });
        // Get the response as JSON
        let errors = await response.json();
        console.log(errors);
        // If no errors, submit the form
        if (errors.length == 0) {
            this.submit();
        } else {
            // Handle errors
            errors.forEach(error => {
                for (let field in error) {
                    if (field == 'image') {
                        document.querySelector('#imageError').classList.remove('d-none');
                        document.querySelector('#imageError').innerHTML = error[field];
                    }
                    if (field == 'title') {
                        document.querySelector('#titleError').classList.remove('d-none');
                        document.querySelector('#titleError').innerHTML = error[field];
                    }
                    if (field == 'category') {
                        document.querySelector('#categoryError').classList.remove('d-none');
                        document.querySelector('#categoryError').innerHTML = error[field];
                    }
                    if (field == 'content') {
                        document.querySelector('#contentError').classList.remove('d-none');
                        document.querySelector('#contentError').innerHTML = error[field];
                    }
                }
            });
        }
    });
    
    /* 
        Upon selection postImage and show it in the preview
    */
        const chooseFile = document.getElementById("postImage");
        const imgPreview = document.getElementById("postImagePreview");
    
        chooseFile.addEventListener("change", function () {
        getImgData();
        });
    
        function getImgData() {
            const files = chooseFile.files[0];
            if (files) {
                const fileReader = new FileReader();
                fileReader.readAsDataURL(files);
                fileReader.addEventListener("load", function () {
                imgPreview.style.display = "block";
                imgPreview.innerHTML = '<img src="' + this.result + '" alt="Preview" />';
                });    
            }
        }
})