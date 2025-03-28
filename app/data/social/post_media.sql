CREATE TABLE post_media (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    type VARCHAR NOT NULL,
    thumbnail_url TEXT NULL,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_post_media_url ON post_media (url);

CREATE INDEX idx_post_media_type ON post_media (type);

CREATE INDEX idx_post_media_post_type ON post_media (post_id, media_type);