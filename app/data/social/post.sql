CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    description VARCHAR(500) NOT NULL,
    bookable BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    hashtags TEXT[],
    mentions BIGINT[],
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    save_count INT DEFAULT 0,
    expiration_time TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX idx_posts_bookable ON posts (bookable);
CREATE INDEX idx_posts_user_id ON posts (user_id);
CREATE INDEX idx_posts_create_at ON posts (created_at);
CREATE INDEX idx_posts_expiration_time ON posts (expiration_time);
CREATE INDEX idx_posts_bookable_expiration_time ON posts (bookable, expiration_time);