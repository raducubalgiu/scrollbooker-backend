-- Create user_counters table
CREATE TABLE user_counters (
    user_id INTEGER PRIMARY KEY,
    followings_count INTEGER NOT NULL DEFAULT 0,
    followers_count INTEGER NOT NULL DEFAULT 0,
    products_count INTEGER NOT NULL DEFAULT 0,
    posts_count INTEGER NOT NULL DEFAULT 0,
    ratings_count INTEGER NOT NULL DEFAULT 0,
    ratings_average DOUBLE PRECISION NOT NULL DEFAULT 5,
    CONSTRAINT fk_user FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
)