CREATE TABLE hashtags(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL CHECK (char_length(name) >= 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_hashtags_name ON hashtags(name);