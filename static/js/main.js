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
            button.setAttribute('title', 'Unfollow');
            if (total_followers) {
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
            button.setAttribute('title', 'Follow');
            if (total_followers) {
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

// Function to vote post
function vote_post(id, vote) {
    let upvote_btn = document.getElementById('upvote_btn_' + id);
    let downvote_btn = document.getElementById('downvote_btn_' + id);
    let upvote_count = document.getElementById('upvote_count_' + id);
    let upvotes = upvote_count.getAttribute('data-upvotes');
    fetch('/vote_post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: id, vote: vote})
    })
    .then(response => response.json())
    .then(data => {
        // Handle buttons 
        if (data['message'] == 'upvoted') {
            upvote_btn.innerHTML = `<i class="bi bi-caret-up-fill text-primary"></i>`;
            downvote_btn.innerHTML = `<i class="bi bi-caret-down"></i>`;
        }
        else if (data['message'] == 'downvoted') {
            upvote_btn.innerHTML = `<i class="bi bi-caret-up"></i>`;
            downvote_btn.innerHTML = `<i class="bi bi-caret-down text-danger"></i>`;
        }
        else if (data['message'] == 'unvoted') {
            upvote_btn.innerHTML = `<i class="bi bi-caret-up"></i>`;
            downvote_btn.innerHTML = `<i class="bi bi-caret-down"></i>`;
        }

        // Handle upvote count
        upvote_count.innerText = convert_to_short_number(parseInt(upvotes) + parseInt(data['upvote']));
        upvote_count.setAttribute('data-upvotes', parseInt(upvotes) + parseInt(data['upvote']));
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Fill the comment modal with data
function openComments(post_id, user_id) {
    let commentFooter = document.getElementById('commentFooter');
    
    // Load the comments
    get_comments(post_id, user_id);

    commentFooter.innerHTML = `
    <input type="text" class="form-control" placeholder="Write a comment..." id="comment_input_${post_id}" title="comment" autocomplete="off">
    <button type="button" class="btn btn-primary" onclick="create_comment(${post_id}, '{{ user.id }}')">
        <i class="bi bi-chevron-right"></i>
    </button>
    `;
    
}

// Function to create comment
function create_comment(post_id, user_id) {
    let comment = document.getElementById(`comment_input_${post_id}`).value;
    
    fetch('/comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: post_id, comment: comment})
    })
    .then(response => response.json())
    .then(data => {

        if (data['message'] == 'commented') {
            // Load the comments
            get_comments(post_id, user_id);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to format datetime
function formatDateTime(datetimeStr) {
    let date = new Date(datetimeStr);
    let options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

// Function to get comments
function get_comments(post_id, user_id, offset=0, limit=10) {
    let commentBody = document.getElementById('commentBody');

    fetch('/get_comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: post_id, offset: offset, limit: limit})
    })
    .then(response => response.json())
    .then(data => {
        if (data['message'] == 'comments') {
            // Clear Previous Comments
            commentBody.innerHTML = '';
            // Add New Comments
            let comments = data['comments'];
            
            for (let i = 0; i < comments.length; i++) {
                let comment = comments[i];

                let button = '';
                if (parseInt(user_id) == parseInt(comment.user_id)) {
                    button = `
                    <button type="button" class="btn btn-small" onclick="delete_comment(${comment.comment_id}, ${post_id}, ${user_id})">
                        <i class="bi bi-trash"></i>
                    </button>`;
                }
                commentBody.innerHTML += `
                    <div class="mb-2 px-2 rounded bg-body-tertiary">
                        <div class="d-flex flex-row justify-content-between">
                            <div class="d-flex flex-column">
                                <a href="/profile/${comment.user_id}">${comment.fname}</a>
                                <small class="text-body-secondary">${formatDateTime(comment.created_at)}</small>
                            </div>
                            ${button}
                        </div>
                        <span>${comment.comment}</span>
                    </div>
                `;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// Function to delete comment
function delete_comment(comment_id, post_id, user_id) {
    fetch('/delete_comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ comment_id: comment_id})
    })
    .then (response => response.json())
    .then(data => {
        if (data['message'] == 'deleted') {
            get_comments(post_id, user_id);
        }
    })
    .catch(error => {
        console.error('Error', error)
    });
}