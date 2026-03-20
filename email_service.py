import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from typing import List, Optional

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None, 
                   attachments: List[str] = None) -> bool:
        """Send email with optional HTML body and attachments"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_welcome_email(self, user_name: str, user_email: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Mugisha Learning Platform!"
        
        body = f"""
Dear {user_name},

Welcome to the Mugisha Learning Platform! We're excited to have you join our community of learners.

Here's what you can do with your new account:
• Browse and enroll in courses
• Track your learning progress
• Participate in discussion forums
• Earn certificates upon course completion
• Access assignments and submit your work

If you have any questions, please don't hesitate to contact our support team.

Best regards,
The Mugisha Learning Platform Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to Mugisha Learning Platform!</h1>
    </div>
    <div class="content">
        <p>Dear {user_name},</p>
        <p>Welcome to the Mugisha Learning Platform! We're excited to have you join our community of learners.</p>
        
        <h3>What you can do:</h3>
        <ul>
            <li>Browse and enroll in courses</li>
            <li>Track your learning progress</li>
            <li>Participate in discussion forums</li>
            <li>Earn certificates upon course completion</li>
            <li>Access assignments and submit your work</li>
        </ul>
        
        <a href="http://localhost:3000/login" class="button">Get Started</a>
        
        <p>If you have any questions, please don't hesitate to contact our support team.</p>
        
        <p>Best regards,<br>The Mugisha Learning Platform Team</p>
    </div>
    <div class="footer">
        <p>&copy; 2024 Mugisha Learning Platform. All rights reserved.</p>
    </div>
</body>
</html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_course_enrollment_confirmation(self, user_name: str, user_email: str, 
                                           course_title: str, instructor_name: str) -> bool:
        """Send enrollment confirmation email"""
        subject = f"Enrollment Confirmed: {course_title}"
        
        body = f"""
Dear {user_name},

Congratulations! You have successfully enrolled in "{course_title}".

Course Details:
• Course: {course_title}
• Instructor: {instructor_name}
• Enrollment Date: {datetime.now().strftime('%B %d, %Y')}

You can now access all course materials, participate in discussions, and track your progress.

To get started, please log in to your account and navigate to your dashboard.

We wish you success in your learning journey!

Best regards,
The Mugisha Learning Platform Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .course-info {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #10b981; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Enrollment Confirmed!</h1>
    </div>
    <div class="content">
        <p>Dear {user_name},</p>
        <p>Congratulations! You have successfully enrolled in "<strong>{course_title}</strong>".</p>
        
        <div class="course-info">
            <h3>Course Details:</h3>
            <p><strong>Course:</strong> {course_title}</p>
            <p><strong>Instructor:</strong> {instructor_name}</p>
            <p><strong>Enrollment Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
        <p>You can now access all course materials, participate in discussions, and track your progress.</p>
        
        <a href="http://localhost:3000/dashboard" class="button">Go to Dashboard</a>
        
        <p>We wish you success in your learning journey!</p>
        
        <p>Best regards,<br>The Mugisha Learning Platform Team</p>
    </div>
    <div class="footer">
        <p>&copy; 2024 Mugisha Learning Platform. All rights reserved.</p>
    </div>
</body>
</html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_assignment_notification(self, user_name: str, user_email: str, 
                                   assignment_title: str, course_title: str, due_date: str) -> bool:
        """Send new assignment notification"""
        subject = f"New Assignment: {assignment_title}"
        
        body = f"""
Dear {user_name},

A new assignment has been posted for your course "{course_title}".

Assignment Details:
• Assignment: {assignment_title}
• Course: {course_title}
• Due Date: {due_date}

Please log in to your account to view the assignment details and submit your work before the deadline.

Good luck with your assignment!

Best regards,
The Mugisha Learning Platform Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #f59e0b; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .assignment-info {{ background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #f59e0b; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>New Assignment Posted!</h1>
    </div>
    <div class="content">
        <p>Dear {user_name},</p>
        <p>A new assignment has been posted for your course "<strong>{course_title}</strong>".</p>
        
        <div class="assignment-info">
            <h3>Assignment Details:</h3>
            <p><strong>Assignment:</strong> {assignment_title}</p>
            <p><strong>Course:</strong> {course_title}</p>
            <p><strong>Due Date:</strong> {due_date}</p>
        </div>
        
        <p>Please log in to your account to view the assignment details and submit your work before the deadline.</p>
        
        <a href="http://localhost:3000/dashboard" class="button">View Assignment</a>
        
        <p>Good luck with your assignment!</p>
        
        <p>Best regards,<br>The Mugisha Learning Platform Team</p>
    </div>
    <div class="footer">
        <p>&copy; 2024 Mugisha Learning Platform. All rights reserved.</p>
    </div>
</body>
</html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_certificate_earned(self, user_name: str, user_email: str, 
                              course_title: str, completion_date: str, certificate_code: str) -> bool:
        """Send certificate earned notification"""
        subject = f"🎉 Certificate Earned: {course_title}"
        
        body = f"""
Dear {user_name},

Congratulations! 🎉

You have successfully completed the course "{course_title}" and earned your certificate.

Certificate Details:
• Course: {course_title}
• Completion Date: {completion_date}
• Certificate Code: {certificate_code}

You can now download your certificate and share it with employers or add it to your professional profile.

To verify your certificate, visit our verification page and enter your certificate code.

Congratulations on your achievement!

Best regards,
The Mugisha Learning Platform Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #8b5cf6; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .certificate-info {{ background: #ede9fe; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
        .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #8b5cf6; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .emoji {{ font-size: 48px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Certificate Earned!</h1>
    </div>
    <div class="content">
        <div class="emoji">🎓</div>
        <p>Dear {user_name},</p>
        <p>Congratulations! 🎉</p>
        <p>You have successfully completed the course "<strong>{course_title}</strong>" and earned your certificate.</p>
        
        <div class="certificate-info">
            <h3>Certificate Details:</h3>
            <p><strong>Course:</strong> {course_title}</p>
            <p><strong>Completion Date:</strong> {completion_date}</p>
            <p><strong>Certificate Code:</strong> {certificate_code}</p>
        </div>
        
        <p>You can now download your certificate and share it with employers or add it to your professional profile.</p>
        
        <a href="http://localhost:3000/verify-certificate" class="button">Verify Certificate</a>
        
        <p>Congratulations on your achievement!</p>
        
        <p>Best regards,<br>The Mugisha Learning Platform Team</p>
    </div>
    <div class="footer">
        <p>&copy; 2024 Mugisha Learning Platform. All rights reserved.</p>
    </div>
</body>
</html>
        """
        
        return self.send_email(user_email, subject, body, html_body)

# Global email service instance
email_service = EmailService()
