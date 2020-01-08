CREATE USER 'host'@'localhost' IDENTIFIED BY 'hostpass123';
GRANT ALL PRIVILEGES ON * . * TO 'host'@'localhost';
CREATE DATABASE music_player;
USE music_player
CREATE TABLE song_queue (
id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
url VARCHAR(100),
thumbnail_url VARCHAR(100),
title VARCHAR(100),
duration INT,
status BOOLEAN
);
ALTER DATABASE music_player CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
ALTER TABLE song_queue CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE song_queue CHANGE title title VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
