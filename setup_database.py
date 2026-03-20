#!/usr/bin/env python3
"""
Database Setup Script for Mugisha Learning Platform
This script creates the database and initializes it with sample data
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create database and tables"""
    try:
        # First connect without database to create it
        app = Flask(__name__)
        
        # Connect to MySQL server without specifying database
        db_uri = f"mysql+mysqlconnector://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db = SQLAlchemy(app)
        
        print("🔗 Connecting to MySQL server...")
        
        # Create database
        with app.app_context():
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'mugisha')} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
            print(f"✅ Database '{os.getenv('DB_NAME', 'mugisha')}' created successfully!")
        
        # Now connect to the specific database
        app.config['SQLALCHEMY_DATABASE_URI'] = f"{db_uri}/{os.getenv('DB_NAME', 'mugisha')}"
        
        # Import models and create tables
        from models import User, Course, Enrollment, Lesson, Exam, Question, AnswerOption, ExamAttempt, StudentAnswer
        
        with app.app_context():
            db.create_all()
            print("✅ All database tables created successfully!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Mugisha Learning Platform Database Setup")
    print("=" * 60)
    
    # Check if MySQL is available
    try:
        import mysql.connector
        print("✅ MySQL connector is available")
    except ImportError:
        print("❌ MySQL connector not found. Please install it:")
        print("   pip install mysql-connector-python")
        sys.exit(1)
    
    # Create database
    if create_database():
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Run: python create_sample_data.py")
        print("   2. Start backend: python app.py")
        print("   3. Access frontend: http://localhost:3000")
    else:
        print("\n❌ Database setup failed!")
        print("Please check your MySQL configuration in .env file")
        sys.exit(1)

if __name__ == '__main__':
    main()
