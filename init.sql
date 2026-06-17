-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- 1. 用户表
CREATE TABLE sys_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录账号',
    password VARCHAR(255) NOT NULL COMMENT '加密密码',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    role_type TINYINT NOT NULL COMMENT '角色：1-管理员 2-教师 3-学生',
    phone VARCHAR(20) COMMENT '联系电话',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常 0-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);

-- 2. 班级表
CREATE TABLE class_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_name VARCHAR(50) NOT NULL COMMENT '班级名称',
    class_code VARCHAR(20) UNIQUE NOT NULL COMMENT '班级编号',
    teacher_id INT COMMENT '班主任ID（关联sys_user）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES sys_user(id) ON DELETE SET NULL
);

-- 3. 学生表
CREATE TABLE student_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(20) UNIQUE NOT NULL COMMENT '学号',
    name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    gender TINYINT COMMENT '性别：1-男 2-女',
    age INT COMMENT '年龄',
    phone VARCHAR(20) COMMENT '学生电话',
    class_id INT COMMENT '所属班级ID',
    user_id INT UNIQUE COMMENT '关联的用户账号ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES class_info(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES sys_user(id) ON DELETE CASCADE
);

-- 4. 成绩表
CREATE TABLE student_score (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    subject VARCHAR(50) NOT NULL COMMENT '科目名称',
    score DECIMAL(5,2) NOT NULL COMMENT '分数（0-100）',
    semester VARCHAR(20) NOT NULL COMMENT '考试学期，如2024-2025-1',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student_info(id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_subject_semester (student_id, subject, semester),
    CONSTRAINT chk_score_range CHECK (score >= 0 AND score <= 100)
);

-- 5. 公告表
CREATE TABLE sys_notice (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL COMMENT '公告标题',
    content TEXT NOT NULL COMMENT '公告内容',
    is_top TINYINT DEFAULT 0 COMMENT '是否置顶：1-置顶 0-普通',
    creator_id INT NOT NULL COMMENT '发布人ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES sys_user(id) ON DELETE CASCADE
);

-- 6. 插入初始管理员账号（用户名：admin，密码：123456）
-- 密码加密方式：SHA256(密码 + 盐)，盐固定为 "student2024"
-- 123456加密后：8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
INSERT INTO sys_user (username, password, real_name, role_type, phone, status) VALUES
('admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '系统管理员', 1, '13800000000', 1);venv\Scripts\activate