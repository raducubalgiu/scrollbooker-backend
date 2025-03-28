-- Create Businesses table
CREATE TABLE businesses(
    id SERIAL PRIMARY KEY,
    owner_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description TEXT,
    address TEXT NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    has_employees BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Index for query businesses by location
CREATE INDEX idx_businesses_location ON businesses GIST(location);

-- Create Index for owner_id
CREATE INDEX idx_businesses_owner_id ON businesses(owner_id);

-- Create Unique Index for location (coordinates)
CREATE UNIQUE INDEX uq_business_location ON businesses (ST_AsText(location));

-- FETCH BY DISTANCE
SELECT b.id, ST_AsText(b.location) AS location, ROUND((ST_Distance(b.location::geography, ST_SetSRID(ST_Point(26.019, 44.421), 4326)::geography) / 1000)::numeric, 2) AS distance FROM businesses b WHERE ST_DWithin(b.location::geography, ST_SetSRID(ST_Point(26.019, 44.421), 4326)::geography, 3000) ORDER BY distance ASC;

-- SELECT a business with descriptive location values
SELECT id, ST_AsText(location) AS location_text FROM businesses;