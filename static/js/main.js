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
    else {
        // Based on current time
        const currentHour = new Date().getHours();
        if (currentHour >= 6 && currentHour < 18) {
            document.body.setAttribute('data-bs-theme', 'light');
        } else {
            document.body.setAttribute('data-bs-theme', 'dark');
        }
    }
    if (themeToggler) {
        themeToggler.addEventListener('change', () => {
            const newTheme = themeToggler.checked ? 'dark' : 'light';
            document.body.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
    // Add root url to username
    if (document.getElementById('rootUrl')) {
        document.getElementById('rootUrl').innerHTML = window.location.origin;
    }
});

/* 
* ---- Helper Functions ----
*/
// Count the letters of textarea
function countLetter(inputId, counterId) {
    var input = document.getElementById(inputId);
    var letterCount = input.value.length;
    var counterDisplay = document.getElementById(counterId);
    counterDisplay.textContent = letterCount;
}

// Function to format datetime
function formatDateTime(datetimeStr) {
    let date = new Date(datetimeStr);
    let options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

// Convert number to short number
function short_number(value) {
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

// Convert number to short with 99+
function short_value(value) {
    if (value >= 100) {
        return '99+';
    }
    else {
        return value;
    }
}

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
                total_followers.innerText = short_number(followers_count + 1);
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
                total_followers.innerText = short_number(followers_count - 1);
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

/*
 *-------  Post related Functions -------
 */
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
        upvote_count.innerText = short_number(parseInt(upvotes) + parseInt(data['upvote']));
        upvote_count.setAttribute('data-upvotes', parseInt(upvotes) + parseInt(data['upvote']));
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Manage posts Edit
function edit_post(post) {
    document.getElementById("editPostId").value = post.id;
    document.getElementById("editPostContent").value = post.content;
    document.getElementById("editPostContentCount").innerText = post.content.length;
}

function delete_post(post_id) {
    document.getElementById("deletePostId").value = post_id;
}


/*
 *-------  Comment related Functions -------
 */

// Fill the comment modal with data
function openComments(post_id, user_id) {
    let commentFooter = document.getElementById('commentFooter');
    
    // Load the comments
    get_comments(post_id, user_id);

    commentFooter.innerHTML = `
    <input type="text" class="form-control" placeholder="Write a comment..." id="comment_input_${post_id}" title="comment" autocomplete="off">
    <button type="button" class="btn btn-primary" onclick="create_comment(${post_id}, ${user_id})">
        <i class="bi bi-chevron-right"></i>
    </button>
    `;
    
}

// Function to create comment
function create_comment(post_id, user_id) {
    let comment = document.getElementById(`comment_input_${post_id}`).value;
    let commentCount = document.getElementById(`comment_count_${post_id}`);
    let commentCountValue = parseInt(commentCount.getAttribute('data-comment-count'));
    
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
            // Increase comment count by 1
            commentCount.innerText = short_value(commentCountValue + 1);
            commentCount.setAttribute('data-comment-count', commentCountValue + 1);
            // Clear the input
            document.getElementById(`comment_input_${post_id}`).value = '';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
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
            if (offset == 0) {
                commentBody.innerHTML = '';
            }
            // Remove load more comment button
            if (offset != 0) {
                document.getElementById('loadMoreCommentBtn').remove();
            }
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

            // Add load more button
            if (comments.length == limit) {
                commentBody.innerHTML += `
                    <div class="text-center">
                        <button type="button" class="btn btn-primary" id="loadMoreCommentBtn" onclick="get_comments(${post_id}, ${user_id}, ${offset + limit})">Load More</button>
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
    let commentCount = document.getElementById(`comment_count_${post_id}`);
    let commentCountValue = parseInt(commentCount.getAttribute('data-comment-count'));
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
            // Decrease comment count by 1
            commentCount.innerText = short_value(commentCountValue - 1);
            commentCount.setAttribute('data-comment-count', commentCountValue - 1);
        }
    })
    .catch(error => {
        console.error('Error', error)
    });
}

// TO DO: Function to share post
function sharePost(id) {
    return;
}

// TO DO: Function to report post
function reportPost(id) {
    return;
}

// TO DO: Function to notify admin
function notifyAdmin(id) {
    return;
}
