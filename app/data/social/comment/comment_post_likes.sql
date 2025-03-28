CREATE TABLE comment_post_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL,
    post_author_id INTEGER NOT NULL,
    CONSTRAINT fk_comment_post_likes_comment FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_post_likes_author FOREIGN KEY (post_author_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_comment_post_like UNIQUE (comment_id, post_author_id)
);

CREATE INDEX idx_commentpostlike_comment ON comment_post_likes (comment_id);
CREATE INDEX idx_commentpostlike_author ON comment_post_likes (post_author_id);
CREATE INDEX idx_commentpostlike_author_comment ON comment_post_likes (post_author_id, comment_id);