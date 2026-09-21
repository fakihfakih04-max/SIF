-- Seed the initial administrator with the default local-development password.
INSERT OR IGNORE INTO users (id, username, password_hash, role, active) VALUES (1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Administrator', 1);
UPDATE users SET password_hash='8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', role='Administrator', active=1 WHERE username='admin';
