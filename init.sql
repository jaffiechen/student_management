-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- 先清理旧表，确保脚本可重复执行
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS student_score;
DROP TABLE IF EXISTS student_info;
DROP TABLE IF EXISTS class_info;
DROP TABLE IF EXISTS sys_notice;
DROP TABLE IF EXISTS sys_user;
SET FOREIGN_KEY_CHECKS = 1;

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

-- 插入管理员账户
INSERT INTO sys_user (username, password, real_name, role_type, phone, status) VALUES
('admin', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '系统管理员', 1, '13800000000', 1);

-- 插入教师账户
INSERT INTO sys_user (username, password, real_name, role_type, phone, status) VALUES
('teacher_li', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '李华', 2, '13800138001', 1),
('teacher_wang', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '王芳', 2, '13800138002', 1),
('teacher_zhang', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '张伟', 2, '13800138003', 1),
('teacher_zhao', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '赵磊', 2, '13800138004', 1),
('teacher_liu', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '刘洋', 2, '13800138005', 1);

-- 插入学生账户
INSERT INTO sys_user (username, password, real_name, role_type, phone, status) VALUES
('20240001', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '张三', 3, '15911111111', 1),
('20240002', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '李四', 3, '15922222222', 1),
('20240003', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '王五', 3, '15933333333', 1),
('20240004', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '赵六', 3, '15944444444', 1),
('20240005', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '周杰', 3, '15955555555', 1),
('20240006', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '吴迪', 3, '15966666666', 1),
('20240007', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '郑爽', 3, '15977777777', 1),
('20240008', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '陈晨', 3, '15988888888', 1),
('20240009', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '林欣', 3, '15999999999', 1),
('20240010', '067e42a984f6487a74035f623188a8968ccc0594acc7ae11202d7749b1c9482b', '黄伟', 3, '15800000000', 1);

-- 插入班级信息
INSERT INTO class_info (class_name, class_code, teacher_id) VALUES
('计算机科学与技术1班', 'CS2401', 2),
('软件工程1班', 'SE2401', 3),
('数据科学1班', 'DS2401', 4),
('人工智能1班', 'AI2401', 5),
('网络工程1班', 'NE2401', 6);

-- 插入学生档案
INSERT INTO student_info (student_no, name, gender, age, phone, class_id, user_id) VALUES
('20240001', '张三', 1, 20, '15911111111', 1, 7),
('20240002', '李四', 1, 19, '15922222222', 1, 8),
('20240003', '王五', 2, 21, '15933333333', 2, 9),
('20240004', '赵六', 1, 20, '15944444444', 2, 10),
('20240005', '周杰', 1, 19, '15955555555', 3, 11),
('20240006', '吴迪', 2, 20, '15966666666', 3, 12),
('20240007', '郑爽', 2, 21, '15977777777', 4, 13),
('20240008', '陈晨', 1, 20, '15988888888', 4, 14),
('20240009', '林欣', 2, 19, '15999999999', 5, 15),
('20240010', '黄伟', 1, 20, '15800000000', 5, 16);

-- 插入成绩数据
INSERT INTO student_score (student_id, subject, score, semester) VALUES
(1, '高等数学', 85, '2024-2025-1'),
(1, '大学英语', 78, '2024-2025-1'),
(1, 'C语言', 92, '2024-2025-1'),
(1, '数据结构', 88, '2024-2025-2'),
(2, '高等数学', 72, '2024-2025-1'),
(2, '大学英语', 85, '2024-2025-1'),
(2, 'C语言', 79, '2024-2025-1'),
(2, '操作系统', 81, '2024-2025-2'),
(3, '高等数学', 91, '2024-2025-1'),
(3, '大学英语', 88, '2024-2025-1'),
(3, 'C语言', 94, '2024-2025-1'),
(4, '高等数学', 65, '2024-2025-1'),
(4, '大学英语', 70, '2024-2025-1'),
(4, 'C语言', 68, '2024-2025-1'),
(5, '高等数学', 82, '2024-2025-1'),
(5, '大学英语', 79, '2024-2025-1'),
(5, '数据结构', 85, '2024-2025-1'),
(6, '高等数学', 76, '2024-2025-1'),
(6, '大学英语', 81, '2024-2025-1'),
(6, 'C语言', 74, '2024-2025-1'),
(7, '高等数学', 88, '2024-2025-1'),
(7, '大学英语', 92, '2024-2025-1'),
(7, 'C语言', 90, '2024-2025-1'),
(8, '高等数学', 79, '2024-2025-1'),
(8, '大学英语', 83, '2024-2025-1'),
(8, '数据结构', 81, '2024-2025-1'),
(9, '高等数学', 95, '2024-2025-1'),
(9, '大学英语', 91, '2024-2025-1'),
(9, 'C语言', 96, '2024-2025-1'),
(10, '高等数学', 84, '2024-2025-1'),
(10, '大学英语', 87, '2024-2025-1'),
(10, 'C语言', 82, '2024-2025-1');

-- 插入公告
INSERT INTO sys_notice (title, content, is_top, creator_id) VALUES
('关于2024-2025学年第一学期考试安排的通知', '请各位同学查看附件，按时参加考试。', 1, 1),
('图书馆开放时间调整公告', '自下周起，图书馆开放时间改为8:00-22:00。', 0, 2),
('奖学金申请通知', '本学年奖学金申请已开始，请符合条件的同学提交材料。', 1, 1),
('校园网络维护通知', '本周六晚10点至周日早6点校园网将进行维护。', 0, 3),
('学术讲座预告', '周五下午3点在教学楼报告厅举办AI前沿讲座，欢迎参加。', 0, 4),
('迎新晚会通知', '9月28日晚7点在大礼堂举办迎新晚会，请准时参加。', 1, 1),
('体育节报名通知', '一年一度的体育节报名开始了，请各班体育委员统计。', 0, 5),
('关于实验室安全教育的通知', '所有新生必须参加实验室安全培训。', 0, 2),
('端午节放假安排', '6月7日至9日放假，假期注意安全。', 0, 1),
('优秀学生评选通知', '请各班推荐优秀学生候选人，截止日期10月15日。', 1, 6);