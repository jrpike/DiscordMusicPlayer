CREATE USER 'host'@'localhost' IDENTIFIED BY 'hostpass123';
GRANT ALL PRIVILEGES ON * . * TO 'host'@'localhost';
CREATE DATABASE music_player
USE music_player
CREATE TABLE song_queue (
id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
url VARCHAR(100),
status BOOLEAN
)