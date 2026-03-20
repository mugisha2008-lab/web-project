from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from models import Assignment, AssignmentSubmission, User, Course, Enrollment
from database import db

assignments_bp = Blueprint('assignments', __name__)

# File upload configuration
UPLOAD_FOLDER = 'uploads/assignments'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'zip', 'rar', 'jpg', 'jpeg', 'png', 'gif', 'ppt', 'pptx', 'xls', 'xlsx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Assignment Management
@assignments_bp.route('/courses/<int:course_id>/assignments', methods=['GET'])
@login_required
def get_course_assignments(course_id):
    try:
        # Check if user is enrolled or instructor/admin
        course = Course.query.get_or_404(course_id)
        
        if current_user.role == 'student':
            enrollment = Enrollment.query.filter_by(
                course_id=course_id, 
                student_id=current_user.user_id
            ).first()
            if not enrollment:
                return jsonify({'error': 'Not enrolled in this course'}), 403
        elif current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Assignment.query.filter_by(course_id=course_id)
        
        # Students only see published assignments
        if current_user.role == 'student':
            query = query.filter_by(is_published=True)
        
        assignments = query.order_by(Assignment.due_date.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Add submission status for students
        assignments_data = []
        for assignment in assignments.items:
            assignment_dict = assignment.to_dict()
            
            if current_user.role == 'student':
                submission = AssignmentSubmission.query.filter_by(
                    assignment_id=assignment.assignment_id,
                    student_id=current_user.user_id
                ).first()
                assignment_dict['submission'] = submission.to_dict() if submission else None
            else:
                assignment_dict['submissions_count'] = assignment.submissions.count()
                assignment_dict['graded_count'] = assignment.submissions.filter(
                    AssignmentSubmission.status == 'graded'
                ).count()
            
            assignments_data.append(assignment_dict)
        
        return jsonify({
            'assignments': assignments_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': assignments.total,
                'pages': assignments.pages,
                'has_next': assignments.has_next,
                'has_prev': assignments.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/courses/<int:course_id>/assignments', methods=['POST'])
@login_required
def create_assignment(course_id):
    try:
        # Check if user is instructor or admin
        if current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        course = Course.query.get_or_404(course_id)
        
        # Check if user is course instructor or admin
        if current_user.role == 'instructor' and course.instructor_id != current_user.user_id:
            return jsonify({'error': 'Not authorized for this course'}), 403
        
        data = request.get_json()
        
        assignment = Assignment(
            course_id=course_id,
            title=data['title'],
            description=data['description'],
            instructions=data.get('instructions', ''),
            max_score=data.get('max_score', 100),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            created_by=current_user.user_id,
            is_published=data.get('is_published', False)
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment created successfully',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@login_required
def get_assignment(assignment_id):
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check permissions
        if current_user.role == 'student':
            enrollment = Enrollment.query.filter_by(
                course_id=assignment.course_id,
                student_id=current_user.user_id
            ).first()
            if not enrollment or not assignment.is_published:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role == 'instructor' and assignment.course.instructor_id != current_user.user_id:
            return jsonify({'error': 'Not authorized for this course'}), 403
        
        assignment_dict = assignment.to_dict()
        
        # Add submission info for students
        if current_user.role == 'student':
            submission = AssignmentSubmission.query.filter_by(
                assignment_id=assignment_id,
                student_id=current_user.user_id
            ).first()
            assignment_dict['submission'] = submission.to_dict() if submission else None
        
        return jsonify({'assignment': assignment_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
@login_required
def update_assignment(assignment_id):
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if user is instructor or admin
        if current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if current_user.role == 'instructor' and assignment.course.instructor_id != current_user.user_id:
            return jsonify({'error': 'Not authorized for this course'}), 403
        
        data = request.get_json()
        
        updatable_fields = ['title', 'description', 'instructions', 'max_score', 'due_date', 'is_published']
        for field in updatable_fields:
            if field in data:
                if field == 'due_date' and data[field]:
                    setattr(assignment, field, datetime.fromisoformat(data[field]))
                else:
                    setattr(assignment, field, data[field])
        
        assignment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment updated successfully',
            'assignment': assignment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Assignment Submissions
@assignments_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@login_required
def get_assignment_submissions(assignment_id):
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if user is instructor or admin
        if current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if current_user.role == 'instructor' and assignment.course.instructor_id != current_user.user_id:
            return jsonify({'error': 'Not authorized for this course'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        submissions = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id
        ).order_by(AssignmentSubmission.submitted_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'submissions': [submission.to_dict() for submission in submissions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': submissions.total,
                'pages': submissions.pages,
                'has_next': submissions.has_next,
                'has_prev': submissions.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>/submit', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if student is enrolled
        enrollment = Enrollment.query.filter_by(
            course_id=assignment.course_id,
            student_id=current_user.user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        if not assignment.is_published:
            return jsonify({'error': 'Assignment not published'}), 403
        
        # Check if already submitted
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.user_id
        ).first()
        
        if submission and submission.status == 'submitted':
            return jsonify({'error': 'Assignment already submitted'}), 400
        
        data = request.get_json()
        
        # Create or update submission
        if submission:
            submission.content = data.get('content', '')
            submission.status = 'submitted'
            submission.submitted_at = datetime.utcnow()
        else:
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.user_id,
                content=data.get('content', ''),
                status='submitted',
                submitted_at=datetime.utcnow()
            )
            db.session.add(submission)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment submitted successfully',
            'submission': submission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>/upload', methods=['POST'])
@login_required
def upload_assignment_file(assignment_id):
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if student is enrolled
        enrollment = Enrollment.query.filter_by(
            course_id=assignment.course_id,
            student_id=current_user.user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large'}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(file_path)
        
        # Get or create submission
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.user_id
        ).first()
        
        if not submission:
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.user_id
            )
            db.session.add(submission)
        
        submission.file_path = file_path
        submission.file_name = file.filename
        submission.file_size = file_size
        submission.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'submission': submission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/submissions/<int:submission_id>/download', methods=['GET'])
@login_required
def download_submission_file(submission_id):
    try:
        submission = AssignmentSubmission.query.get_or_404(submission_id)
        
        # Check permissions
        if current_user.role == 'student':
            if submission.student_id != current_user.user_id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user.role == 'instructor':
            assignment = Assignment.query.get(submission.assignment_id)
            if assignment.course.instructor_id != current_user.user_id:
                return jsonify({'error': 'Not authorized for this course'}), 403
        elif current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        if not submission.file_path or not os.path.exists(submission.file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            submission.file_path,
            as_attachment=True,
            download_name=submission.file_name
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/submissions/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_submission(submission_id):
    try:
        submission = AssignmentSubmission.query.get_or_404(submission_id)
        
        # Check if user is instructor or admin
        if current_user.role not in ['instructor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        assignment = Assignment.query.get(submission.assignment_id)
        
        if current_user.role == 'instructor' and assignment.course.instructor_id != current_user.user_id:
            return jsonify({'error': 'Not authorized for this course'}), 403
        
        data = request.get_json()
        
        submission.score = data.get('score')
        submission.feedback = data.get('feedback', '')
        submission.status = 'graded'
        submission.graded_at = datetime.utcnow()
        submission.graded_by = current_user.user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Submission graded successfully',
            'submission': submission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
