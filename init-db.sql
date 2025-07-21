-- Create the users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    family_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    workplace VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    note TEXT,
    hashed_password VARCHAR(255) NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data only if the table is empty
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users) THEN
        INSERT INTO users (name, family_name, email, workplace, position, note, hashed_password, is_approved, is_superuser)
        VALUES
            ('Admin', 'Crude Oil Search', 'admin@example.com', 'Crude Oil Search', 'Admin', NULL, '$2b$12$z.bzspVajav2sG4RKf70xupf7GuXkmW1Ytb8S4VyfVmIlMgKvQunG', TRUE, TRUE),
            ('John', 'Doe', 'john.doe@example.com', 'Tech Corp', 'Data Analyst', 'Interested in data visualization', '$2b$12$Kix2tYf2Z7Qz3z4Z5Y6X7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j', TRUE, FALSE),
            ('Jane', 'Smith', 'jane.smith@example.com', 'Research Inc', 'Researcher', NULL, '$2b$12$Ljy3uZ4v5W6x7Y8z9A0B1C2D3E4F5G6H7I8J9K0L1M2N3O4P5Q6R', FALSE, FALSE),
            ('Alice', 'Johnson', 'alice.johnson@example.com', 'Analytics Ltd', 'Manager', 'Needs access to advanced reports', '$2b$12$Mkx4vY5w6X7y8Z9A0B1C2D3E4F5G6H7I8J9K0L1M2N3O4P5Q6R7S', FALSE, FALSE);
    END IF;
END $$;
