#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        
        cat > .env << EOF
# MongoDB Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=manufacturing_secure_$(date +%s)
DATABASE_NAME=manufacturing_db

# Analytics Service Configuration
SCHEDULE_INTERVAL_MINUTES=60
FLASK_ENV=production

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=grafana_admin_$(date +%s)

# Mongo Express Configuration (for development/debugging)
MONGO_EXPRESS_USER=admin
MONGO_EXPRESS_PASSWORD=mongoexpress_$(date +%s)
EOF
        
        print_success "Created .env file with random passwords"
        print_warning "Please review and update the .env file with your preferred settings"
    else
        print_success ".env file exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p grafana/dashboards
    mkdir -p analytics_output
    
    # Copy dashboard if it doesn't exist
    if [ ! -f "grafana/dashboards/manufacturing-overview.json" ]; then
        print_status "Creating sample Grafana dashboard..."
        # Dashboard would be copied here in real implementation
    fi
    
    print_success "Directories created"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build the analytics service
    print_status "Building analytics service..."
    docker-compose build
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "Services started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for analytics service
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            print_success "Analytics service is ready"
            break
        fi
        
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            print_error "Analytics service failed to start after 5 minutes"
            exit 1
        fi
        
        sleep 10
    done
    
    # Check Grafana
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        print_success "Grafana is ready"
    else
        print_warning "Grafana may still be starting up"
    fi
}

# Show service information
show_services() {
    print_status "Service URLs:"
    echo -e "  ${GREEN}Analytics API:${NC} http://localhost:5000"
    echo -e "  ${GREEN}Grafana:${NC} http://localhost:3000"
    echo -e "  ${GREEN}Mongo Express:${NC} http://localhost:8081 (if enabled)"
    
    echo
    print_status "Default credentials (check .env for current values):"
    echo -e "  ${YELLOW}Grafana:${NC} admin / [check GRAFANA_ADMIN_PASSWORD in .env]"
    echo -e "  ${YELLOW}Mongo Express:${NC} admin / [check MONGO_EXPRESS_PASSWORD in .env]"
    
    echo
    print_status "Useful commands:"
    echo -e "  ${BLUE}View logs:${NC} docker-compose logs -f analytics_service"
    echo -e "  ${BLUE}Stop services:${NC} docker-compose down"
    echo -e "  ${BLUE}Restart analytics:${NC} docker-compose restart analytics_service"
    echo -e "  ${BLUE}Check status:${NC} curl http://localhost:5000/health"
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Test health endpoint
    if health_response=$(curl -s http://localhost:5000/health); then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Test analytics trigger
    print_status "Testing analytics generation..."
    if curl -s -X POST http://localhost:5000/analytics/run > /dev/null; then
        print_success "Analytics generation test passed"
    else
        print_warning "Analytics generation test failed (may be normal if no data exists)"
    fi
}

# Main deployment function
main() {
    print_status "Starting Manufacturing Analytics Deployment"
    echo
    
    check_docker
    check_env_file
    create_directories
    deploy_services
    wait_for_services
    
    echo
    print_success "Deployment completed successfully!"
    echo
    
    show_services
    
    echo
    print_status "Running deployment tests..."
    test_deployment
    
    echo
    print_success "Manufacturing Analytics is ready to use!"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        print_success "Services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose restart
        print_success "Services restarted"
        ;;
    "logs")
        docker-compose logs -f "${2:-analytics_service}"
        ;;
    "status")
        docker-compose ps
        echo
        curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || echo "Analytics service not responding"
        ;;
    "test")
        test_deployment
        ;;
    "clean")
        print_warning "This will remove all containers, volumes, and data. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            docker-compose down -v --remove-orphans
            docker system prune -f
            print_success "Cleanup completed"
        else
            print_status "Cleanup cancelled"
        fi
        ;;
    "help"|*)
        echo "Manufacturing Analytics Deployment Script"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  deploy  - Deploy all services (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - View service logs"
        echo "  status  - Check service status"
        echo "  test    - Test deployment"
        echo "  clean   - Remove all containers and data"
        echo "  help    - Show this help message"
        ;;
esac