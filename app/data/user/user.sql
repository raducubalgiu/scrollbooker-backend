-- Create Table Users

-- Create Index for business_id
CREATE UNIQUE INDEX idx_users_id ON users(id);
CREATE INDEX idx_users_business_id ON users(business_id)
