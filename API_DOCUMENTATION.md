# 📚 Mugisha Learning Platform - API Documentation

## 🚀 **Base URL**
```
http://localhost:5000
```

## 🔐 **Authentication Endpoints**

### **Register User**
```http
POST /auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
}
```

### **Login**
```http
POST /auth/login
Content-Type: application/json

{
    "username": "john_doe",
    "password": "password123"
}
```

**Response:**
```json
{
    "token": "jwt_token_here",
    "user": {
        "user_id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "student"
    }
}
```

### **Logout**
```http
POST /auth/logout
Authorization: Bearer {token}
```

### **Get Profile**
```http
GET /auth/profile
Authorization: Bearer {token}
```

## 📚 **Course Management**

### **Get All Courses**
```http
GET /api/courses?page=1&per_page=10&category=programming&search=python
```

**Response:**
```json
{
    "courses": [
        {
            "course_id": 1,
            "title": "Python Programming",
            "description": "Learn Python from scratch",
            "instructor_id": 2,
            "instructor_name": "John Smith",
            "category": "programming",
            "difficulty_level": "beginner",
            "price": 49.99,
            "enrollment_count": 25
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 50,
        "pages": 5
    }
}
```

### **Get Single Course**
```http
GET /api/courses/1
```

### **Create Course** (Instructor/Admin)
```http
POST /api/courses
Authorization: Bearer {token}
Content-Type: application/json

{
    "course_code": "PYT101",
    "title": "Python Programming",
    "description": "Learn Python from scratch",
    "category": "programming",
    "difficulty_level": "beginner",
    "duration_hours": 40,
    "price": 49.99
}
```

## 📖 **Lesson Management**

### **Get Course Lessons**
```http
GET /api/courses/1/lessons
```

### **Get Single Lesson**
```http
GET /api/lessons/1
```

### **Create Lesson** (Instructor)
```http
POST /api/courses/1/lessons
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "Introduction to Python",
    "content": "Lesson content here...",
    "video_url": "https://example.com/video.mp4",
    "duration_minutes": 45,
    "lesson_order": 1,
    "is_published": true
}
```

## 📝 **Exam Management**

### **Get Course Exams**
```http
GET /api/courses/1/exams
```

### **Get Exam with Questions**
```http
GET /api/exams/1
```

**Response:**
```json
{
    "exam": {
        "exam_id": 1,
        "title": "Python Basics Quiz",
        "duration_minutes": 60,
        "passing_marks": 70,
        "max_attempts": 3,
        "questions": [
            {
                "question_id": 1,
                "question_text": "What is Python?",
                "question_type": "multiple_choice",
                "answer_options": [
                    {
                        "option_id": 1,
                        "option_text": "Programming language"
                    }
                ]
            }
        ]
    }
}
```

### **Create Exam** (Instructor)
```http
POST /api/courses/1/exams
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "Python Basics Quiz",
    "description": "Test your Python knowledge",
    "duration_minutes": 60,
    "passing_marks": 70,
    "max_attempts": 3
}
```

## 🎓 **Enrollment Management**

### **Enroll in Course**
```http
POST /api/courses/1/enroll
Authorization: Bearer {token}
```

### **Get Student Enrollments**
```http
GET /api/students/1/enrollments
Authorization: Bearer {token}
```

## 📋 **Exam Taking**

### **Start Exam Attempt**
```http
POST /api/exams/1/attempt
Authorization: Bearer {token}
```

### **Submit Exam Answers**
```http
POST /api/attempts/1/submit
Authorization: Bearer {token}
Content-Type: application/json

{
    "answers": [
        {
            "question_id": 1,
            "selected_option_id": 2,
            "is_correct": true,
            "marks_obtained": 20
        }
    ]
}
```

## 👥 **User Management** (Admin)

### **Get All Users**
```http
GET /api/users?page=1&per_page=10&search=john
Authorization: Bearer {token}
```

### **Get User Details**
```http
GET /api/users/1
Authorization: Bearer {token}
```

### **Update User**
```http
PUT /api/users/1
Authorization: Bearer {token}
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
}
```

## 📊 **Dashboard Data**

### **Get Dashboard Stats**
```http
GET /api/dashboard/stats
Authorization: Bearer {token}
```

**Admin Response:**
```json
{
    "stats": {
        "total_users": 150,
        "total_courses": 25,
        "total_enrollments": 500
    }
}
```

**Instructor Response:**
```json
{
    "stats": {
        "total_courses": 5,
        "total_students": 75,
        "courses": [...]
    }
}
```

**Student Response:**
```json
{
    "stats": {
        "total_enrollments": 8,
        "completed_courses": 3,
        "in_progress": 5,
        "enrollments": [...]
    }
}
```

## 🏆 **Certificate Management**

### **Generate Certificate**
```http
POST /certificates/generate/1
Authorization: Bearer {token}
```

### **Get Certificate**
```http
GET /certificates/1
Authorization: Bearer {token}
```

### **Verify Certificate**
```http
GET /certificates/verify/ABC123
```

### **Download Certificate**
```http
GET /certificates/download/1
Authorization: Bearer {token}
```

### **Get Student Certificates**
```http
GET /certificates/students/1/certificates
Authorization: Bearer {token}
```

## 📁 **File Upload**

### **Upload Course Thumbnail**
```http
POST /uploads/course-thumbnail
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [image file]
```

### **Upload Lesson Video**
```http
POST /uploads/lesson-video
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [video file]
```

### **Upload Profile Image**
```http
POST /uploads/profile-image
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [image file]
```

### **Get Uploaded File**
```http
GET /uploads/filename.jpg
```

### **List All Uploads** (Admin)
```http
GET /uploads
Authorization: Bearer {token}
```

## 🔍 **System Endpoints**

### **Health Check**
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "database": "connected"
}
```

### **API Info**
```http
GET /
```

## 🚨 **Error Responses**

All endpoints return consistent error format:

```json
{
    "error": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## 🔑 **Authentication**

Include JWT token in Authorization header:
```
Authorization: Bearer {your_jwt_token}
```

## 📝 **Notes**

- All timestamps are in ISO 8601 format
- Pagination starts from page 1
- File uploads limited to 16MB
- Supported image formats: PNG, JPG, JPEG, GIF
- Supported video formats: MP4, AVI, MOV
- All endpoints require authentication unless specified

## 🧪 **Test Data**

Use these credentials for testing:
- **Admin**: `admin / admin123`
- **Instructor**: `john_instructor / instructor123`
- **Student**: `alice_student / student123`

---

## 🎯 **API Usage Examples**

### **Complete Course Enrollment Flow:**
1. `POST /auth/login` - Get JWT token
2. `GET /api/courses` - Browse courses
3. `POST /api/courses/1/enroll` - Enroll in course
4. `GET /api/courses/1/lessons` - View lessons
5. `POST /api/exams/1/attempt` - Start exam
6. `POST /api/attempts/1/submit` - Submit exam
7. `POST /certificates/generate/1` - Get certificate

### **Instructor Course Creation Flow:**
1. `POST /auth/login` - Get JWT token
2. `POST /api/courses` - Create course
3. `POST /uploads/course-thumbnail` - Upload thumbnail
4. `POST /api/courses/1/lessons` - Add lessons
5. `POST /api/courses/1/exams` - Create exams

---

**🚀 Your Mugisha Learning Platform API is fully documented and ready for integration!**
