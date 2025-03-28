CREATE TABLE employment_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    employer_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES businesses(id) ON DELETE CASCADE,
    CONSTRAINT uix_employee_employer_business UNIQUE (employee_id, employer_id, business_id)
);

CREATE INDEX idx_employee_id ON employment_requests (employee_id);
CREATE INDEX idx_employer_id ON employment_requests (employer_id);
CREATE INDEX idx_business_id ON employment_requests (business_id);
CREATE INDEX idx_status ON employment_requests (status);