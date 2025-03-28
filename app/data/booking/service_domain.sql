CREATE TABLE service_domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIMEZONE DEFAULT NOW()
    updated_at TIMESTAMP WITH TIMEZONE
);

CREATE INDEX idx_service_domains_name ON service_domains (name);