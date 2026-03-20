from models import CourseRating, User, Course, Enrollment
from database import db
from app import app
import random

def create_sample_ratings():
    with app.app_context():
        # Get sample data
        courses = Course.query.all()
        students = User.query.filter_by(role='student').all()
        
        if not courses or not students:
            print("Missing courses or students. Please run create_sample_data.py first.")
            return
        
        sample_reviews = [
            "Excellent course! Very well structured and easy to follow.",
            "Great content, but could use more practical examples.",
            "The instructor explains concepts very clearly. Highly recommend!",
            "Good course overall. Learned a lot of new things.",
            "Challenging but rewarding. The projects were very helpful.",
            "Perfect for beginners. Everything was explained step by step.",
            "Advanced topics were covered well. Great depth of knowledge.",
            "Could be improved with more interactive content.",
            "Outstanding course! Worth every penny.",
            "Good balance of theory and practice."
        ]
        
        for course in courses:
            # Get enrolled students for this course
            enrollments = Enrollment.query.filter_by(course_id=course.course_id).all()
            enrolled_students = [e.student for e in enrollments]
            
            # Create 2-4 ratings per course from enrolled students
            num_ratings = min(len(enrolled_students), random.randint(2, 4))
            
            for i in range(num_ratings):
                if i < len(enrolled_students):
                    student = enrolled_students[i]
                    
                    # Check if rating already exists
                    existing = CourseRating.query.filter_by(
                        course_id=course.course_id,
                        student_id=student.user_id
                    ).first()
                    
                    if not existing:
                        rating = CourseRating(
                            course_id=course.course_id,
                            student_id=student.user_id,
                            rating=random.randint(3, 5),  # Mostly positive ratings
                            review=random.choice(sample_reviews),
                            is_anonymous=random.choice([True, False])
                        )
                        db.session.add(rating)
        
        db.session.commit()
        
        print(f"Created sample ratings for {len(courses)} courses")
        
        # Display rating summary
        for course in courses:
            avg_rating = db.session.query(db.func.avg(CourseRating.rating)).filter_by(course_id=course.course_id).scalar() or 0
            total_ratings = CourseRating.query.filter_by(course_id=course.course_id).count()
            print(f"  {course.title}: {avg_rating:.1f}★ ({total_ratings} ratings)")

if __name__ == "__main__":
    create_sample_ratings()
