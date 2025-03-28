CREATE TABLE comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    CONSTRAINT fk_comment_likes_comment FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_likes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_comment_like UNIQUE (comment_id, user_id),
);

CREATE INDEX idx_commentlike_comment ON comment_likes (comment_id);
CREATE INDEX idx_commentlike_user ON comment_likes (user_id);
CREATE INDEX idx_commentlike_user_comment ON comment_likes (user_id, comment_id);