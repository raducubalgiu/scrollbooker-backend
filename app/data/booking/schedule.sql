-- Create Table for schedules
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    day_of_week VARCHAR(9) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time NULL,
    end_time NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    CONSTRAINT unique_user_day UNIQUE (user_id, day_of_week),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_business FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_id ON schedules (user_id);
CREATE INDEX idx_business_id ON schedules (business_id);
CREATE INDEX idx_start_time ON schedules (start_time);
CREATE INDEX idx_end_time ON schedules (end_time);
CREATE INDEX idx_user_id_day_of_week ON schedules (user_id, day_of_week);
CREATE INDEX idx_user_id_start_time_end_time_day_of_week ON schedules (user_id, start_time, end_time, day_of_week);
CREATE INDEX idx_business_id_start_time_end_time_day_of_week ON schedules (business_id, start_time, end_time, day_of_week);