# Mugisha Learning Platform - Startup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- MySQL server running
- Git installed

### Step 1: Database Setup

1. **Start MySQL Server**
   ```bash
   # On Windows (using XAMPP/WAMP)
   # Start MySQL service from your control panel
   
   # On Linux/Mac
   sudo systemctl start mysql
   ```

2. **Create Database**
   ```bash
   mysql -u root -p < mugisha_database_schema.sql
   ```

3. **Update Environment Variables**
   Edit `.env` file in the project root:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=mugisha
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

### Step 2: Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Sample Data** (Optional)
   ```bash
   python create_sample_data.py
   ```
   
   *If Python command doesn't work, try:*
   ```bash
   py create_sample_data.py
   ```

3. **Start Backend Server**
   ```bash
   python app.py
   ```
   
   Backend will run on: `http://localhost:5000`

### Step 3: Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies**
   ```bash
   npm install
   ```

3. **Start Frontend Development Server**
   ```bash
   npm start
   ```
   
   Frontend will run on: `http://localhost:3000`

## 📱 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health

## 🔑 Default Login Credentials

If you created sample data, use these credentials:

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

### Instructor Accounts
- **Username**: `john_instructor` or `sarah_instructor`
- **Password**: `instructor123`

### Student Accounts
- **Username**: `alice_student`, `bob_student`, `charlie_student`, `diana_student`, `eve_student`
- **Password**: `student123`

## 🧪 Testing the API

Run the API test script:
```bash
python test_api.py
```

## 📁 Project Structure

```
mugisha-learning-platform/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── auth.py                # Authentication routes
├── api.py                 # API endpoints
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── create_sample_data.py   # Sample data generator
├── test_api.py           # API testing script
├── mugisha_database_schema.sql  # Database schema
└── frontend/             # React frontend
    ├── src/
    │   ├── components/   # React components
    │   ├── pages/        # Page components
    │   ├── context/      # React context
    │   ├── services/     # API services
    │   └── types/        # TypeScript types
    ├── package.json
    └── tailwind.config.js
```

## 🔧 Common Issues & Solutions

### 1. Python Not Found
- **Windows**: Install Python from python.org or Microsoft Store
- **Mac**: Use Homebrew: `brew install python`
- **Linux**: Use package manager: `sudo apt install python3`

### 2. MySQL Connection Issues
- Ensure MySQL server is running
- Check credentials in `.env` file
- Verify database name exists
- Check firewall settings

### 3. Port Already in Use
- **Backend**: Change port in `app.py` (line with `app.run`)
- **Frontend**: React will automatically find available port

### 4. CORS Issues
- Backend includes CORS middleware
- Ensure both servers are running
- Check proxy configuration in `frontend/package.json`

### 5. Node.js Issues
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

## 🚀 Features Available

### For Students
- Browse and enroll in courses
- Track learning progress
- Take exams and quizzes
- View certificates

### For Instructors
- Create and manage courses
- Add lessons and content
- Create exams and assessments
- Track student progress

### For Administrators
- User management
- System configuration
- Analytics and reporting
- Full platform access

## 📞 Support

If you encounter issues:

1. Check the console output for error messages
2. Verify all prerequisites are installed
3. Ensure database connection is working
4. Test API endpoints individually
5. Check network connectivity

## 🔄 Development Workflow

1. Make changes to backend code
2. Restart Flask server (`python app.py`)
3. Make changes to frontend code
4. React will auto-reload in browser
5. Test integration between frontend and backend

## 🌍 Production Deployment

For production deployment:

1. Set environment variables properly
2. Use a production database
3. Configure HTTPS
4. Set up proper logging
5. Use a production web server (Gunicorn/uWSGI)
6. Build React frontend (`npm run build`)
7. Configure reverse proxy (Nginx)

Happy coding! 🎓
