from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Import database instance
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('student', 'instructor', 'admin'), nullable=False, default='student')
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses_taught = db.relationship('Course', backref='instructor', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    exam_attempts = db.relationship('ExamAttempt', backref='student', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Course(db.Model):
    __tablename__ = 'courses'
    
    course_id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category = db.Column(db.String(100))
    difficulty_level = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), default='beginner')
    duration_hours = db.Column(db.Integer, default=0)
    price = db.Column(db.Numeric(10, 2), default=0.00)
    thumbnail_image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')
    exams = db.relationship('Exam', backref='course', lazy='dynamic')
    
    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_code': self.course_code,
            'title': self.title,
            'description': self.description,
            'instructor_id': self.instructor_id,
            'instructor_name': f"{self.instructor.first_name} {self.instructor.last_name}",
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'duration_hours': self.duration_hours,
            'price': float(self.price),
            'thumbnail_image': self.thumbnail_image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'enrollment_count': self.enrollments.count()
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    enrollment_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    enrollment_date = db.Column(db.DATE, default=datetime.utcnow().date)
    status = db.Column(db.Enum('active', 'completed', 'dropped'), default='active')
    completion_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    final_grade = db.Column(db.Numeric(5, 2))
    completion_date = db.Column(db.DATE)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)
    
    def to_dict(self):
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'course_title': self.course.title,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status,
            'completion_percentage': float(self.completion_percentage),
            'final_grade': float(self.final_grade) if self.final_grade else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None
        }

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    lesson_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.TEXT)
    video_url = db.Column(db.String(500))
    lesson_order = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'lesson_id': self.lesson_id,
            'course_id': self.course_id,
            'title': self.title,
            'content': self.content,
            'video_url': self.video_url,
            'lesson_order': self.lesson_order,
            'duration_minutes': self.duration_minutes,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Exam(db.Model):
    __tablename__ = 'exams'
    
    exam_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    total_marks = db.Column(db.Numeric(10, 2), nullable=False, default=100.00)
    passing_marks = db.Column(db.Numeric(10, 2), nullable=False, default=60.00)
    start_date = db.Column(db.DATETIME)
    end_date = db.Column(db.DATETIME)
    max_attempts = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='exam', lazy='dynamic')
    attempts = db.relationship('ExamAttempt', backref='exam', lazy='dynamic')
    
    def to_dict(self):
        return {
            'exam_id': self.exam_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'total_marks': float(self.total_marks),
            'passing_marks': float(self.passing_marks),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_attempts': self.max_attempts,
            'is_active': self.is_active,
            'question_count': self.questions.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Question(db.Model):
    __tablename__ = 'questions'
    
    question_id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('multiple_choice', 'true_false', 'short_answer', 'essay'), nullable=False)
    marks = db.Column(db.Numeric(5, 2), nullable=False, default=1.00)
    question_order = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text)
    
    # Relationships
    answer_options = db.relationship('AnswerOption', backref='question', lazy='dynamic')
    student_answers = db.relationship('StudentAnswer', backref='question', lazy='dynamic')
    
    def to_dict(self):
        return {
            'question_id': self.question_id,
            'exam_id': self.exam_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'marks': float(self.marks),
            'question_order': self.question_order,
            'explanation': self.explanation,
            'answer_options': [opt.to_dict() for opt in self.answer_options] if self.question_type in ['multiple_choice', 'true_false'] else []
        }

class AnswerOption(db.Model):
    __tablename__ = 'answer_options'
    
    option_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    option_order = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'option_id': self.option_id,
            'question_id': self.question_id,
            'option_text': self.option_text,
            'option_order': self.option_order
        }

class ExamAttempt(db.Model):
    __tablename__ = 'exam_attempts'
    
    attempt_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id'), nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False, default=1)
    start_time = db.Column(db.DATETIME, default=datetime.utcnow)
    end_time = db.Column(db.DATETIME)
    total_score = db.Column(db.Numeric(10, 2), default=0.00)
    percentage_score = db.Column(db.Numeric(5, 2), default=0.00)
    status = db.Column(db.Enum('in_progress', 'completed', 'submitted', 'expired'), default='in_progress')
    time_taken_minutes = db.Column(db.Integer)
    
    # Relationships
    student_answers = db.relationship('StudentAnswer', backref='attempt', lazy='dynamic')
    
    __table_args__ = (db.UniqueConstraint('student_id', 'exam_id', 'attempt_number', name='unique_attempt'),)
    
    def to_dict(self):
        return {
            'attempt_id': self.attempt_id,
            'student_id': self.student_id,
            'exam_id': self.exam_id,
            'exam_title': self.exam.title,
            'attempt_number': self.attempt_number,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_score': float(self.total_score),
            'percentage_score': float(self.percentage_score),
            'status': self.status,
            'time_taken_minutes': self.time_taken_minutes
        }

class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'
    
    answer_id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('exam_attempts.attempt_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('answer_options.option_id'))
    text_answer = db.Column(db.Text)
    marks_obtained = db.Column(db.Numeric(5, 2), default=0.00)
    is_correct = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DATETIME, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('attempt_id', 'question_id', name='unique_answer'),)
    
    def to_dict(self):
        return {
            'answer_id': self.answer_id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'selected_option_id': self.selected_option_id,
            'text_answer': self.text_answer,
            'marks_obtained': float(self.marks_obtained),
            'is_correct': self.is_correct,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }

# Discussion Forum Models
class DiscussionForum(db.Model):
    __tablename__ = 'discussion_forums'
    
    forum_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref=db.backref('forums', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('created_forums', lazy='dynamic'))
    posts = db.relationship('ForumPost', backref='forum', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'forum_id': self.forum_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'creator_name': self.creator.first_name + ' ' + self.creator.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'posts_count': self.posts.count()
        }

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    post_id = db.Column(db.Integer, primary_key=True)
    forum_id = db.Column(db.Integer, db.ForeignKey('discussion_forums.forum_id'), nullable=False)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.post_id'), nullable=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref=db.backref('forum_posts', lazy='dynamic'))
    replies = db.relationship('ForumPost', backref=db.backref('parent', remote_side=[post_id]), lazy='dynamic')
    
    def to_dict(self):
        return {
            'post_id': self.post_id,
            'forum_id': self.forum_id,
            'parent_post_id': self.parent_post_id,
            'title': self.title,
            'content': self.content,
            'created_by': self.created_by,
            'author_name': self.author.first_name + ' ' + self.author.last_name,
            'author_role': self.author.role,
            'is_pinned': self.is_pinned,
            'is_locked': self.is_locked,
            'like_count': self.like_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'replies_count': self.replies.count()
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Enum('course', 'exam', 'discussion', 'system', 'achievement'), nullable=False)
    related_id = db.Column(db.Integer)  # Reference to course_id, exam_id, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'related_id': self.related_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

class CourseRating(db.Model):
    __tablename__ = 'course_ratings'
    
    rating_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref=db.backref('ratings', lazy='dynamic'))
    student = db.relationship('User', backref=db.backref('course_ratings', lazy='dynamic'))
    
    # Ensure one rating per student per course
    __table_args__ = (db.UniqueConstraint('course_id', 'student_id'),)
    
    def to_dict(self):
        return {
            'rating_id': self.rating_id,
            'course_id': self.course_id,
            'student_id': self.student_id,
            'student_name': 'Anonymous' if self.is_anonymous else self.student.first_name + ' ' + self.student.last_name,
            'rating': self.rating,
            'review': self.review,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat()
        }

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text)
    max_score = db.Column(db.Integer, default=100)
    due_date = db.Column(db.TIMESTAMP)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref=db.backref('assignments', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('created_assignments', lazy='dynamic'))
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'max_score': self.max_score,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_by': self.created_by,
            'creator_name': self.creator.first_name + ' ' + self.creator.last_name,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submissions_count': self.submissions.count()
        }

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    
    submission_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    status = db.Column(db.Enum('draft', 'submitted', 'graded', 'returned'), default='draft')
    submitted_at = db.Column(db.TIMESTAMP)
    graded_at = db.Column(db.TIMESTAMP)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', backref=db.backref('assignment_submissions', lazy='dynamic'), foreign_keys=[student_id])
    grader = db.relationship('User', backref=db.backref('graded_submissions', lazy='dynamic'), foreign_keys=[graded_by])
    
    # Ensure one submission per student per assignment
    __table_args__ = (db.UniqueConstraint('assignment_id', 'student_id'),)
    
    def to_dict(self):
        return {
            'submission_id': self.submission_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'student_name': self.student.first_name + ' ' + self.student.last_name,
            'content': self.content,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'score': self.score,
            'feedback': self.feedback,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'graded_by': self.graded_by,
            'grader_name': self.grader.first_name + ' ' + self.grader.last_name if self.grader else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
