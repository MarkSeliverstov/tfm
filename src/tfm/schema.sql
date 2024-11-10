CREATE TABLE IF NOT EXISTS users
(
    id INT PRIMARY KEY,
    initial_balance DECIMAL(12, 2) NOT NULL,
    current_balance DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transactions_types VARCHAR[] NOT NULL
);


CREATE TABLE IF NOT EXISTS transactions
(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    type VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- CREATE OR REPLACE FUNCTION validate_transaction_type()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     -- Check if the transaction type exists in the user's transactions_types array
--     IF NOT EXISTS (
--         SELECT 1
--         FROM users
--         WHERE id = NEW.user_id
--         AND NEW.type = ANY (transactions_types)
--     ) THEN
--         RAISE EXCEPTION 'Invalid transaction type: % for user_id: %', NEW.type, NEW.user_id;
--     END IF;
--
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER check_transaction_type
-- BEFORE INSERT OR UPDATE ON transactions
-- FOR EACH ROW
-- EXECUTE FUNCTION validate_transaction_type();
--
