# Logging and Troubleshooting Guide

## Overview
The Procurement System includes comprehensive logging at multiple levels to help identify and troubleshoot issues quickly.

## Logging Features

### 1. Request/Response Logging
Every API request and response is logged with:
- Unique Request ID for tracking
- HTTP method and path
- Client IP address
- Request/response headers
- Processing time
- Status codes
- Error details (if any)

### 2. Authentication Logging
All authentication events are logged:
- Login attempts (successful and failed)
- Registration events
- Token refresh operations
- Password change attempts
- Logout events
- Failed authentication reasons

### 3. Database Operation Logging
- Query execution times
- Connection pool status
- Failed queries with error details
- Transaction boundaries

### 4. Error Logging
- Full stack traces for exceptions
- Context information (user, endpoint, parameters)
- Request IDs for correlation
- Error categorization

## Viewing Logs

### Using the Log Viewer Script
We provide a convenient script to view and analyze logs:

```bash
# Make the script executable
chmod +x logs.sh

# Run the log viewer
./logs.sh
```

The script provides options to:
1. View backend API logs
2. View frontend logs
3. View database logs
4. Search for errors
5. View login-related logs
6. View request/response logs
7. Export logs to a file

### Using Docker Compose Commands

View all logs:
```bash
docker-compose logs
```

View specific service logs:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

Follow logs in real-time:
```bash
docker-compose logs -f backend
```

View last N lines:
```bash
docker-compose logs --tail=100 backend
```

### Filtering Logs

Find all errors:
```bash
docker-compose logs | grep ERROR
```

Find login-related issues:
```bash
docker-compose logs backend | grep -i login
```

Find specific request ID:
```bash
docker-compose logs backend | grep "ID: abc123"
```

## Log Levels

The system uses the following log levels:

- **DEBUG**: Detailed information for debugging (includes request bodies)
- **INFO**: General operational information
- **WARNING**: Warning messages (failed login attempts, etc.)
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Severe errors that might stop the application

## Common Issues and Troubleshooting

### Login Issues

1. **Check authentication logs:**
   ```bash
   docker-compose logs backend | grep -E "(login|authentication)"
   ```

2. **Common login errors:**
   - "Incorrect email or password" - Invalid credentials
   - "Inactive user" - User account is disabled
   - "User not found" - Email doesn't exist in database

3. **Debug steps:**
   - Verify database is running: `docker-compose ps postgres`
   - Check if user exists in database
   - Verify password is being hashed correctly
   - Check CORS settings if frontend can't connect

### Database Connection Issues

1. **Check PostgreSQL logs:**
   ```bash
   docker-compose logs postgres
   ```

2. **Test database connection:**
   ```bash
   docker-compose exec postgres pg_isready
   ```

3. **Common issues:**
   - Database not initialized
   - Wrong connection string
   - PostgreSQL not fully started

### CORS Issues

1. **Check CORS configuration:**
   ```bash
   docker-compose logs backend | grep CORS
   ```

2. **Verify allowed origins in .env:**
   ```
   BACKEND_CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
   ```

### Request Tracking

Every request gets a unique ID that appears in all related logs:

```
Incoming request - ID: 123e4567-e89b-12d3-a456-426614174000
Login attempt from IP 127.0.0.1 for username: admin@example.com
Outgoing response - ID: 123e4567-e89b-12d3-a456-426614174000 - Status: 200
```

Use this ID to track a request through the entire system.

## Performance Monitoring

### Request Performance
Each response includes timing headers:
- `X-Request-ID`: Unique request identifier
- `X-Process-Time`: Time taken to process request

### Slow Query Detection
Database queries taking longer than 100ms are logged as warnings.

### Health Check Endpoint
Monitor system health at: http://localhost:8000/health

Returns:
```json
{
  "status": "healthy",
  "service": "procurement-backend",
  "version": "1.0.0",
  "environment": "development",
  "database": "healthy"
}
```

## Log Storage and Rotation

- Logs are stored in Docker containers
- Each service has a 10MB log size limit
- Logs rotate after reaching the limit (keeps last 3-5 files)
- In production, consider using centralized logging (ELK stack, CloudWatch, etc.)

## Security Considerations

- Sensitive data (passwords, tokens) are never logged
- Request bodies are only logged in DEBUG mode
- Production logs exclude detailed error messages
- User IDs are logged instead of personal information

## Best Practices

1. **Always check logs when debugging**
2. **Use request IDs to correlate events**
3. **Monitor error rates and response times**
4. **Set up alerts for critical errors**
5. **Regularly review authentication logs for security**
6. **Export and archive logs periodically**

## Advanced Debugging

### Enable SQL Query Logging
Set in .env:
```
LOG_LEVEL=DEBUG
```

### View Raw JSON Logs
```bash
docker-compose logs --no-color backend | jq '.'
```

### Real-time Error Monitoring
```bash
docker-compose logs -f backend | grep -E "(ERROR|CRITICAL)"
```

### Export Logs for Analysis
```bash
# Export last hour of logs
docker-compose logs --since 1h > logs_export.txt

# Export specific time range
docker-compose logs --since 2024-01-01T10:00:00 --until 2024-01-01T11:00:00 > time_range_logs.txt
```
