from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
import os
import uuid
import qrcode
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from models import User, Course, Enrollment
from database import db

cert_bp = Blueprint('certificates', __name__)

@cert_bp.route('/certificates/generate/<int:course_id>', methods=['POST'])
@login_required
def generate_certificate(course_id):
    try:
        # Check if student is enrolled and completed the course
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.user_id, 
            course_id=course_id,
            status='completed'
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Course not completed'}), 400
        
        # Check if certificate already exists
        existing_cert = Certificate.query.filter_by(
            student_id=current_user.user_id,
            course_id=course_id
        ).first()
        
        if existing_cert:
            return jsonify({'certificate': existing_cert.to_dict()}), 200
        
        # Generate certificate
        verification_code = str(uuid.uuid4())[:8].upper()
        certificate = Certificate(
            student_id=current_user.user_id,
            course_id=course_id,
            issue_date=datetime.utcnow(),
            completion_date=enrollment.completion_date or datetime.utcnow(),
            grade_achieved='A',  # Simplified
            verification_code=verification_code
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        # Generate PDF certificate
        pdf_path = generate_certificate_pdf(certificate)
        certificate.certificate_url = f'/certificates/download/{certificate.certificate_id}'
        db.session.commit()
        
        return jsonify({
            'certificate': certificate.to_dict(),
            'download_url': certificate.certificate_url
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cert_bp.route('/certificates/<int:certificate_id>', methods=['GET'])
def get_certificate(certificate_id):
    try:
        certificate = Certificate.query.get_or_404(certificate_id)
        return jsonify({'certificate': certificate.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cert_bp.route('/certificates/verify/<verification_code>', methods=['GET'])
def verify_certificate(verification_code):
    try:
        certificate = Certificate.query.filter_by(verification_code=verification_code).first()
        if not certificate:
            return jsonify({'valid': False}), 404
        
        return jsonify({
            'valid': True,
            'certificate': certificate.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cert_bp.route('/certificates/download/<int:certificate_id>', methods=['GET'])
def download_certificate(certificate_id):
    try:
        certificate = Certificate.query.get_or_404(certificate_id)
        
        # Check authorization
        if (certificate.student_id != current_user.user_id and 
            current_user.role != 'admin'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        pdf_path = generate_certificate_pdf(certificate)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'certificate_{certificate_id}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cert_bp.route('/students/<int:student_id>/certificates', methods=['GET'])
@login_required
def get_student_certificates(student_id):
    try:
        if current_user.user_id != student_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        certificates = Certificate.query.filter_by(student_id=student_id).all()
        return jsonify({
            'certificates': [cert.to_dict() for cert in certificates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_certificate_pdf(certificate):
    """Generate PDF certificate"""
    try:
        # Create certificates directory if it doesn't exist
        if not os.path.exists('certificates'):
            os.makedirs('certificates')
        
        filename = f'certificates/certificate_{certificate.certificate_id}.pdf'
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = styles['Title']
        story.append(Paragraph("Certificate of Completion", title_style))
        story.append(Spacer(1, 20))
        
        # Certificate content
        normal_style = styles['Normal']
        
        # Student name
        student = User.query.get(certificate.student_id)
        course = Course.query.get(certificate.course_id)
        
        story.append(Paragraph(f"This is to certify that", normal_style))
        story.append(Paragraph(f"<b>{student.first_name} {student.last_name}</b>", normal_style))
        story.append(Paragraph(f"has successfully completed the course", normal_style))
        story.append(Paragraph(f"<b>{course.title}</b>", normal_style))
        story.append(Spacer(1, 20))
        
        # Course details
        story.append(Paragraph(f"Duration: {course.duration_hours} hours", normal_style))
        story.append(Paragraph(f"Grade: {certificate.grade_achieved}", normal_style))
        story.append(Paragraph(f"Date: {certificate.issue_date.strftime('%B %d, %Y')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Verification code
        story.append(Paragraph(f"Verification Code: {certificate.verification_code}", normal_style))
        
        # Generate QR code for verification
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"https://mugisha.com/verify/{certificate.verification_code}")
        qr.make(fit=True)
        
        # Save QR code
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = f'certificates/qr_{certificate.certificate_id}.png'
        qr_img.save(qr_path)
        
        # Build PDF
        doc.build(story)
        
        return filename
        
    except Exception as e:
        print(f"Error generating certificate PDF: {e}")
        return None
