#!/usr/bin/env python3
"""
Script to create sample data for the Mugisha Learning Platform
"""

import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import User, Course, Enrollment, Lesson, Exam, Question, AnswerOption
from database import db
from app import app

def create_sample_data():
    """Create sample users, courses, lessons, and exams"""
    
    with app.app_context():
        print("Creating sample data...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("Database cleared and recreated.")
        
        # Create Users
        users = []
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@mugisha.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        users.append(admin)
        
        # Instructor users
        instructor1 = User(
            username='john_instructor',
            email='john@mugisha.com',
            password_hash=generate_password_hash('instructor123'),
            first_name='John',
            last_name='Smith',
            role='instructor',
            phone='+1234567890',
            is_active=True
        )
        users.append(instructor1)
        
        instructor2 = User(
            username='sarah_instructor',
            email='sarah@mugisha.com',
            password_hash=generate_password_hash('instructor123'),
            first_name='Sarah',
            last_name='Johnson',
            role='instructor',
            phone='+1234567891',
            is_active=True
        )
        users.append(instructor2)
        
        # Student users
        students_data = [
            {'username': 'alice_student', 'email': 'alice@mugisha.com', 'first_name': 'Alice', 'last_name': 'Wilson'},
            {'username': 'bob_student', 'email': 'bob@mugisha.com', 'first_name': 'Bob', 'last_name': 'Brown'},
            {'username': 'charlie_student', 'email': 'charlie@mugisha.com', 'first_name': 'Charlie', 'last_name': 'Davis'},
            {'username': 'diana_student', 'email': 'diana@mugisha.com', 'first_name': 'Diana', 'last_name': 'Miller'},
            {'username': 'eve_student', 'email': 'eve@mugisha.com', 'first_name': 'Eve', 'last_name': 'Garcia'},
        ]
        
        for student_data in students_data:
            student = User(
                username=student_data['username'],
                email=student_data['email'],
                password_hash=generate_password_hash('student123'),
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                role='student',
                is_active=True
            )
            users.append(student)
        
        # Save all users
        for user in users:
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Create Courses
        courses = []
        
        course1 = Course(
            course_code='WEB101',
            title='Introduction to Web Development',
            description='Learn the fundamentals of web development including HTML, CSS, and JavaScript. This comprehensive course covers everything you need to know to build modern, responsive websites from scratch.',
            instructor_id=instructor1.user_id,
            category='Programming',
            difficulty_level='beginner',
            duration_hours=40,
            price=99.99,
            is_active=True
        )
        courses.append(course1)
        
        course2 = Course(
            course_code='PYT201',
            title='Python Programming Masterclass',
            description='Master Python programming from basics to advanced concepts. Learn data structures, algorithms, object-oriented programming, and popular Python frameworks.',
            instructor_id=instructor2.user_id,
            category='Programming',
            difficulty_level='intermediate',
            duration_hours=60,
            price=149.99,
            is_active=True
        )
        courses.append(course2)
        
        course3 = Course(
            course_code='DBA301',
            title='Database Design and SQL',
            description='Learn database design principles and SQL programming. Master relational databases, normalization, indexing, and advanced query techniques.',
            instructor_id=instructor1.user_id,
            category='Data Science',
            difficulty_level='intermediate',
            duration_hours=45,
            price=129.99,
            is_active=True
        )
        courses.append(course3)
        
        course4 = Course(
            course_code='UIX401',
            title='User Experience Design Fundamentals',
            description='Discover the principles of user experience design. Learn user research, wireframing, prototyping, and usability testing.',
            instructor_id=instructor2.user_id,
            category='Design',
            difficulty_level='beginner',
            duration_hours=30,
            price=89.99,
            is_active=True
        )
        courses.append(course4)
        
        # Save all courses
        for course in courses:
            db.session.add(course)
        db.session.commit()
        print(f"Created {len(courses)} courses")
        
        # Create Lessons for Course 1 (Web Development)
        lessons_web = [
            {'title': 'Introduction to HTML', 'content': 'Learn the basics of HTML markup language...', 'lesson_order': 1, 'duration_minutes': 45},
            {'title': 'CSS Fundamentals', 'content': 'Master CSS styling and layout...', 'lesson_order': 2, 'duration_minutes': 60},
            {'title': 'JavaScript Basics', 'content': 'Introduction to JavaScript programming...', 'lesson_order': 3, 'duration_minutes': 90},
            {'title': 'Responsive Design', 'content': 'Create websites that work on all devices...', 'lesson_order': 4, 'duration_minutes': 75},
            {'title': 'Web Development Project', 'content': 'Build your first complete website...', 'lesson_order': 5, 'duration_minutes': 120},
        ]
        
        for lesson_data in lessons_web:
            lesson = Lesson(
                course_id=course1.course_id,
                title=lesson_data['title'],
                content=lesson_data['content'],
                lesson_order=lesson_data['lesson_order'],
                duration_minutes=lesson_data['duration_minutes'],
                is_published=True
            )
            db.session.add(lesson)
        
        # Create Lessons for Course 2 (Python)
        lessons_python = [
            {'title': 'Python Installation and Setup', 'content': 'Install Python and set up your development environment...', 'lesson_order': 1, 'duration_minutes': 30},
            {'title': 'Variables and Data Types', 'content': 'Understanding Python variables and data types...', 'lesson_order': 2, 'duration_minutes': 60},
            {'title': 'Control Flow', 'content': 'If statements, loops, and conditional logic...', 'lesson_order': 3, 'duration_minutes': 75},
            {'title': 'Functions and Modules', 'content': 'Creating reusable code with functions...', 'lesson_order': 4, 'duration_minutes': 90},
            {'title': 'Object-Oriented Programming', 'content': 'Classes, objects, and OOP principles...', 'lesson_order': 5, 'duration_minutes': 120},
        ]
        
        for lesson_data in lessons_python:
            lesson = Lesson(
                course_id=course2.course_id,
                title=lesson_data['title'],
                content=lesson_data['content'],
                lesson_order=lesson_data['lesson_order'],
                duration_minutes=lesson_data['duration_minutes'],
                is_published=True
            )
            db.session.add(lesson)
        
        db.session.commit()
        print("Created lessons")
        
        # Create Exams
        exams = []
        
        exam1 = Exam(
            course_id=course1.course_id,
            title='HTML & CSS Fundamentals Quiz',
            description='Test your knowledge of HTML and CSS basics',
            duration_minutes=60,
            total_marks=100,
            passing_marks=70,
            max_attempts=3,
            is_active=True
        )
        exams.append(exam1)
        
        exam2 = Exam(
            course_id=course2.course_id,
            title='Python Basics Assessment',
            description='Evaluate your understanding of Python fundamentals',
            duration_minutes=90,
            total_marks=100,
            passing_marks=75,
            max_attempts=3,
            is_active=True
        )
        exams.append(exam2)
        
        for exam in exams:
            db.session.add(exam)
        db.session.commit()
        print("Created exams")
        
        # Create Questions for Exam 1
        questions_exam1 = [
            {
                'question_text': 'What does HTML stand for?',
                'question_type': 'multiple_choice',
                'marks': 20,
                'question_order': 1,
                'options': [
                    {'text': 'Hyper Text Markup Language', 'is_correct': True},
                    {'text': 'High Tech Modern Language', 'is_correct': False},
                    {'text': 'Home Tool Markup Language', 'is_correct': False},
                    {'text': 'Hyperlinks and Text Markup Language', 'is_correct': False}
                ]
            },
            {
                'question_text': 'Which CSS property is used to change the text color?',
                'question_type': 'multiple_choice',
                'marks': 20,
                'question_order': 2,
                'options': [
                    {'text': 'text-color', 'is_correct': False},
                    {'text': 'font-color', 'is_correct': False},
                    {'text': 'color', 'is_correct': True},
                    {'text': 'text-style', 'is_correct': False}
                ]
            },
            {
                'question_text': 'HTML5 is the latest version of HTML.',
                'question_type': 'true_false',
                'marks': 15,
                'question_order': 3,
                'options': [
                    {'text': 'True', 'is_correct': True},
                    {'text': 'False', 'is_correct': False}
                ]
            },
            {
                'question_text': 'Describe the box model in CSS.',
                'question_type': 'short_answer',
                'marks': 25,
                'question_order': 4,
                'options': []
            },
            {
                'question_text': 'Explain the difference between inline and block elements.',
                'question_type': 'essay',
                'marks': 20,
                'question_order': 5,
                'options': []
            }
        ]
        
        for q_data in questions_exam1:
            question = Question(
                exam_id=exam1.exam_id,
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                marks=q_data['marks'],
                question_order=q_data['question_order']
            )
            db.session.add(question)
            db.session.flush()  # Get the question_id
            
            for opt_data in q_data['options']:
                option = AnswerOption(
                    question_id=question.question_id,
                    option_text=opt_data['text'],
                    is_correct=opt_data['is_correct'],
                    option_order=len([o for o in q_data['options'] if q_data['options'].index(o) <= q_data['options'].index(opt_data)]) + 1
                )
                db.session.add(option)
        
        # Create Questions for Exam 2
        questions_exam2 = [
            {
                'question_text': 'Which keyword is used to define a function in Python?',
                'question_type': 'multiple_choice',
                'marks': 25,
                'question_order': 1,
                'options': [
                    {'text': 'function', 'is_correct': False},
                    {'text': 'def', 'is_correct': True},
                    {'text': 'func', 'is_correct': False},
                    {'text': 'define', 'is_correct': False}
                ]
            },
            {
                'question_text': 'Python is a compiled language.',
                'question_type': 'true_false',
                'marks': 15,
                'question_order': 2,
                'options': [
                    {'text': 'True', 'is_correct': False},
                    {'text': 'False', 'is_correct': True}
                ]
            },
            {
                'question_text': 'What is a list comprehension in Python?',
                'question_type': 'short_answer',
                'marks': 30,
                'question_order': 3,
                'options': []
            },
            {
                'question_text': 'Explain the concept of inheritance in OOP.',
                'question_type': 'essay',
                'marks': 30,
                'question_order': 4,
                'options': []
            }
        ]
        
        for q_data in questions_exam2:
            question = Question(
                exam_id=exam2.exam_id,
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                marks=q_data['marks'],
                question_order=q_data['question_order']
            )
            db.session.add(question)
            db.session.flush()
            
            for opt_data in q_data['options']:
                option = AnswerOption(
                    question_id=question.question_id,
                    option_text=opt_data['text'],
                    is_correct=opt_data['is_correct'],
                    option_order=len([o for o in q_data['options'] if q_data['options'].index(o) <= q_data['options'].index(opt_data)]) + 1
                )
                db.session.add(option)
        
        db.session.commit()
        print("Created questions and answer options")
        
        # Create Enrollments
        students = [u for u in users if u.role == 'student']
        
        for student in students:
            # Enroll each student in 2-3 random courses
            import random
            num_enrollments = random.randint(2, 3)
            selected_courses = random.sample(courses, num_enrollments)
            
            for course in selected_courses:
                enrollment = Enrollment(
                    student_id=student.user_id,
                    course_id=course.course_id,
                    status='active',
                    completion_percentage=random.uniform(0, 100) if random.random() > 0.3 else 0
                )
                db.session.add(enrollment)
        
        db.session.commit()
        print("Created enrollments")
        
        print("\n" + "="*50)
        print("Sample data created successfully!")
        print("="*50)
        print("\nLogin Credentials:")
        print("Admin: admin / admin123")
        print("Instructor 1: john_instructor / instructor123")
        print("Instructor 2: sarah_instructor / instructor123")
        print("Students: alice_student, bob_student, charlie_student, diana_student, eve_student / student123")
        print("\nCourses created:")
        for course in courses:
            print(f"- {course.course_code}: {course.title}")
        print("="*50)

if __name__ == '__main__':
    create_sample_data()
