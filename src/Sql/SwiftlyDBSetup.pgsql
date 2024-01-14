
CREATE DATABASE swiftlydb;

CREATE TABLE Threads (
    row_id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255),
    message_body TEXT,
    subject VARCHAR(255),
    user_email VARCHAR(255),
    from_email VARCHAR(255),
    timestamp_of_last_message TIMESTAMP,
    email_link TEXT,
    processed_status BOOLEAN,
    last_updated TIMESTAMP,
    user_status VARCHAR(100),
    next_step VARCHAR(100),
    action TEXT,
    deadline TIMESTAMP,
    summary TEXT,
    effort VARCHAR(100),
    todo_constraint TEXT
);
