# 🚀 Mugisha Learning Platform - Deployment Guide

## 📋 Overview

This guide will help you deploy the Mugisha Learning Platform to production. The platform consists of:
- **Backend**: Flask API server with SQLite/MySQL database
- **Frontend**: React TypeScript application
- **File Storage**: Local file system (can be upgraded to cloud storage)

## 🛠️ Prerequisites

### System Requirements
- **Node.js**: 16.x or higher
- **Python**: 3.8 or higher
- **Database**: SQLite (default) or MySQL/PostgreSQL
- **Web Server**: Nginx (recommended) or Apache
- **SSL Certificate**: Let's Encrypt (recommended)

### Environment Variables
Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///mugisha_learning.db
# Or for MySQL:
# DATABASE_URL=mysql://username:password@localhost/mugisha_learning

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🗄️ Database Setup

### Option 1: SQLite (Default - Good for small deployments)
```bash
# Database is automatically created on first run
# No additional setup required
```

### Option 2: MySQL (Recommended for production)
```bash
# Install MySQL
sudo apt-get install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE mugisha_learning;
CREATE USER 'mugisha_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON mugisha_learning.* TO 'mugisha_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Update .env file
DATABASE_URL=mysql://mugisha_user:strong_password@localhost/mugisha_learning
```

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile for Backend
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads/assignments

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### 2. Create Dockerfile for Frontend
```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Create docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=sqlite:///mugisha_learning.db
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./uploads:/app/uploads
      - ./instance:/app/instance
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mugisha_learning
      MYSQL_USER: mugisha_user
      MYSQL_PASSWORD: userpassword
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

### 4. Deploy with Docker
```bash
# Build and start containers
docker-compose up -d --build

# Initialize database
docker-compose exec backend python create_sample_data.py

# Check logs
docker-compose logs -f
```

## 🌐 Traditional Deployment

### 1. Backend Deployment

#### Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
pip install gunicorn
```

#### Configure Gunicorn
```bash
# Create gunicorn config
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

#### Start Backend Service
```bash
# Using systemd (recommended)
sudo tee /etc/systemd/system/mugisha-api.service > /dev/null << EOF
[Unit]
Description=Mugisha Learning Platform API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/mugisha-learning
Environment="PATH=/path/to/mugisha-learning/venv/bin"
ExecStart=/path/to/mugisha-learning/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable mugisha-api
sudo systemctl start mugisha-api
```

### 2. Frontend Deployment

#### Build for Production
```bash
cd frontend
npm run build
```

#### Configure Nginx
```bash
# Install Nginx
sudo apt-get install nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/mugisha-learning > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Frontend
    location / {
        root /path/to/mugisha-learning/frontend/build;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # File uploads
    location /uploads/ {
        alias /path/to/mugisha-learning/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/mugisha-learning /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL Setup with Let's Encrypt
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Production Optimizations

### 1. Database Optimization
```bash
# For MySQL - Add indexes
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_assignments_course_id ON assignments(course_id);
CREATE INDEX idx_submissions_assignment_id ON assignment_submissions(assignment_id);
```

### 2. Caching Setup
```bash
# Install Redis for caching
sudo apt-get install redis-server

# Update Flask app to use Redis cache
pip install redis
```

### 3. Backup Strategy
```bash
# Create backup script
cat > backup.sh << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mugisha-learning"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup database
mysqldump -u mugisha_user -p mugisha_learning > \$BACKUP_DIR/db_\$DATE.sql

# Backup uploads
tar -czf \$BACKUP_DIR/uploads_\$DATE.tar.gz uploads/

# Clean old backups (keep 30 days)
find \$BACKUP_DIR -name "*.sql" -mtime +30 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## 📊 Monitoring & Logging

### 1. Application Logging
```bash
# Configure logging in app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/mugisha.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 2. System Monitoring
```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs

# Monitor application
sudo systemctl status mugisha-api
sudo journalctl -u mugisha-api -f
```

## 🔒 Security Considerations

### 1. Firewall Setup
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 5000  # Block direct backend access
```

### 2. Environment Security
```bash
# Secure .env file
chmod 600 .env

# Secure uploads directory
chmod 755 uploads
chmod 644 uploads/*
```

### 3. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip install --upgrade -r requirements.txt
```

## 🚀 Deployment Checklist

### Pre-deployment:
- [ ] Environment variables configured
- [ ] Database created and migrated
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules set
- [ ] Backup strategy implemented

### Post-deployment:
- [ ] Test all API endpoints
- [ ] Test file uploads
- [ ] Test email notifications
- [ ] Verify SSL certificate
- [ ] Check monitoring logs
- [ ] Performance testing

### Regular Maintenance:
- [ ] Update dependencies
- [ ] Monitor disk space
- [ ] Check backup integrity
- [ ] Review security logs
- [ ] Update SSL certificates

## 🆘 Troubleshooting

### Common Issues:

#### 1. Database Connection Errors
```bash
# Check database status
sudo systemctl status mysql

# Check connection string
echo $DATABASE_URL
```

#### 2. File Upload Issues
```bash
# Check permissions
ls -la uploads/
chmod 755 uploads/
```

#### 3. Nginx Configuration Issues
```bash
# Test Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew
```

## 📞 Support

For deployment issues:
1. Check logs: `sudo journalctl -u mugisha-api -f`
2. Verify configuration files
3. Test individual components
4. Check system resources

## 🎉 Success!

Your Mugisha Learning Platform is now deployed and ready for users! 🚀

### Next Steps:
1. Monitor performance
2. Gather user feedback
3. Plan feature updates
4. Scale as needed

**Congratulations on launching your learning platform!** 🎓✨
