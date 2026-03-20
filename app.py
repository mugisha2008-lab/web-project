from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database configuration
from database import init_db, db, login_manager

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
# Use SQLite for development (switch to MySQL when available)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mugisha_learning.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Configure CORS to allow frontend requests
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

# Import models after database initialization
from models import User, Course, Enrollment, Lesson, Exam, Question, DiscussionForum, ForumPost, Notification, CourseRating, Assignment, AssignmentSubmission

# Import routes
from auth import auth_bp
from api import api_bp
from certificates import cert_bp
from uploads import upload_bp
from forums import forums_bp
from admin_api import admin_bp
from assignments import assignments_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(cert_bp, url_prefix='/certificates')
app.register_blueprint(upload_bp, url_prefix='/uploads')
app.register_blueprint(forums_bp, url_prefix='/api/forums')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(assignments_bp, url_prefix='/api/assignments')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Basic routes
@app.route('/')
def index():
    return jsonify({'message': 'Mugisha Learning Platform API', 'version': '1.0.0'})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'database': 'connected' if db.engine else 'disconnected'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
