CREATE DATABASE smart_brewery;

USE smart_brewery;

CREATE TABLE environment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature FLOAT,
    humidity FLOAT
);