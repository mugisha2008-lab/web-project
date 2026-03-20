from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from models import DiscussionForum, ForumPost, User, Course, Notification
from database import db

forums_bp = Blueprint('forums', __name__)

# Discussion Forum Routes
@forums_bp.route('/courses/<int:course_id>/forums', methods=['GET'])
@login_required
def get_course_forums(course_id):
    try:
        # Check if user is enrolled in the course or is instructor/admin
        course = Course.query.get_or_404(course_id)
        
        if (current_user.role == 'student' and 
            not course.enrollments.filter_by(student_id=current_user.user_id).first()):
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        forums = DiscussionForum.query.filter_by(course_id=course_id, is_active=True).all()
        
        return jsonify({
            'forums': [forum.to_dict() for forum in forums]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forums_bp.route('/courses/<int:course_id>/forums', methods=['POST'])
@login_required
def create_forum(course_id):
    try:
        # Check if user is instructor or admin
        course = Course.query.get_or_404(course_id)
        
        if current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        forum = DiscussionForum(
            course_id=course_id,
            title=data['title'],
            description=data.get('description', ''),
            created_by=current_user.user_id
        )
        
        db.session.add(forum)
        db.session.commit()
        
        # Create notification for enrolled students
        enrollments = course.enrollments.all()
        for enrollment in enrollments:
            notification = Notification(
                user_id=enrollment.student_id,
                title='New Discussion Forum',
                message=f'A new discussion forum "{forum.title}" has been created for {course.title}',
                notification_type='discussion',
                related_id=forum.forum_id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Forum created successfully',
            'forum': forum.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forums_bp.route('/forums/<int:forum_id>', methods=['GET'])
@login_required
def get_forum(forum_id):
    try:
        forum = DiscussionForum.query.get_or_404(forum_id)
        
        # Check if user is enrolled in the course or is instructor/admin
        if (current_user.role == 'student' and 
            not forum.course.enrollments.filter_by(student_id=current_user.user_id).first()):
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        # Get posts with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        posts = ForumPost.query.filter_by(
            forum_id=forum_id, 
            parent_post_id=None
        ).order_by(
            ForumPost.is_pinned.desc(),
            ForumPost.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'forum': forum.to_dict(),
            'posts': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Forum Post Routes
@forums_bp.route('/forums/<int:forum_id>/posts', methods=['POST'])
@login_required
def create_post(forum_id):
    try:
        forum = DiscussionForum.query.get_or_404(forum_id)
        
        # Check if user is enrolled in the course or is instructor/admin
        if (current_user.role == 'student' and 
            not forum.course.enrollments.filter_by(student_id=current_user.user_id).first()):
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        data = request.get_json()
        
        post = ForumPost(
            forum_id=forum_id,
            title=data.get('title', ''),
            content=data['content'],
            created_by=current_user.user_id,
            parent_post_id=data.get('parent_post_id')
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Create notification for forum creator (if it's a reply)
        if post.parent_post_id:
            parent_post = ForumPost.query.get(post.parent_post_id)
            if parent_post and parent_post.created_by != current_user.user_id:
                notification = Notification(
                    user_id=parent_post.created_by,
                    title='New Reply',
                    message=f'{current_user.first_name} {current_user.last_name} replied to your post in "{forum.title}"',
                    notification_type='discussion',
                    related_id=forum.forum_id
                )
                db.session.add(notification)
                db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forums_bp.route('/posts/<int:post_id>/replies', methods=['GET'])
@login_required
def get_post_replies(post_id):
    try:
        post = ForumPost.query.get_or_404(post_id)
        
        # Check if user is enrolled in the course or is instructor/admin
        if (current_user.role == 'student' and 
            not post.forum.course.enrollments.filter_by(student_id=current_user.user_id).first()):
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        replies = ForumPost.query.filter_by(parent_post_id=post_id).order_by(
            ForumPost.created_at.asc()
        ).all()
        
        return jsonify({
            'replies': [reply.to_dict() for reply in replies]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forums_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    try:
        post = ForumPost.query.get_or_404(post_id)
        
        # Check if user is enrolled in the course or is instructor/admin
        if (current_user.role == 'student' and 
            not post.forum.course.enrollments.filter_by(student_id=current_user.user_id).first()):
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        post.like_count += 1
        db.session.commit()
        
        return jsonify({
            'message': 'Post liked successfully',
            'like_count': post.like_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Notification Routes
@forums_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        notifications = Notification.query.filter_by(
            user_id=current_user.user_id
        ).order_by(
            Notification.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'unread_count': Notification.query.filter_by(user_id=current_user.user_id, is_read=False).count(),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': notifications.total,
                'pages': notifications.pages,
                'has_next': notifications.has_next,
                'has_prev': notifications.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forums_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.user_id != current_user.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Notification marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forums_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    try:
        Notification.query.filter_by(user_id=current_user.user_id, is_read=False).update(
            {'is_read': True}
        )
        db.session.commit()
        
        return jsonify({
            'message': 'All notifications marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
