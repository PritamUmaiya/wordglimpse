CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY,
    fname TEXT NOT NULL,
    lname TEXT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- hashed password
    avatar TEXT,
    cover TEXT,
    bio TEXT,
    profession TEXT,
    public_email TEXT, -- Visiable email in profile
    username TEXT UNIQUE,
    -- Social media
    facebook TEXT,
    github TEXT,
    linkedin TEXT,
    instagram TEXT,
    twitter TEXT,
    website TEXT,
    -- Account Info
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME,
    -- Settings
    offer_messaging INTEGER DEFAULT 1, -- INTEGER 0 for no or 1 for yes
    post_reported_times INTEGER DEFAULT 0 -- Times reported post by other users
);

CREATE TABLE followings (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    UNIQUE(user_id, profile_id),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(profile_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_followings_profile_id ON followings(profile_id);

CREATE TABLE posts (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    image TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_posts_user_id ON posts(user_id);

CREATE TABLE saved_posts (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE voted_posts (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    vote INTEGER NOT NULL, -- 1 for upvote -1 for downvote
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE INDEX idx_voted_posts_post_id ON voted_posts(post_id);

CREATE TABLE reported_posts (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    report TEXT NOT NULL,
    comment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE commented_posts (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE INDEX idx_commented_posts_post_id ON commented_posts(post_id);

CREATE TABLE messages (
    id INTEGER NOT NULL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    seen INTEGER NOT NULL DEFAULT 0, -- 0 for not seen 1 for seen
    FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_receiver_id ON messages(receiver_id);

CREATE TABLE blocked_messages (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(person_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    link TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    seen INTEGER NOT NULL DEFAULT 0, -- 0 for not seen 1 for seen
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE feedbacks (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    feedback TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);