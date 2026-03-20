#!/bin/bash

# 🚀 Mugisha Learning Platform - Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

echo "🎓 Mugisha Learning Platform - Deployment Script"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p uploads/assignments
    mkdir -p instance
    mkdir -p logs
    mkdir -p nginx/ssl
    mkdir -p nginx/logs
    mkdir -p mysql/init
    
    # Set permissions
    chmod 755 uploads
    chmod 755 instance
    chmod 755 logs
    chmod 755 nginx
    
    print_success "Directories created and permissions set"
}

# Check environment variables
check_env() {
    print_status "Checking environment variables..."
    
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating a template..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///instance/mugisha_learning.db

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# CORS Configuration
CORS_ORIGINS=http://localhost,http://localhost:3000,https://yourdomain.com

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
EOF
        print_warning "Please edit .env file with your production values before continuing."
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    print_success "Environment variables checked"
}

# Build and start containers
deploy_containers() {
    print_status "Building and starting containers..."
    
    # Stop any existing containers
    docker-compose down
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run database initialization
    docker-compose exec backend python setup_database.py
    
    # Create sample data (optional)
    read -p "Do you want to create sample data? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creating sample data..."
        docker-compose exec backend python create_sample_data.py
        docker-compose exec backend python create_sample_forums.py
        docker-compose exec backend python create_sample_ratings.py
        docker-compose exec backend python create_sample_assignments.py
        print_success "Sample data created"
    fi
}

# Setup SSL certificates (Let's Encrypt)
setup_ssl() {
    read -p "Do you want to setup SSL certificates? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setting up SSL certificates..."
        
        # Install certbot
        if command -v certbot &> /dev/null; then
            print_status "Certbot is already installed"
        else
            print_status "Installing Certbot..."
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        fi
        
        # Get domain from user
        read -p "Enter your domain name: " domain
        if [ -n "$domain" ]; then
            print_status "Obtaining SSL certificate for $domain..."
            sudo certbot --nginx -d $domain --non-interactive --agree-tos --email admin@$domain
            print_success "SSL certificate obtained for $domain"
        fi
    fi
}

# Setup backup script
setup_backup() {
    print_status "Setting up backup script..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mugisha-learning"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db mysqldump -u mugisha_user -puserpassword123 mugisha_learning > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env docker-compose.yml nginx/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x backup.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/backup.sh") | crontab -
    
    print_success "Backup script setup completed"
}

# Final checks
final_checks() {
    print_status "Performing final checks..."
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "All services are running"
    else
        print_error "Some services are not running"
        docker-compose ps
        exit 1
    fi
    
    # Test API health
    if curl -f http://localhost:5000/health &> /dev/null; then
        print_success "Backend API is healthy"
    else
        print_warning "Backend API health check failed"
    fi
    
    # Test frontend
    if curl -f http://localhost/ &> /dev/null; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend health check failed"
    fi
}

# Show deployment summary
show_summary() {
    print_success "Deployment completed successfully!"
    echo ""
    echo "🎓 Mugisha Learning Platform is now running!"
    echo ""
    echo "📊 Services:"
    echo "  • Frontend: http://localhost"
    echo "  • Backend API: http://localhost:5000"
    echo "  • Database: MySQL on port 3306"
    echo "  • Redis: Port 6379"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Update containers: docker-compose pull && docker-compose up -d"
    echo ""
    echo "📱 Access Information:"
    echo "  • Admin: admin / admin123"
    echo "  • Instructor: instructor / instructor123"
    echo "  • Student: student / student123"
    echo ""
    echo "🔒 Security:"
    echo "  • Change default passwords in production"
    echo "  • Update .env file with your values"
    echo "  • Setup SSL certificates for production"
    echo ""
    echo "📞 For support, check the logs or run: docker-compose logs"
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    echo ""
    
    check_docker
    create_directories
    check_env
    deploy_containers
    init_database
    setup_ssl
    setup_backup
    final_checks
    show_summary
}

# Run main function
main
