from models import Assignment, User, Course
from database import db
from app import app
from datetime import datetime, timedelta

def create_sample_assignments():
    with app.app_context():
        # Get sample data
        courses = Course.query.all()
        instructors = User.query.filter_by(role='instructor').all()
        
        if not courses or not instructors:
            print("Missing courses or instructors. Please run create_sample_data.py first.")
            return
        
        sample_assignments = [
            {
                'title': 'Build a Personal Portfolio Website',
                'description': 'Create a responsive personal portfolio website using HTML, CSS, and JavaScript. The website should showcase your skills, projects, and contact information.',
                'instructions': '1. Design a modern, clean layout\n2. Include at least 3 different sections\n3. Make it fully responsive\n4. Add smooth scrolling and animations\n5. Include a contact form',
                'max_score': 100,
                'due_date': datetime.utcnow() + timedelta(days=7)
            },
            {
                'title': 'JavaScript Functions and Arrays',
                'description': 'Complete a series of JavaScript exercises focusing on functions, arrays, and basic algorithms.',
                'instructions': 'Complete all exercises in the provided worksheet. Focus on understanding array methods and function composition.',
                'max_score': 50,
                'due_date': datetime.utcnow() + timedelta(days=5)
            },
            {
                'title': 'Database Design Project',
                'description': 'Design a complete database schema for a small e-commerce application.',
                'instructions': 'Create ER diagrams, write SQL queries, and document your design decisions.',
                'max_score': 150,
                'due_date': datetime.utcnow() + timedelta(days=14)
            },
            {
                'title': 'UI/UX Case Study',
                'description': 'Analyze an existing mobile app and propose improvements to its user interface and experience.',
                'instructions': '1. Choose a mobile app\n2. Analyze its current UI/UX\n3. Identify pain points\n4. Create wireframes for improvements\n5. Present your findings',
                'max_score': 80,
                'due_date': datetime.utcnow() + timedelta(days=10)
            }
        ]
        
        for course in courses:
            instructor = next((i for i in instructors if i.user_id == course.instructor_id), instructors[0])
            
            # Create 2-3 assignments per course
            for i, assignment_data in enumerate(sample_assignments[:2]):
                assignment = Assignment(
                    course_id=course.course_id,
                    title=assignment_data['title'],
                    description=assignment_data['description'],
                    instructions=assignment_data['instructions'],
                    max_score=assignment_data['max_score'],
                    due_date=assignment_data['due_date'],
                    created_by=instructor.user_id,
                    is_published=True
                )
                db.session.add(assignment)
        
        db.session.commit()
        
        print(f"Created sample assignments for {len(courses)} courses")
        
        # Display assignment summary
        for course in courses:
            assignment_count = Assignment.query.filter_by(course_id=course.course_id).count()
            print(f"  {course.title}: {assignment_count} assignments")

if __name__ == "__main__":
    create_sample_assignments()
