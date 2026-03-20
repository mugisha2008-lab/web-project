from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

from models import User, Course, Enrollment, Lesson, Exam, Question, AnswerOption, ExamAttempt, StudentAnswer, CourseRating
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
            description=data.get('description'),
            instructor_id=current_user.user_id,
            category=data.get('category'),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            duration_hours=data.get('duration_hours', 0),
            price=data.get('price', 0.00),
            thumbnail_image=data.get('thumbnail_image')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>', methods=['PUT'])
@login_required
def update_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        
        if current_user.user_id != course.instructor_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        updatable_fields = ['title', 'description', 'category', 'difficulty_level', 'duration_hours', 'price', 'thumbnail_image', 'is_active']
        for field in updatable_fields:
            if field in data:
                setattr(course, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Course updated successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Enrollment Management
@api_bp.route('/enrollments', methods=['POST'])
@login_required
def enroll_course():
    try:
        if current_user.role != 'student':
            return jsonify({'error': 'Only students can enroll in courses'}), 403
        
        data = request.get_json()
        course_id = data.get('course_id')
        
        # Check if course exists and is active
        course = Course.query.filter_by(course_id=course_id, is_active=True).first()
        if not course:
            return jsonify({'error': 'Course not found or inactive'}), 404
        
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id,
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Already enrolled in this course'}), 400
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=current_user.user_id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': 'Enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/enrollments', methods=['GET'])
@login_required
def get_enrollments():
    try:
        enrollments = Enrollment.query.filter_by(student_id=current_user.user_id).all()
        
        return jsonify({
            'enrollments': [enrollment.to_dict() for enrollment in enrollments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lesson Management
@api_bp.route('/courses/<int:course_id>/lessons', methods=['GET'])
@login_required
def get_lessons(course_id):
    try:
        # Check if user is enrolled or is instructor
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id,
            course_id=course_id
        ).first()
        
        course = Course.query.get(course_id)
        
        if not enrollment and current_user.user_id != course.instructor_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.lesson_order).all()
        
        return jsonify({
            'lessons': [lesson.to_dict() for lesson in lessons]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>/lessons', methods=['POST'])
@login_required
def create_lesson(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        
        if current_user.user_id != course.instructor_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        lesson = Lesson(
            course_id=course_id,
            title=data['title'],
            content=data.get('content'),
            video_url=data.get('video_url'),
            lesson_order=data['lesson_order'],
            duration_minutes=data.get('duration_minutes', 0),
            is_published=data.get('is_published', False)
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        return jsonify({
            'message': 'Lesson created successfully',
            'lesson': lesson.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Exam Management
@api_bp.route('/courses/<int:course_id>/exams', methods=['GET'])
@login_required
def get_exams(course_id):
    try:
        # Check if user is enrolled or is instructor
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id,
            course_id=course_id
        ).first()
        
        course = Course.query.get(course_id)
        
        if not enrollment and current_user.user_id != course.instructor_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        exams = Exam.query.filter_by(course_id=course_id, is_active=True).all()
        
        return jsonify({
            'exams': [exam.to_dict() for exam in exams]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/exams/<int:exam_id>', methods=['GET'])
@login_required
def get_exam(exam_id):
    try:
        exam = Exam.query.get_or_404(exam_id)
        
        # Check if user is enrolled in the course
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id,
            course_id=exam.course_id
        ).first()
        
        course = Course.query.get(exam.course_id)
        
        if not enrollment and current_user.user_id != course.instructor_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get questions with options (without correct answers for students)
        questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.question_order).all()
        
        exam_data = exam.to_dict()
        exam_data['questions'] = []
        
        for question in questions:
            question_data = question.to_dict()
            # Remove correct answer indicators for students
            if current_user.role == 'student':
                for option in question_data['answer_options']:
                    option.pop('is_correct', None)
            exam_data['questions'].append(question_data)
        
        return jsonify({'exam': exam_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/exams/<int:exam_id>/attempt', methods=['POST'])
@login_required
def start_exam_attempt(exam_id):
    try:
        if current_user.role != 'student':
            return jsonify({'error': 'Only students can attempt exams'}), 403
        
        exam = Exam.query.get_or_404(exam_id)
        
        # Check if student is enrolled
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id,
            course_id=exam.course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        # Check exam availability
        now = datetime.utcnow()
        if exam.start_date and now < exam.start_date:
            return jsonify({'error': 'Exam has not started yet'}), 400
        
        if exam.end_date and now > exam.end_date:
            return jsonify({'error': 'Exam has ended'}), 400
        
        # Check previous attempts
        attempt_count = ExamAttempt.query.filter_by(
            student_id=current_user.user_id,
            exam_id=exam_id
        ).count()
        
        if attempt_count >= exam.max_attempts:
            return jsonify({'error': 'Maximum attempts reached'}), 400
        
        # Create new attempt
        attempt = ExamAttempt(
            student_id=current_user.user_id,
            exam_id=exam_id,
            attempt_number=attempt_count + 1,
            start_time=now
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Exam attempt started',
            'attempt': attempt.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/attempts/<int:attempt_id>/submit', methods=['POST'])
@login_required
def submit_exam_attempt(attempt_id):
    try:
        if current_user.role != 'student':
            return jsonify({'error': 'Only students can submit exams'}), 403
        
        attempt = ExamAttempt.query.get_or_404(attempt_id)
        
        if attempt.student_id != current_user.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if attempt.status != 'in_progress':
            return jsonify({'error': 'Attempt is not in progress'}), 400
        
        data = request.get_json()
        answers = data.get('answers', [])
        
        total_score = 0
        total_marks = 0
        
        for answer_data in answers:
            question = Question.query.get(answer_data['question_id'])
            if not question:
                continue
            
            total_marks += float(question.marks)
            
            # Check if answer already exists
            student_answer = StudentAnswer.query.filter_by(
                attempt_id=attempt_id,
                question_id=answer_data['question_id']
            ).first()
            
            if not student_answer:
                student_answer = StudentAnswer(
                    attempt_id=attempt_id,
                    question_id=answer_data['question_id']
                )
                db.session.add(student_answer)
            
            # Process answer based on question type
            if question.question_type in ['multiple_choice', 'true_false']:
                selected_option_id = answer_data.get('selected_option_id')
                student_answer.selected_option_id = selected_option_id
                
                if selected_option_id:
                    correct_option = AnswerOption.query.filter_by(
                        question_id=answer_data['question_id'],
                        option_id=selected_option_id,
                        is_correct=True
                    ).first()
                    
                    if correct_option:
                        student_answer.is_correct = True
                        student_answer.marks_obtained = question.marks
                        total_score += float(question.marks)
                    else:
                        student_answer.is_correct = False
                        student_answer.marks_obtained = 0
                else:
                    student_answer.is_correct = False
                    student_answer.marks_obtained = 0
            
            elif question.question_type in ['short_answer', 'essay']:
                student_answer.text_answer = answer_data.get('text_answer', '')
                # For now, auto-grade as 0 - manual grading required
                student_answer.marks_obtained = 0
                student_answer.is_correct = False
        
        # Update attempt
        attempt.end_time = datetime.utcnow()
        attempt.total_score = total_score
        attempt.percentage_score = (total_score / total_marks * 100) if total_marks > 0 else 0
        attempt.status = 'submitted'
        attempt.time_taken_minutes = int((attempt.end_time - attempt.start_time).total_seconds() / 60)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exam submitted successfully',
            'attempt': attempt.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
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
        role = request.args.get('role')
        search = request.args.get('search')
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
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

# Course Rating Management
@api_bp.route('/courses/<int:course_id>/ratings', methods=['GET'])
def get_course_ratings(course_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Check if course exists
        course = Course.query.get_or_404(course_id)
        
        # Get ratings with pagination
        ratings = CourseRating.query.filter_by(course_id=course_id).order_by(
            CourseRating.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        # Calculate average rating
        avg_rating = db.session.query(db.func.avg(CourseRating.rating)).filter_by(course_id=course_id).scalar() or 0
        total_ratings = CourseRating.query.filter_by(course_id=course_id).count()
        
        # Get rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = CourseRating.query.filter_by(course_id=course_id, rating=i).count()
            rating_distribution[str(i)] = count
        
        return jsonify({
            'ratings': [rating.to_dict() for rating in ratings.items],
            'average_rating': round(float(avg_rating), 2),
            'total_ratings': total_ratings,
            'rating_distribution': rating_distribution,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': ratings.total,
                'pages': ratings.pages,
                'has_next': ratings.has_next,
                'has_prev': ratings.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>/ratings', methods=['POST'])
@login_required
def create_course_rating(course_id):
    try:
        # Check if user is enrolled in the course
        enrollment = Enrollment.query.filter_by(
            course_id=course_id, 
            student_id=current_user.user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Must be enrolled in the course to rate it'}), 403
        
        data = request.get_json()
        
        # Validate rating
        rating = data.get('rating')
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        
        # Check if user has already rated this course
        existing_rating = CourseRating.query.filter_by(
            course_id=course_id,
            student_id=current_user.user_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.review = data.get('review', '')
            existing_rating.is_anonymous = data.get('is_anonymous', False)
            existing_rating.updated_at = datetime.utcnow()
            
            message = 'Rating updated successfully'
        else:
            # Create new rating
            new_rating = CourseRating(
                course_id=course_id,
                student_id=current_user.user_id,
                rating=rating,
                review=data.get('review', ''),
                is_anonymous=data.get('is_anonymous', False)
            )
            db.session.add(new_rating)
            
            message = 'Rating created successfully'
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'rating': existing_rating.to_dict() if existing_rating else new_rating.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<int:course_id>/my-rating', methods=['GET'])
@login_required
def get_my_course_rating(course_id):
    try:
        rating = CourseRating.query.filter_by(
            course_id=course_id,
            student_id=current_user.user_id
        ).first()
        
        if not rating:
            return jsonify({'rating': None}), 200
        
        return jsonify({'rating': rating.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
