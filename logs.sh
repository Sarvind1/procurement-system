#!/bin/bash

# Procurement System - Log Viewer and Troubleshooting Script

echo "🔍 Procurement System Log Viewer"
echo "================================"
echo ""

# Function to show menu
show_menu() {
    echo "Select a service to view logs:"
    echo "1) Backend API logs"
    echo "2) Frontend logs"
    echo "3) PostgreSQL logs"
    echo "4) Redis logs"
    echo "5) All services logs"
    echo "6) Backend API logs (follow mode)"
    echo "7) Search for errors in all logs"
    echo "8) Show login-related logs"
    echo "9) Show request/response logs"
    echo "10) Export all logs to file"
    echo "0) Exit"
    echo ""
}

# Function to view backend logs with highlighting
view_backend_logs() {
    echo "📋 Backend API Logs (last 100 lines):"
    echo "------------------------------------"
    docker-compose logs --tail=100 backend | grep -E "(ERROR|WARNING|Login|request|response)" --color=always
}

# Function to follow backend logs
follow_backend_logs() {
    echo "📋 Following Backend API Logs (Ctrl+C to stop):"
    echo "----------------------------------------------"
    docker-compose logs -f backend | grep -E "(ERROR|WARNING|Login|request|response|INFO)" --color=always
}

# Function to view frontend logs
view_frontend_logs() {
    echo "🎨 Frontend Logs (last 50 lines):"
    echo "--------------------------------"
    docker-compose logs --tail=50 frontend
}

# Function to view PostgreSQL logs
view_postgres_logs() {
    echo "🗄️  PostgreSQL Logs (last 50 lines):"
    echo "-----------------------------------"
    docker-compose logs --tail=50 postgres
}

# Function to view Redis logs
view_redis_logs() {
    echo "💾 Redis Logs (last 50 lines):"
    echo "-----------------------------"
    docker-compose logs --tail=50 redis
}

# Function to view all logs
view_all_logs() {
    echo "📊 All Services Logs (last 50 lines each):"
    echo "-----------------------------------------"
    docker-compose logs --tail=50
}

# Function to search for errors
search_errors() {
    echo "❌ Searching for errors in all logs:"
    echo "-----------------------------------"
    docker-compose logs | grep -E "(ERROR|CRITICAL|Failed|Exception|Traceback)" --color=always
}

# Function to show login-related logs
show_login_logs() {
    echo "🔐 Login-related logs:"
    echo "---------------------"
    docker-compose logs backend | grep -E "(login|Login|authentication|Authentication|password|token)" --color=always
}

# Function to show request/response logs
show_request_logs() {
    echo "🌐 Request/Response logs:"
    echo "------------------------"
    docker-compose logs backend | grep -E "(Incoming request|Outgoing response|Request ID)" --color=always
}

# Function to export logs
export_logs() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    filename="procurement_logs_${timestamp}.txt"
    echo "💾 Exporting all logs to ${filename}..."
    docker-compose logs > "${filename}"
    echo "✅ Logs exported to ${filename}"
}

# Function to check service health
check_health() {
    echo "🏥 Service Health Check:"
    echo "-----------------------"
    
    # Check if services are running
    echo "Container Status:"
    docker-compose ps
    
    echo ""
    echo "API Health Check:"
    curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API is not responding"
    
    echo ""
    echo "Database Connection Test:"
    docker-compose exec postgres pg_isready -U postgres || echo "❌ Database is not ready"
}

# Main loop
while true; do
    echo ""
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            view_backend_logs
            ;;
        2)
            view_frontend_logs
            ;;
        3)
            view_postgres_logs
            ;;
        4)
            view_redis_logs
            ;;
        5)
            view_all_logs
            ;;
        6)
            follow_backend_logs
            ;;
        7)
            search_errors
            ;;
        8)
            show_login_logs
            ;;
        9)
            show_request_logs
            ;;
        10)
            export_logs
            ;;
        0)
            echo "👋 Exiting log viewer..."
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
