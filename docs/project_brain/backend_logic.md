# Backend Logic Documentation

## Table of Contents
1. [Configuration Management](#configuration-management)
2. [Authentication & Authorization](#authentication--authorization)
3. [Database Operations](#database-operations)
4. [API Structure](#api-structure)
5. [Error Handling](#error-handling)
6. [Logging & Monitoring](#logging--monitoring)

---

## Configuration Management

### Environment Variables Setup
The application uses Pydantic Settings for configuration management. All sensitive configuration is loaded from environment variables.

**Key Configuration Areas:**
1. **Application Settings**
   - `PROJECT_NAME`: Name of the application
   - `VERSION`: API version
   - `ENVIRONMENT`: Current environment (development/staging/production)
   - `DEBUG`: Debug mode flag

2. **Security Settings**
   - `SECRET_KEY`: JWT token signing key (auto-generated for development)
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime (default: 15 minutes)
   - `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime (default: 7 days)

3. **Database Configuration**
   - `DATABASE_URL`: PostgreSQL connection string
   - Default development URL: `postgresql://postgres:postgres@localhost:5432/procurement_db`
   - Automatic validation with helpful error messages

4. **External Services**
   - `REDIS_URL`: Redis connection for caching
   - `MINIO_*`: Object storage configuration
   - `SMTP_*`: Email service configuration

### Development Setup
1. Copy `.env.example` to `.env`
2. Update values as needed
3. The system provides sensible defaults for development

### Error Handling
- Missing environment variables show clear instructions
- Default values provided for development
- Production warnings for insecure defaults

---

## Authentication & Authorization

### JWT Token Flow
1. **Login Process**
   - User submits email/password
   - Credentials validated against database
   - Access token (15 min) + Refresh token (7 days) issued
   - Tokens stored in HTTP-only cookies

2. **Token Refresh**
   - Before access token expires, use refresh token
   - New access token issued
   - Maintains user session without re-login

3. **Authorization**
   - Role-based access control (RBAC)
   - Permissions checked on each API endpoint
   - Dependency injection for current user

### Security Features
- Password hashing with bcrypt
- Token rotation
- Session management
- Audit logging for security events

---

## Database Operations

### SQLAlchemy Setup
- Async SQLAlchemy for better performance
- Connection pooling configured
- Automatic retry on connection failures
- Query optimization with eager loading

### Migration Strategy
- Alembic for database migrations
- Auto-generated migrations from models
- Rollback capability
- Migration testing in CI/CD

### Transaction Management
- Unit of Work pattern
- Automatic rollback on errors
- Bulk operations support
- Optimistic locking for concurrency

---

## API Structure

### RESTful Design
- Resource-based URLs
- Standard HTTP methods
- Consistent response formats
- HATEOAS principles

### Request/Response Flow
1. Request validation with Pydantic
2. Business logic execution
3. Database operations
4. Response serialization
5. Error handling at each step

### Pagination
- Cursor-based pagination for large datasets
- Configurable page sizes
- Total count included in responses

---

## Error Handling

### Error Types
1. **Validation Errors** (422)
   - Field-level validation messages
   - Type checking
   - Business rule violations

2. **Authentication Errors** (401)
   - Invalid credentials
   - Expired tokens
   - Missing authentication

3. **Authorization Errors** (403)
   - Insufficient permissions
   - Resource access denied

4. **Not Found Errors** (404)
   - Resource doesn't exist
   - Soft-deleted resources

5. **Server Errors** (500)
   - Logged with full stack trace
   - User-friendly error messages
   - Automatic alerting in production

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "field": "field_name" // For validation errors
}
```

---

## Logging & Monitoring

### Structured Logging
- JSON format for machine parsing
- Correlation IDs for request tracking
- Performance metrics included
- Security events highlighted

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General application flow
- **WARNING**: Potential issues
- **ERROR**: Error conditions
- **CRITICAL**: System failures

### Monitoring Integration
- Prometheus metrics exposed
- Health check endpoints
- Performance tracking
- Resource usage monitoring

---

## Recent Updates

### 2025-06-16: Configuration Management Improvements
- **Issue**: Application failing to start due to missing environment variables
- **Solution**: 
  - Added development-friendly defaults
  - Improved error messages with setup instructions
  - Created `.env.example` file
  - Auto-generation of SECRET_KEY for development
- **Impact**: Easier onboarding for new developers
