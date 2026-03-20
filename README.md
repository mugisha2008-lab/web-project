# Mugisha Online Learning Platform

A comprehensive online learning management system built with Flask and MySQL.

## Features

- **Multi-role User Management**: Students, Instructors, and Admins
- **Course Management**: Create, update, and manage courses
- **Enrollment System**: Student enrollment and progress tracking
- **Lesson Management**: Video and text-based lessons
- **Exam System**: Multiple question types with automated grading
- **Progress Tracking**: Monitor student learning progress
- **Certificate Generation**: Issue certificates upon course completion
- **Discussion Forums**: Course-specific discussions
- **Notification System**: Keep users informed

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: MySQL
- **Authentication**: JWT tokens
- **API**: RESTful API design

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mugisha-learning-platform
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/MacOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env` file and update with your database credentials
   - Set your MySQL connection details
   - Generate secure secret keys

5. **Set up database**
   ```bash
   mysql -u root -p < mugisha_database_schema.sql
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile
- `POST /auth/change-password` - Change password
- `POST /auth/verify-token` - Verify JWT token

### Courses
- `GET /api/courses` - Get all courses (with pagination)
- `GET /api/courses/<id>` - Get specific course
- `POST /api/courses` - Create new course (Instructor/Admin only)
- `PUT /api/courses/<id>` - Update course (Instructor/Admin only)

### Enrollments
- `POST /api/enrollments` - Enroll in course (Students only)
- `GET /api/enrollments` - Get user enrollments

### Lessons
- `GET /api/courses/<id>/lessons` - Get course lessons
- `POST /api/courses/<id>/lessons` - Create lesson (Instructor/Admin only)

### Exams
- `GET /api/courses/<id>/exams` - Get course exams
- `GET /api/exams/<id>` - Get specific exam
- `POST /api/exams/<id>/attempt` - Start exam attempt
- `POST /api/attempts/<id>/submit` - Submit exam attempt

### Users (Admin only)
- `GET /api/users` - Get all users

## Database Schema

The platform uses 16 main tables:

1. **users** - User accounts and roles
2. **courses** - Course information
3. **enrollments** - Student enrollments
4. **lessons** - Course lessons
5. **exams** - Exam information
6. **questions** - Exam questions
7. **answer_options** - Multiple choice options
8. **exam_attempts** - Student exam attempts
9. **student_answers** - Student responses
10. **progress_tracking** - Lesson progress
11. **certificates** - Issued certificates
12. **notifications** - System notifications
13. **course_materials** - Additional resources
14. **discussion_forums** - Course forums
15. **forum_posts** - Forum posts and replies
16. **system_settings** - Platform configuration

## User Roles

- **Student**: Can enroll in courses, take exams, track progress
- **Instructor**: Can create/manage courses, lessons, exams
- **Admin**: Full system access, user management

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Input validation and sanitization
- SQL injection protection through SQLAlchemy

## Development

To run in development mode:
```bash
set FLASK_ENV=development
set FLASK_DEBUG=True
python app.py
```

## Testing

Run tests with:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
