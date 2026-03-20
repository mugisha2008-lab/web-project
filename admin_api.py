from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from models import User, Course, Enrollment, CourseRating, Lesson, Exam, ExamAttempt
from database import db

admin_bp = Blueprint('admin', __name__)

# Admin Statistics
@admin_bp.route('/admin/stats', methods=['GET'])
@login_required
def get_admin_stats():
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Basic counts
        total_users = User.query.count()
        total_courses = Course.query.count()
        total_enrollments = Enrollment.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Completions (mock data for now - would need completion tracking)
        total_completions = Enrollment.query.filter_by(status='completed').count()
        
        # Revenue (mock calculation)
        revenue = Enrollment.query.filter_by(status='active').count() * 49.99
        
        # Recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_enrollments = Enrollment.query.order_by(Enrollment.enrolled_at.desc()).limit(5).all()
        
        # Top courses
        top_courses = db.session.query(
            Course.course_id,
            Course.title,
            func.count(Enrollment.enrollment_id).label('enrollment_count')
        ).join(Enrollment).group_by(Course.course_id).order_by(
            func.count(Enrollment.enrollment_id).desc()
        ).limit(5).all()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_courses': total_courses,
                'total_enrollments': total_enrollments,
                'total_completions': total_completions,
                'active_users': active_users,
                'revenue': revenue
            },
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_enrollments': [enrollment.to_dict() for enrollment in recent_enrollments],
            'top_courses': [
                {
                    'course_id': course.course_id,
                    'title': course.title,
                    'enrollment_count': course.enrollment_count
                } for course in top_courses
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management
@admin_bp.route('/admin/users', methods=['GET'])
@login_required
def get_all_users():
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        role_filter = request.args.get('role')
        
        query = User.query
        
        if search:
            query = query.filter(
                User.username.contains(search) | 
                User.email.contains(search) |
                User.first_name.contains(search) |
                User.last_name.contains(search)
            )
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
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

@admin_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Don't allow admin to deactivate themselves
        if user.user_id == current_user.user_id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Course Management for Admin
@admin_bp.route('/admin/courses', methods=['GET'])
@login_required
def get_all_courses_admin():
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        
        query = Course.query
        
        if search:
            query = query.filter(
                Course.title.contains(search) | 
                Course.description.contains(search) |
                Course.course_code.contains(search)
            )
        
        courses = query.order_by(Course.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Add enrollment counts and ratings
        courses_data = []
        for course in courses.items:
            course_dict = course.to_dict()
            course_dict['enrollment_count'] = Enrollment.query.filter_by(course_id=course.course_id).count()
            
            # Calculate average rating
            avg_rating = db.session.query(func.avg(CourseRating.rating)).filter_by(course_id=course.course_id).scalar()
            course_dict['average_rating'] = float(avg_rating) if avg_rating else 0
            
            courses_data.append(course_dict)
        
        return jsonify({
            'courses': courses_data,
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

@admin_bp.route('/admin/courses/<int:course_id>/toggle-status', methods=['POST'])
@login_required
def toggle_course_status(course_id):
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        course = Course.query.get_or_404(course_id)
        course.is_active = not course.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'Course {"activated" if course.is_active else "deactivated"} successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# System Health
@admin_bp.route('/admin/health', methods=['GET'])
@login_required
def get_system_health():
    try:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Database connection test
        db_status = 'healthy' if db.engine else 'disconnected'
        
        # Recent activity counts
        recent_signups = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        recent_enrollments = Enrollment.query.filter(
            Enrollment.enrolled_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Storage usage (mock data)
        storage_usage = {
            'total': '10GB',
            'used': '3.2GB',
            'available': '6.8GB'
        }
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'recent_activity': {
                'signups_7_days': recent_signups,
                'enrollments_7_days': recent_enrollments
            },
            'storage': storage_usage,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
