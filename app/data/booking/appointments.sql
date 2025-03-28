-- Later we'll create the status enum
-- CREATE TYPE appointment_status AS ENUM ('canceled', 'in_progress', 'finished')

-- Crate the appointments table
CREATE TABLE appointments(
    id SERIAL PRIMARY KEY,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    -- status appointment_status DEFAULT 'in_progress',
    status VARCHAR NOT NULL, -- Later we will change to be the type enum: 'deleted', 'in_progress', 'finished'
    customer_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    CONSTRAINT unique_user_start_date UNIQUE (user_id, start_date)
);

-- Create Indexes
CREATE INDEX idx_appointments_start_date ON appointments(start_date);
CREATE INDEX idx_appointments_end_date ON appointments(end_date);
CREATE INDEX idx_appointments_customer_id ON appointments(customer_id);
CREATE INDEX idx_appointments_product_id ON appointments(product_id);
CREATE INDEX idx_appointments_business_id ON appointments(business_id);
CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_status ON appointments(status);

CREATE INDEX idx_appointments_user_time ON appointments(service_id, user_id, start_date, end_date);
CREATE INDEX idx_appointments_business_time ON appointments(service_id, business_id, start_date, end_date);
CREATE INDEX idx_appointments_business_user_time ON appointments(business_id, user_id, start_date, end_date);
