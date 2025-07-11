-- To run this file, use the command: mysql -u root -p < init.sql

-- 1. Create a user
CREATE USER IF NOT EXISTS 'auth_user'@'localhost' IDENTIFIED BY 'auth123';

-- 2. Create a database
CREATE DATABASE IF NOT EXISTS auth;

-- 3. Grant privileges
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';

-- 4. Use the new database
USE auth;

-- 5. Create the user table
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 6. Insert data
INSERT INTO user(email, password) VALUES ('ask@gmail.com', 'auth@123');
