CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    age_group VARCHAR(20) NOT NULL
        CHECK (age_group IN ('minor', 'adult', 'senior'))
);


CREATE TABLE customer_quarantine (
    quarantine_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    raw_record JSONB NOT NULL,
    errors JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

