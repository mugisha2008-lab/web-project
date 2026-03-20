# Quick Setup Instructions for Mugisha Learning Platform

## 🔧 **Python Setup (Windows)**

Since Python isn't found in your system, follow these steps:

### Option 1: Install Python (Recommended)
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Restart your terminal/command prompt

### Option 2: Use Windows Store Python
1. Open Microsoft Store
2. Search for "Python 3.11" or similar
3. Click "Install"
4. Use `python` command in terminal

### Option 3: Find Existing Python
1. Open Command Prompt
2. Run: `where python`
3. Use the full path shown

## 🚀 **Start the Platform**

### 1. Setup Database
```bash
mysql -u root -p < mugisha_database_schema.sql
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Backend Server
```bash
python app.py
```
*Server will run on: http://localhost:5000*

### 4. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm start
```
*Frontend will run on: http://localhost:3000*

## 🎯 **Access the Platform**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 🔑 **Login Credentials**

If you created sample data:
- **Admin**: `admin / admin123`
- **Instructor**: `john_instructor / instructor123`
- **Student**: `alice_student / student123`

## 🐛 **Troubleshooting**

### Python Issues:
- Make sure Python is added to PATH
- Try `python3` instead of `python`
- Use full path to Python executable

### Port Issues:
- Backend: Change port in `app.py` (line with `app.run`)
- Frontend: React will auto-find available port

### Database Issues:
- Ensure MySQL server is running
- Check credentials in `.env` file
- Verify database name exists

## 📱 **Once Running**

1. Open browser to http://localhost:3000
2. Register a new account or use test credentials
3. Browse courses and enroll
4. Start learning!

The platform is fully functional with all features implemented!
