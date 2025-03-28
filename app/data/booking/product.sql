-- Create Products Table
CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    duration INTEGER NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    price_with_discount DOUBLE PRECISION NOT NULL,
    discount DOUBLE PRECISION NOT NULL,
    filter_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,
    employee_id INTEGER,
    reviews_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    CONSTRAINT fk_filter FOREIGN KEY (filter_id) REFERENCES filters(id) ON DELETE CASCADE,
    CONSTRAINT fk_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    CONSTRAINT fk_business FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create Index for name
CREATE INDEX idx_products_name ON products(name);

-- Create Index for price
CREATE INDEX idx_products_price ON products(price);