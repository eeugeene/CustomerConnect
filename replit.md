# Mini Flask CRM System

## Overview

This is a lightweight Customer Relationship Management (CRM) system built with Flask. The application provides basic customer management functionality with a simple web interface for adding, viewing, editing, and deleting customer records. It includes an admin authentication system for protected operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite as the default database
- **Authentication**: Session-based authentication for admin users
- **Security**: CSRF protection using Flask-WTF
- **Forms**: WTForms for form handling and validation

### Frontend Architecture
- **Templates**: Jinja2 templating engine with Bootstrap 5 for styling
- **Theme**: Dark theme using Bootstrap Agent Dark Theme
- **Icons**: Font Awesome 6.0 for UI icons
- **Responsive Design**: Bootstrap responsive grid system

### Database Schema
- **Customer Model**: Stores customer information (name, email, phone, created_at)
- **Admin Model**: Stores admin user credentials with password hashing

## Key Components

### Application Structure
- **app.py**: Application factory and configuration setup
- **models.py**: Database models for Customer and Admin entities
- **views.py**: Route handlers and business logic
- **forms.py**: Form classes with validation rules
- **main.py**: Application entry point
- **templates/**: HTML templates for the user interface

### Core Features
1. **Customer Management**: CRUD operations for customer records
2. **Admin Authentication**: Login/logout system for administrative access
3. **Search Functionality**: Search customers by name, email, or phone
4. **Form Validation**: Server-side validation with user-friendly error messages
5. **CSRF Protection**: Security against cross-site request forgery attacks

## Data Flow

### Customer Operations
1. User accesses customer list or forms through public routes
2. Forms are validated using WTForms validators
3. Data is persisted to SQLite database via SQLAlchemy ORM
4. Success/error messages are displayed using Flask flash messages

### Admin Operations
1. Admin logs in through dedicated login form
2. Session-based authentication tracks admin status
3. Admin can access protected dashboard and management features
4. Logout clears session data

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation library
- **Werkzeug**: WSGI utilities and password hashing

### Frontend Dependencies
- **Bootstrap 5**: CSS framework (CDN)
- **Font Awesome 6.0**: Icon library (CDN)
- **Bootstrap Agent Dark Theme**: Custom dark theme (CDN)

## Deployment Strategy

### Environment Configuration
- **Database**: Configurable via `DATABASE_URL` environment variable (defaults to SQLite)
- **Secret Key**: Configurable via `SESSION_SECRET` environment variable
- **Development Mode**: Debug mode enabled for development

### Database Initialization
- Automatic table creation on application startup
- Default admin user creation (username: 'admin', password: 'admin123')
- Database connection pooling with automatic reconnection

### Security Considerations
- Password hashing using Werkzeug's security utilities
- CSRF token validation on all forms
- Session-based authentication for admin access
- Proxy fix middleware for deployment behind reverse proxies

### Scalability Notes
- SQLite is suitable for development and small deployments
- Database URL configuration allows easy migration to PostgreSQL or other databases
- Connection pooling configured for better performance
- Logging configured for debugging and monitoring