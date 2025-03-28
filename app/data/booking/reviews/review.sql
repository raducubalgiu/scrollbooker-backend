-- Create Reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    review VARCHAR(500) NOT NULL,
    rating INTEGER NOT NULL DEFAULT 5 CHECK (rating > 0 AND rating < 6,
    customer_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parent_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_parent FOREIGN KEY (parent_id) REFERENCES reviews(id) ON DELETE CASCADE
);

-- Create Indexes
CREATE INDEX idx_review ON reviews (review);
CREATE INDEX idx_customer_id ON reviews(customer_id);
CREATE INDEX idx_service_id ON reviews(service_id);
CREATE INDEX idx_product_id ON reviews(product_id);
CREATE INDEX idx_customer_user_service ON reviews(customer_id, user_id, service_id);
CREATE INDEX idx_customer_user_product ON reviews(customer_id, user_id, product_id);

