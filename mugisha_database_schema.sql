-- Mugisha Online Learning Platform Database Schema
-- MySQL Database Structure

-- Create database
CREATE DATABASE IF NOT EXISTS mugisha CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mugisha;

-- 1. Users table - stores all user types (students, instructors, admins)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role ENUM('student', 'instructor', 'admin') NOT NULL DEFAULT 'student',
    phone VARCHAR(20),
    profile_image VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- 2. Courses table - stores course information
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    instructor_id INT NOT NULL,
    category VARCHAR(100),
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    duration_hours INT DEFAULT 0,
    price DECIMAL(10,2) DEFAULT 0.00,
    thumbnail_image VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    INDEX idx_course_code (course_code),
    INDEX idx_instructor (instructor_id),
    INDEX idx_category (category),
    INDEX idx_active (is_active)
);

-- 3. Enrollments table - tracks student enrollments in courses
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status ENUM('active', 'completed', 'dropped') DEFAULT 'active',
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    final_grade DECIMAL(5,2),
    completion_date DATE,
    UNIQUE KEY unique_enrollment (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_student_enrollments (student_id),
    INDEX idx_course_enrollments (course_id),
    INDEX idx_status (status)
);

-- 4. Lessons table - stores individual lessons within courses
CREATE TABLE lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content LONGTEXT,
    video_url VARCHAR(500),
    lesson_order INT NOT NULL,
    duration_minutes INT DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_course_lessons (course_id),
    INDEX idx_lesson_order (course_id, lesson_order),
    INDEX idx_published (is_published)
);

-- 5. Exams table - stores exam information
CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL DEFAULT 60,
    total_marks DECIMAL(10,2) NOT NULL DEFAULT 100.00,
    passing_marks DECIMAL(10,2) NOT NULL DEFAULT 60.00,
    start_date DATETIME,
    end_date DATETIME,
    max_attempts INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_course_exams (course_id),
    INDEX idx_exam_dates (start_date, end_date),
    INDEX idx_active (is_active)
);

-- 6. Questions table - stores exam questions
CREATE TABLE questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type ENUM('multiple_choice', 'true_false', 'short_answer', 'essay') NOT NULL,
    marks DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    question_order INT NOT NULL,
    explanation TEXT,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    INDEX idx_exam_questions (exam_id),
    INDEX idx_question_order (exam_id, question_order),
    INDEX idx_question_type (question_type)
);

-- 7. Answer Options table - stores multiple choice options
CREATE TABLE answer_options (
    option_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    option_order INT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_question_options (question_id),
    INDEX idx_option_order (question_id, option_order)
);

-- 8. Exam Attempts table - tracks student exam attempts
CREATE TABLE exam_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    attempt_number INT NOT NULL DEFAULT 1,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    total_score DECIMAL(10,2) DEFAULT 0.00,
    percentage_score DECIMAL(5,2) DEFAULT 0.00,
    status ENUM('in_progress', 'completed', 'submitted', 'expired') DEFAULT 'in_progress',
    time_taken_minutes INT,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    UNIQUE KEY unique_attempt (student_id, exam_id, attempt_number),
    INDEX idx_student_attempts (student_id),
    INDEX idx_exam_attempts (exam_id),
    INDEX idx_status (status),
    INDEX idx_attempt_dates (start_time)
);

-- 9. Student Answers table - stores student responses to questions
CREATE TABLE student_answers (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_option_id INT,
    text_answer TEXT,
    marks_obtained DECIMAL(5,2) DEFAULT 0.00,
    is_correct BOOLEAN DEFAULT FALSE,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_option_id) REFERENCES answer_options(option_id) ON DELETE SET NULL,
    UNIQUE KEY unique_answer (attempt_id, question_id),
    INDEX idx_attempt_answers (attempt_id),
    INDEX idx_question_answers (question_id)
);

-- 10. Progress Tracking table - tracks student lesson progress
CREATE TABLE progress_tracking (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    lesson_id INT NOT NULL,
    completion_status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
    completion_date DATETIME,
    time_spent_minutes INT DEFAULT 0,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    UNIQUE KEY unique_progress (student_id, lesson_id),
    INDEX idx_student_progress (student_id),
    INDEX idx_course_progress (course_id),
    INDEX idx_lesson_progress (lesson_id),
    INDEX idx_completion_status (completion_status)
);

-- 11. Certificates table - stores issued certificates
CREATE TABLE certificates (
    certificate_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    issue_date DATE DEFAULT CURRENT_DATE,
    certificate_url VARCHAR(500),
    verification_code VARCHAR(50) UNIQUE NOT NULL,
    grade_achieved VARCHAR(10),
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY unique_certificate (student_id, course_id),
    INDEX idx_student_certificates (student_id),
    INDEX idx_course_certificates (course_id),
    INDEX idx_verification_code (verification_code)
);

-- 12. Notifications table - stores system notifications
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('exam_reminder', 'grade_posted', 'course_update', 'system_announcement') DEFAULT 'system_announcement',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_notifications (user_id),
    INDEX idx_notification_type (notification_type),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- 13. Course Materials table - stores additional course resources
CREATE TABLE course_materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_url VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_course_materials (course_id),
    INDEX idx_file_type (file_type)
);

-- 14. Discussion Forums table - for course discussions
CREATE TABLE discussion_forums (
    forum_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE RESTRICT,
    INDEX idx_course_forums (course_id),
    INDEX idx_forum_creator (created_by),
    INDEX idx_active (is_active)
);

-- 15. Forum Posts table - stores forum posts and replies
CREATE TABLE forum_posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    forum_id INT NOT NULL,
    parent_post_id INT NULL,
    author_id INT NOT NULL,
    title VARCHAR(200),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (forum_id) REFERENCES discussion_forums(forum_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_post_id) REFERENCES forum_posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    INDEX idx_forum_posts (forum_id),
    INDEX idx_parent_post (parent_post_id),
    INDEX idx_author (author_id),
    INDEX idx_created_at (created_at),
    INDEX idx_pinned (is_pinned)
);

-- 16. System Settings table - for platform configuration
CREATE TABLE system_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('platform_name', 'Mugisha Learning Platform', 'string', 'Name of the learning platform'),
('max_file_size', '10485760', 'number', 'Maximum file upload size in bytes'),
('default_exam_duration', '60', 'number', 'Default exam duration in minutes'),
('auto_grade_exams', 'true', 'boolean', 'Automatically grade objective questions'),
('certificate_template', 'default', 'string', 'Default certificate template');
