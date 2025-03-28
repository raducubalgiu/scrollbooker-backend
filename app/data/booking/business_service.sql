CREATE TABLE business_services (
    business_id INT NOT NULL,
    service_id INT NOT NULL,
    PRIMARY KEY (business_id, service_id),
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    CONSTRAINT unique_business_service UNIQUE (business_id, service_id)
);