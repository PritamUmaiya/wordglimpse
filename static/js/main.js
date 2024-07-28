document.addEventListener('DOMContentLoaded', () => {
    // Toggle Theme Functions
    const theme = localStorage.getItem('theme');
    const themeToggler = document.querySelector('#themeToggler');
    if (theme) {
        document.body.setAttribute('data-bs-theme', theme);
        if (themeToggler) {
            themeToggler.checked = (theme == 'dark');
        }
    }
    if (themeToggler) {
        themeToggler.addEventListener('change', () => {
            const newTheme = themeToggler.checked ? 'dark' : 'light';
            document.body.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
});

// Search Toggler Functions
function openSearch() {
    document.getElementById('searchContainer').classList.remove('d-none');
    document.getElementById('searchInput').focus(); // Opens keyboard by default in extra small devices
}
function closeSearch() {
    document.getElementById('searchContainer').classList.add('d-none');
}

// Toggle Arrow for category in Left menu
function toggleArrow() {
    document.getElementById('keyArrDown').classList.toggle('rotate-180');
}

// Count the letters of textarea
function countLetter(textareaId, counterId) {
    var textarea = document.getElementById(textareaId);
    var letterCount = textarea.value.length;
    var counterDisplay = document.getElementById(counterId);
    counterDisplay.textContent = letterCount;
}

// Convert number to short number
function convert_to_short_number(value) {
    let formattedValue;
    if (value >= 1000000) {
        formattedValue = (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        formattedValue = (value / 1000).toFixed(1) + 'k';
    } else {
        return value.toString();
    }

    // Remove trailing '.0' if present
    if (formattedValue.endsWith('.0k')) {
        formattedValue = formattedValue.slice(0, -3) + 'k';
    } else if (formattedValue.endsWith('.0M')) {
        formattedValue = formattedValue.slice(0, -3) + 'M';
    }

    return formattedValue;
}

// Follow or unfollow user profile
function follow_profile(button, id) {
    let total_followers = document.getElementById('total_followers');
    let total_followers_text = document.getElementById('total_followers_text');
    let followers_count = 0;

    if (total_followers) {
        followers_count = parseInt(total_followers.getAttribute('data-total-followers'));
    }
    
    fetch('/follow_profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ profile_id: id})
    })
    .then(response => response.json())
    .then(data => {
        if (data['message'] == 'followed') {
            button.innerText = 'Following';
            if (total_followers && followers_count < 1000) {
                total_followers.innerText = convert_to_short_number(followers_count + 1);
                total_followers.setAttribute('data-total-followers', followers_count + 1);
                if (followers_count + 1 > 1) {
                    total_followers_text.innerText = 'Followers';
                }
                else {
                    total_followers_text.innerText = 'Follower';
                }
            }
        }
        else if (data['message'] == 'unfollowed') {
            button.innerText = 'Follow';
            if (total_followers && followers_count > 0) {
                total_followers.innerText = convert_to_short_number(followers_count - 1);
                total_followers.setAttribute('data-total-followers', followers_count - 1);
                if (followers_count - 1 > 1) {
                    total_followers_text.innerText = 'Followers';
                }
                else {
                    total_followers_text.innerText = 'Follower';
                }
            }
        }
    })
    .catch(error => {  // Corrected syntax here
        console.error('Error:', error);
    });
}

// Function to save post
function save_post(button, id) {
    fetch('/save_post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: id})
    })
    .then(response => response.json())
    .then(data => {
        if (data['message'] == 'saved') {
            button.innerHTML = `<i class="bi bi-bookmark-fill text-primary"></i>`;
        }
        else if (data['message'] == 'unsaved') {
            button.innerHTML = `<i class="bi bi-bookmark"></i>`;
        }
    })
    .catch(error => {  // Corrected syntax here
        console.error('Error:', error);
    });
}