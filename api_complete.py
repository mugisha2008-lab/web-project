from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

from models import User, Course, Enrollment, Lesson, Exam, Question, AnswerOption, ExamAttempt, StudentAnswer
from database import db

api_bp = Blueprint('api', __name__)

# Course Management
@api_bp.route('/courses', methods=['GET'])
def get_courses():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Course.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Course.title.contains(search) | Course.description.contains(search))
        
        courses = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'courses': [course.to_dict() for course in courses.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': courses.total,
                'pages': courses.pages,
                'has_next': courses.has_next,
                'has_prev': courses.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        return jsonify({'course': course.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses', methods=['POST'])
@login_required
def create_course():
    try:
        if current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        course = Course(
            course_code=data['course_code'],
            title=data['title'],
            description=data.get('description', ''),
            instructor_id=current_user.user_id,
            category=data.get('category', ''),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            duration_hours=data.get('duration_hours', 0),
            price=data.get('price', 0.00),
            thumbnail_image=data.get('thumbnail_image', '')
        )
        db.session.add(course)
        db.session.commit()
        return jsonify({'course': course.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lesson Management
@api_bp.route('/courses/<int:course_id>/lessons', methods=['GET'])
def get_lessons(course_id):
    try:
        lessons = Lesson.query.filter_by(course_id=course_id, is_published=True).order_by(Lesson.lesson_order).all()
        return jsonify({
            'lessons': [lesson.to_dict() for lesson in lessons]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        return jsonify({'lesson': lesson.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>/lessons', methods=['POST'])
@login_required
def create_lesson(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        if course.instructor_id != current_user.user_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        lesson = Lesson(
            course_id=course_id,
            title=data['title'],
            content=data.get('content', ''),
            video_url=data.get('video_url', ''),
            duration_minutes=data.get('duration_minutes', 0),
            lesson_order=data.get('lesson_order', 1),
            is_published=data.get('is_published', False)
        )
        db.session.add(lesson)
        db.session.commit()
        return jsonify({'lesson': lesson.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Exam Management
@api_bp.route('/courses/<int:course_id>/exams', methods=['GET'])
def get_exams(course_id):
    try:
        exams = Exam.query.filter_by(course_id=course_id, is_active=True).all()
        return jsonify({
            'exams': [exam.to_dict() for exam in exams]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    try:
        exam = Exam.query.get_or_404(exam_id)
        exam_data = exam.to_dict()
        exam_data['questions'] = [q.to_dict() for q in exam.questions.order_by(Question.question_order)]
        return jsonify({'exam': exam_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>/exams', methods=['POST'])
@login_required
def create_exam(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        if course.instructor_id != current_user.user_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        exam = Exam(
            course_id=course_id,
            title=data['title'],
            description=data.get('description', ''),
            duration_minutes=data['duration_minutes'],
            passing_marks=data.get('passing_marks', 60),
            max_attempts=data.get('max_attempts', 3)
        )
        db.session.add(exam)
        db.session.commit()
        return jsonify({'exam': exam.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enrollment Management
@api_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id, course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Already enrolled'}), 400
        
        enrollment = Enrollment(
            student_id=current_user.user_id,
            course_id=course_id
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({'enrollment': enrollment.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/students/<int:student_id>/enrollments', methods=['GET'])
@login_required
def get_student_enrollments(student_id):
    try:
        if current_user.user_id != student_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        return jsonify({
            'enrollments': [enrollment.to_dict() for enrollment in enrollments]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Exam Taking
@api_bp.route('/exams/<int:exam_id>/attempt', methods=['POST'])
@login_required
def start_exam_attempt(exam_id):
    try:
        exam = Exam.query.get_or_404(exam_id)
        
        # Check if enrolled
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id, course_id=exam.course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in course'}), 403
        
        # Create new attempt
        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=current_user.user_id,
            attempt_number=1  # Simplified
        )
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({'attempt': attempt.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/attempts/<int:attempt_id>/submit', methods=['POST'])
@login_required
def submit_exam_attempt(attempt_id):
    try:
        attempt = ExamAttempt.query.get_or_404(attempt_id)
        
        if attempt.student_id != current_user.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        answers = data.get('answers', [])
        
        # Process answers
        total_score = 0
        for answer_data in answers:
            question = Question.query.get(answer_data['question_id'])
            student_answer = StudentAnswer(
                attempt_id=attempt_id,
                question_id=answer_data['question_id'],
                selected_option_id=answer_data.get('selected_option_id'),
                text_answer=answer_data.get('text_answer', ''),
                is_correct=answer_data.get('is_correct', False),
                marks_obtained=answer_data.get('marks_obtained', 0)
            )
            db.session.add(student_answer)
            total_score += answer_data.get('marks_obtained', 0)
        
        # Update attempt
        attempt.total_score = total_score
        attempt.percentage_score = (total_score / attempt.exam.total_marks) * 100
        attempt.status = 'submitted'
        attempt.end_time = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'attempt': attempt.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management (Admin only)
@api_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        
        query = User.query
        if search:
            query = query.filter(
                User.username.contains(search) | 
                User.email.contains(search) |
                User.first_name.contains(search) |
                User.last_name.contains(search)
            )
        
        users = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    try:
        if current_user.user_id != user_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = User.query.get_or_404(user_id)
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    try:
        if current_user.user_id != user_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard Data
@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    try:
        if current_user.role == 'admin':
            total_users = User.query.count()
            total_courses = Course.query.count()
            total_enrollments = Enrollment.query.count()
            
            return jsonify({
                'stats': {
                    'total_users': total_users,
                    'total_courses': total_courses,
                    'total_enrollments': total_enrollments
                }
            }), 200
            
        elif current_user.role == 'instructor':
            courses = Course.query.filter_by(instructor_id=current_user.user_id).all()
            total_students = db.session.query(Enrollment).join(Course).filter(Course.instructor_id == current_user.user_id).count()
            
            return jsonify({
                'stats': {
                    'total_courses': len(courses),
                    'total_students': total_students,
                    'courses': [course.to_dict() for course in courses]
                }
            }), 200
            
        else:  # student
            enrollments = Enrollment.query.filter_by(student_id=current_user.user_id).all()
            completed_courses = len([e for e in enrollments if e.status == 'completed'])
            in_progress = len([e for e in enrollments if e.status == 'active'])
            
            return jsonify({
                'stats': {
                    'total_enrollments': len(enrollments),
                    'completed_courses': completed_courses,
                    'in_progress': in_progress,
                    'enrollments': [enrollment.to_dict() for enrollment in enrollments]
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
