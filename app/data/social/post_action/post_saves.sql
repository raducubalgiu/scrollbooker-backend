CREATE TABLE post_saves(
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_post_saves_post_id ON post_likes (post_id);
CREATE INDEX idx_post_saves_user_id ON post_likes (user_id);
CREATE INDEX idx_post_saves_post_user ON post_likes (post_id, user_id)