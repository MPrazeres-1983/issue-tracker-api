# 🎯 Issue Tracker API

[![CI/CD Pipeline](https://github.com/MPrazeres-1983/junior-python-backend-project/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MPrazeres-1983/junior-python-backend-project/actions)

[![codecov](https://codecov.io/gh/MPrazeres-1983/issue-tracker-api/graph/badge.svg)](https://codecov.io/gh/MPrazeres-1983/issue-tracker-api)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A production-ready REST API for project and issue tracking, built with Flask, PostgreSQL, and modern best practices. Designed as a portfolio project demonstrating professional backend development skills.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup (Docker)](#local-setup-docker)
  - [Local Setup (Manual)](#local-setup-manual)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **User Management**: Registration, authentication with JWT (access + refresh tokens)
- **Project Management**: Create, update, and organize projects with team members
- **Issue Tracking**: Create and track issues with status, priority, and assignments
- **Labeling System**: Categorize issues with customizable labels
- **Comments**: Discussion threads on issues
- **Role-Based Access Control**: Admin, Developer, and Viewer roles

### Technical Highlights
- RESTful API design with proper HTTP methods and status codes
- JWT authentication with bcrypt password hashing
- Input validation with Marshmallow schemas
- Pagination and filtering on list endpoints
- Structured JSON logging
- Rate limiting
- CORS support
- Comprehensive error handling
- Database migrations with Alembic
- Docker containerization
- CI/CD with GitHub Actions
- 70%+ test coverage

## 🛠 Tech Stack

### Core
- **Framework**: Flask 3.0
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: Flask-JWT-Extended, bcrypt
- **Validation**: Marshmallow

### Development & Deployment
- **Testing**: pytest, pytest-cov, factory-boy
- **Code Quality**: Ruff, Black
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Production Server**: Gunicorn
- **Deployment**: Render (or any cloud platform)

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                    (Web, Mobile, CLI)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Routes Layer                        │
│            (Blueprints, Request Handling)                    │
├─────────────────────────────────────────────────────────────┤
│                    Middleware Layer                          │
│         (Auth, Error Handling, Rate Limiting)                │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                      │
│              (Services: Auth, Project, Issue)                │
├─────────────────────────────────────────────────────────────┤
│                   Data Access Layer                          │
│              (Repositories, ORM Queries)                     │
├─────────────────────────────────────────────────────────────┤
│                    Persistence Layer                         │
│              (PostgreSQL Database)                           │
└─────────────────────────────────────────────────────────────┘
```

**Layered Architecture Benefits**:
- Separation of concerns
- Easy to test (mock each layer)
- Maintainable and scalable
- Clear data flow

For more details, see [docs/architecture.md](docs/architecture.md).

## 🚀 Getting Started

### Prerequisites

- **Docker**: Docker 20.10+ and Docker Compose 2.0+ (recommended)
- **OR Manual Setup**:
  - Python 3.11+
  - PostgreSQL 15+
  - pip and virtualenv

### Local Setup (Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/issue-tracker-api.git
   cd issue-tracker-api
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (defaults work for Docker)
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Create an admin user (optional)**
   ```bash
   docker-compose exec app python -c "from src.app import create_app; from src.services import AuthService; app = create_app(); ctx = app.app_context(); ctx.push(); auth = AuthService(); user, err = auth.register('admin', 'admin@example.com', 'Admin123!', 'admin'); print(f'Admin created: {user.username}' if user else f'Error: {err}')"
   ```

6. **API is now running at** `http://localhost:5000`
   - Health check: `http://localhost:5000/api/v1/health`
   - API docs: See [docs/api_examples.md](docs/api_examples.md)

### Local Setup (Manual)

1. **Clone and setup environment**
   ```bash
   git clone https://github.com/yourusername/issue-tracker-api.git
   cd issue-tracker-api
   
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Setup PostgreSQL**
   ```bash
   # Create database
   createdb issue_tracker
   
   # Or via psql
   psql -U postgres
   CREATE DATABASE issue_tracker;
   \q
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   # DATABASE_URL=postgresql://postgres:password@localhost:5432/issue_tracker
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Create admin user**
   ```bash
   flask create-admin
   ```

6. **Run the development server**
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

### Main Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get tokens | No |
| POST | `/auth/refresh` | Refresh access token | Yes (refresh token) |
| GET | `/auth/me` | Get current user | Yes |
| GET | `/projects` | List user's projects | Yes |
| POST | `/projects` | Create project | Yes |
| GET | `/projects/{id}` | Get project details | Yes |
| PUT | `/projects/{id}` | Update project | Yes |
| DELETE | `/projects/{id}` | Delete project | Yes (owner/admin) |
| GET | `/projects/{id}/issues` | List project issues | Yes |
| POST | `/projects/{id}/issues` | Create issue | Yes |
| GET | `/issues/{id}` | Get issue details | Yes |
| PUT | `/issues/{id}` | Update issue | Yes |
| DELETE | `/issues/{id}` | Delete issue | Yes |
| GET | `/issues/{id}/comments` | List issue comments | Yes |
| POST | `/issues/{id}/comments` | Add comment | Yes |
| GET | `/labels` | List all labels | Optional |
| POST | `/labels` | Create label | Yes (admin) |
| GET | `/health` | Health check | No |

For detailed examples with request/response payloads, see [docs/api_examples.md](docs/api_examples.md).

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run specific test types
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest tests/unit/test_auth_service.py  # Specific file
```

### View coverage report
```bash
open htmlcov/index.html  # macOS/Linux
start htmlcov\index.html # Windows
```

**Coverage Requirements**: Minimum 70% coverage enforced in CI/CD pipeline.

## 🔄 CI/CD

GitHub Actions pipeline runs on every push and pull request:

1. **Lint**: Code quality checks with Ruff and Black
2. **Test**: Run test suite with coverage reporting
3. **Build**: Build Docker image
4. **Security**: Dependency vulnerability scanning with Safety
5. **Deploy**: Auto-deploy to Render on main branch (optional)

View pipeline status: [![CI/CD](https://github.com/MPrazeres-1983/junior-python-backend-project/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MPrazeres-1983/junior-python-backend-project/actions)

## 🌐 Deployment

### Deploy to Render

1. **Create account** at [render.com](https://render.com)

2. **Create PostgreSQL database**
   - Go to Dashboard → New → PostgreSQL
   - Choose free tier
   - Note the Internal Database URL

3. **Create Web Service**
   - Go to Dashboard → New → Web Service
   - Connect your GitHub repository
   - Configure:
     - **Name**: issue-tracker-api
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn "src.app:create_app()" --bind 0.0.0.0:$PORT`

4. **Set Environment Variables**
   ```
   FLASK_ENV=production
   DATABASE_URL=<your_render_postgres_url>
   SECRET_KEY=<generate_secure_random_string>
   JWT_SECRET_KEY=<generate_secure_random_string>
   PYTHON_VERSION=3.11.0
   ```

5. **Deploy**
   - Render will auto-deploy on git push to main
   - Run migrations: Use Render shell to run `alembic upgrade head`

For other platforms (AWS, Heroku, DigitalOcean), see [docs/deployment.md](docs/deployment.md).

## 🔒 Security

- **Password Hashing**: bcrypt with cost factor 12
- **JWT Tokens**: 
  - Access tokens: 15 minutes expiry
  - Refresh tokens: 7 days expiry
  - Signed with HS256 algorithm
- **HTTPS**: Required in production (configured via reverse proxy)
- **Rate Limiting**: 100 requests per minute per IP
- **CORS**: Configurable allowed origins
- **SQL Injection**: Protected via SQLAlchemy parameterized queries
- **Input Validation**: All inputs validated with Marshmallow schemas
- **Error Handling**: No sensitive data exposed in error messages

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mário Prazeres**
- GitHub: [MPrazeres-1983](https://github.com/MPrazeres-1983)
- LinkedIn: [Mário Prazeres](https://www.linkedin.com/in/mario-prazeres/)
  
## 🙏 Acknowledgments

- Built as a portfolio project to demonstrate production-ready backend development
- Inspired by modern issue tracking systems like Jira, GitHub Issues, and Linear
- Thanks to the Flask and Python communities for excellent documentation

---

**Note**: This is a portfolio/demonstration project. For production use, additional security hardening and monitoring may be required.
