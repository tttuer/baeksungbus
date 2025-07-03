# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based web application for 백성운수 (Baeksung Bus Company) providing bus schedule information, notices, Q&A functionality, and administrative features. The application uses MySQL as the database and includes both API endpoints and web interface.

## Architecture

### Tech Stack
- **Backend**: FastAPI with SQLModel/SQLAlchemy for ORM
- **Database**: MySQL 8 (containerized with Docker)
- **Authentication**: JWT tokens with session middleware
- **Frontend**: Server-side rendered HTML templates with Jinja2
- **Static Files**: CSS, JavaScript, and images served from `/static`

### Key Components

1. **Models** (`/models/`): SQLModel classes defining database schemas
   - `users.py`: User authentication and token models
   - `notice.py`: Notice/announcement system with file attachments and types (TIME, TTOCK, NOTICE)
   - `bus_schedule.py`: Bus schedule with image storage capabilities
   - `qa.py`: Q&A system with email notifications
   - `ddock.py`: Location/stop information
   - `answers.py`: Admin responses to Q&A items

2. **Routes** (`/routes/`): API endpoints organized by feature
   - All API routes prefixed with `/api` except pages and captcha
   - `pages.py`: Frontend template rendering (no `/api` prefix)
   - `users.py`: Authentication endpoints (`/api/users`)
   - `notices.py`: Notice CRUD operations (`/api/notices`)
   - `bus_schedules.py`: Schedule management (`/api/schedules`)
   - `qas.py`: Q&A system (`/api/qas`)
   - `ddocks.py`: Location management (`/api/ddocks`)
   - `captcha_route.py`: CAPTCHA generation

3. **Authentication** (`/auth/`):
   - JWT-based authentication with session storage
   - Admin middleware protecting `/adm/*` routes (except `/adm/login`)
   - Admin user: `bsbus`

4. **Database Connection** (`/database/connection.py`):
   - MySQL connection via SQLModel/SQLAlchemy
   - Connection string uses environment variables from `utils/settings.py`

## Development Commands

### Local Development
```bash
# Run the application locally
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Development
```bash
# Start MySQL database
docker-compose up -d

# Build and run application container
docker build -t baeksungbus .
docker run -p 8000:8000 baeksungbus
```

### Database Setup
The MySQL database is configured through `docker-compose.yml`:
- Database: `baeksung`
- User: `test_user` / Password: `test_password`
- Port: `3306`
- Initialization script: `init.sql`

## Environment Configuration

Required environment variables (configured in `.env`):
- `KAKAO_API_KEY`: For map/location services
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password  
- `MIDDLEWARE_SECRET`: Session middleware secret key

Settings are managed through `utils/settings.py` using Pydantic BaseSettings.

## Key Patterns

### Database Models
- All models extend `SQLModel` with `table=True` for database tables
- Use `Field(primary_key=True, default=None)` for auto-incrementing IDs
- Binary data (images, attachments) stored as `Optional[bytes]`
- Enums defined as Python Enum classes (e.g., `NoticeType`)

### API Structure
- API routes grouped by feature with consistent prefixing
- Request/response models separate from database models
- File uploads handled through FastAPI's `UploadFile`
- Base64 encoding for binary data in API responses

### Authentication Flow
- JWT tokens stored in browser sessions
- Admin routes protected by `AuthMiddleware`
- Token verification through `auth/jwt_handler.py`
- Admin check function: `check_admin('bsbus')`

### Template Rendering
- Jinja2 templates in `/templates/` directory
- Admin templates in `/templates/admin/`
- Base templates with header/footer/sidebar components
- Static assets served from `/static/`

## File Upload Handling

The application handles multiple types of file uploads:
- **Notice attachments**: Stored as bytes in database with filename
- **Bus schedule images**: Up to 3 images per schedule (image_data1/2/3)
- **Q&A attachments**: File upload with email functionality

## Database Schema Notes

- Tables use snake_case naming (e.g., `bus_schedule`, `notice`)
- Foreign key relationships minimal, mostly independent entities
- File data stored directly in database as BLOB/bytes
- Date fields stored as strings, formatted in models

## Admin Interface

Admin routes (`/adm/*`) provide:
- Login/logout functionality
- Notice management (create/edit/delete)
- Bus schedule management with image uploads
- Q&A response system
- Customer inquiry management
- Dashboard with statistics

Protected by session-based authentication middleware that redirects unauthorized access to `/adm/login`.