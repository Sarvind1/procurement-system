#!/bin/bash

# Procurement System - Troubleshooting Script

echo "🔧 Procurement System Troubleshooting"
echo "====================================="
echo ""

# Function to check service status
check_services() {
    echo "📊 Service Status:"
    echo "-----------------"
    docker-compose ps
    echo ""
}

# Function to test API health
test_api_health() {
    echo "🏥 Testing API Health:"
    echo "---------------------"
    response=$(curl -s -w "\n%{http_code}" http://localhost:8000/health 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo "✅ API is healthy!"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo "❌ API is not responding (HTTP $http_code)"
        echo "Response: $body"
    fi
    echo ""
}

# Function to check environment variables
check_env_vars() {
    echo "🔍 Checking Environment Variables:"
    echo "---------------------------------"
    
    if [ -f .env ]; then
        echo "✅ .env file found"
        echo ""
        echo "Key variables:"
        grep -E "^(DATABASE_URL|BACKEND_CORS_ORIGINS|ALLOWED_HOSTS|SECRET_KEY)=" .env | sed 's/SECRET_KEY=.*/SECRET_KEY=<hidden>/'
    else
        echo "❌ .env file not found!"
    fi
    echo ""
}

# Function to check database connection
check_database() {
    echo "🗄️  Testing Database Connection:"
    echo "-------------------------------"
    docker-compose exec -T postgres pg_isready -U postgres
    
    # Try to connect to the database
    docker-compose exec -T postgres psql -U postgres -c "\l" | grep procurement
    echo ""
}

# Function to check logs for errors
check_recent_errors() {
    echo "❌ Recent Errors (last 5 minutes):"
    echo "---------------------------------"
    docker-compose logs --since 5m 2>&1 | grep -E "(ERROR|CRITICAL|Failed|Exception)" | tail -20
    echo ""
}

# Function to test backend startup
test_backend_startup() {
    echo "🚀 Testing Backend Startup:"
    echo "--------------------------"
    
    # Get container logs
    docker-compose logs --tail=50 backend | grep -E "(Configuration loaded|Configuration Error|ERROR|WARNING)"
    echo ""
}

# Function to create test user
create_test_user() {
    echo "👤 Creating Test User:"
    echo "---------------------"
    
    # First check if API is running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "❌ API is not running. Please start it first."
        return
    fi
    
    # Try to create a test user
    response=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }')
    
    echo "Response: $response"
    echo ""
}

# Function to test login
test_login() {
    echo "🔐 Testing Login:"
    echo "----------------"
    
    # Test with default superuser
    echo "Testing with default superuser credentials..."
    response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin@procurement-system.com&password=changethis123")
    
    echo "Response: $response"
    echo ""
}

# Main diagnostics
echo "Running full diagnostics..."
echo ""

check_services
check_env_vars
test_api_health
check_database
test_backend_startup
check_recent_errors

# Interactive menu
while true; do
    echo ""
    echo "🔧 Additional Tests:"
    echo "1) Create test user"
    echo "2) Test login"
    echo "3) View backend logs (last 100 lines)"
    echo "4) Restart backend service"
    echo "5) Re-run diagnostics"
    echo "0) Exit"
    echo ""
    read -p "Select an option: " choice
    
    case $choice in
        1)
            create_test_user
            ;;
        2)
            test_login
            ;;
        3)
            docker-compose logs --tail=100 backend
            ;;
        4)
            echo "Restarting backend..."
            docker-compose restart backend
            sleep 5
            test_api_health
            ;;
        5)
            clear
            exec "$0"
            ;;
        0)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
done
