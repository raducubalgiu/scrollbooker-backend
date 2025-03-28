-- Creating the Services table
CREATE TABLE services(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    keywords JSONB DEFAULT '[]'::JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
)

-- Create Indexex
CREATE INDEX idx_service_name ON services (name);
CREATE INDEX idx_service_keywords ON services USING GIN (keywords);
CREATE INDEX idx_service_active ON services (active);
CREATE INDEX idx_service_name_keywords ON services (name, keywords);
CREATE INDEX idx_service_name_keywords_active ON services (name, keywords, active);

SELECT b.id AS business_id, b.description AS business_description, s.id AS service_id, s.name AS idx_service_name
FROM businesses b
JOIN business_services bs ON b.id = bs.business_id
JOIN services s ON s.id = bs.service_id
WHERE b.id = 24 AND s.id = 7;