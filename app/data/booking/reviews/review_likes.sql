CREATE TABLE review_likes (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    CONSTRAINT fk_review_likes_review FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_likes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_review_like UNIQUE (review_id, user_id)
);

CREATE INDEX idx_reviewlike_review ON review_likes (review_id);
CREATE INDEX idx_reviewlike_user ON review_likes (user_id);
CREATE INDEX idx_reviewlike_user_review ON review_likes (user_id, review_id);