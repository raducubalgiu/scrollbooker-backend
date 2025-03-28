-- CREATE TABLE - FILTERS
CREATE TABLE filters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- CREATE TRIGGER FOR UPDATING updated_at
CREATE TRIGGER update_filters_timestamp
BEFORE UPDATE ON filters
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- DROP TRIGGER FOR UPDATING updated_at
DROP TRIGGER IF EXISTS update_filters_timestamp ON filters;