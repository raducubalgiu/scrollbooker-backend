CREATE TABLE review_product_likes (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL,
    product_author_user_id INTEGER NOT NULL,
    CONSTRAINT fk_review_product_likes_review FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_product_likes_author FOREIGN KEY (product_author_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_review_product_like UNIQUE (review_id, product_author_user_id)
);

CREATE INDEX idx_reviewproductlike_review ON review_product_likes (review_id);
CREATE INDEX idx_reviewproductlike_author ON review_product_likes (product_author_user_id);
CREATE INDEX idx_reviewproductlike_author_review ON review_product_likes (review_id, product_author_user_id);