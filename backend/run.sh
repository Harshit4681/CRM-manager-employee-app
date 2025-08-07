#!/bin/bash

# HackRx 6.0 Document Retrieval System - Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment
validate_env() {
    print_status "Validating environment..."
    
    # Check for required API keys
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY is not set"
        exit 1
    fi
    
    if [ -z "$PINECONE_API_KEY" ]; then
        print_error "PINECONE_API_KEY is not set"
        exit 1
    fi
    
    print_status "Environment validation passed"
}

# Function to install dependencies
install_deps() {
    print_status "Installing dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_status "Dependencies installed successfully"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if command_exists pytest; then
        pytest tests/ -v
    else
        print_error "pytest not found. Please install pytest first."
        exit 1
    fi
    
    print_status "Tests completed"
}

# Function to start the application
start_app() {
    print_status "Starting HackRx Document Retrieval System..."
    
    # Load environment variables if .env exists
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Start the FastAPI application
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to start with Docker
start_docker() {
    print_status "Starting with Docker..."
    
    if command_exists docker-compose; then
        docker-compose up -d
        print_status "Application started with Docker Compose"
        print_status "API available at: http://localhost:8000"
        print_status "Health check: http://localhost:8000/health"
        print_status "API docs: http://localhost:8000/docs"
    else
        print_error "docker-compose not found"
        exit 1
    fi
}

# Function to stop Docker services
stop_docker() {
    print_status "Stopping Docker services..."
    
    if command_exists docker-compose; then
        docker-compose down
        print_status "Docker services stopped"
    else
        print_error "docker-compose not found"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    if command_exists docker-compose; then
        docker-compose logs -f app
    else
        print_error "docker-compose not found"
        exit 1
    fi
}

# Function to run a quick test
quick_test() {
    print_status "Running quick API test..."
    
    # Wait for service to be ready
    sleep 5
    
    # Test health endpoint
    curl -f http://localhost:8000/health || {
        print_error "Health check failed"
        exit 1
    }
    
    print_status "Quick test passed"
}

# Function to show help
show_help() {
    echo "HackRx 6.0 Document Retrieval System"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install Python dependencies"
    echo "  test        Run tests"
    echo "  dev         Start development server"
    echo "  docker      Start with Docker Compose"
    echo "  stop        Stop Docker services"
    echo "  logs        Show application logs"
    echo "  validate    Validate environment"
    echo "  quick-test  Run a quick API test"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 dev"
    echo "  $0 docker"
    echo ""
    echo "For Docker deployment:"
    echo "  1. Copy .env.example to .env and configure"
    echo "  2. Run: $0 docker"
    echo "  3. Test: $0 quick-test"
}

# Main script logic
case "$1" in
    install)
        install_deps
        ;;
    test)
        run_tests
        ;;
    dev)
        validate_env
        start_app
        ;;
    docker)
        start_docker
        ;;
    stop)
        stop_docker
        ;;
    logs)
        show_logs
        ;;
    validate)
        validate_env
        ;;
    quick-test)
        quick_test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac