CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the updated_ar column exists
    IF NEW.updated_at IS DISTINCT FROM OLD.updated_at THEN
    NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    table_record RECORD;
BEGIN
    -- Loop through all tables in the schema
    FOR table_record IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
            AND table_schema = 'public' -- Adjust schema name as needed
    LOOP
        -- Dynamically create the trigger for each table with 'updated_at'
        EXECUTE format('
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_timestamp();
        ', table_record.table_name, table_record.table_name);
    END LOOP;
END $$;
