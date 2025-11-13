-- MySQL建表语句文件
-- 注意：此脚本需要在MySQL命令行或客户端中以root用户执行

-- 检查并创建数据库
CREATE DATABASE IF NOT EXISTS riddle_db DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE riddle_db;

-- 创建谜语类型表
CREATE TABLE IF NOT EXISTS riddle_type (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建谜语表
CREATE TABLE IF NOT EXISTS riddle (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    riddle TEXT NOT NULL,
    answer TEXT NOT NULL,
    riddle_type_id INT UNSIGNED,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_riddle (riddle(255)),
    FOREIGN KEY (riddle_type_id) REFERENCES riddle_type(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 显示创建结果
SELECT '数据库和表创建/验证成功' AS result;