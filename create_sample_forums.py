from models import DiscussionForum, ForumPost, User, Course, Enrollment
from database import db
from app import app

def create_sample_forums():
    with app.app_context():
        # Get sample data
        course = Course.query.first()
        instructor = User.query.filter_by(role='instructor').first()
        student = User.query.filter_by(role='student').first()
        
        if not course or not instructor:
            print("Missing course or instructor. Please run create_sample_data.py first.")
            return
        
        # Create a sample forum
        forum = DiscussionForum(
            course_id=course.course_id,
            title="General Discussion",
            description="A place for general course discussions and questions",
            created_by=instructor.user_id
        )
        db.session.add(forum)
        db.session.commit()
        
        # Create some sample posts
        post1 = ForumPost(
            forum_id=forum.forum_id,
            title="Welcome to the course!",
            content="Hello everyone! Welcome to this course. Feel free to ask any questions here.",
            created_by=instructor.user_id
        )
        db.session.add(post1)
        
        post2 = ForumPost(
            forum_id=forum.forum_id,
            title="Question about first lesson",
            content="I'm having trouble understanding the concepts from the first lesson. Can someone help?",
            created_by=student.user_id
        )
        db.session.add(post2)
        
        # Add a reply to the first post
        reply1 = ForumPost(
            forum_id=forum.forum_id,
            parent_post_id=post1.post_id,
            content="Thank you! Looking forward to learning with everyone.",
            created_by=student.user_id
        )
        db.session.add(reply1)
        
        db.session.commit()
        
        print(f"Created sample forum: {forum.title}")
        print(f"Created posts and replies for course: {course.title}")

if __name__ == "__main__":
    create_sample_forums()
