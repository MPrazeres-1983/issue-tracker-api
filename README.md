# 🎯 Issue Tracker API

[![CI/CD Pipeline](https://github.com/MPrazeres-1983/issue-tracker-api/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MPrazeres-1983/issue-tracker-api/actions)
[![Prompt Eval](https://github.com/MPrazeres-1983/issue-tracker-api/actions/workflows/prompt-eval.yml/badge.svg)](https://github.com/MPrazeres-1983/issue-tracker-api/actions)
[![codecov](https://codecov.io/gh/MPrazeres-1983/issue-tracker-api/graph/badge.svg?token=180b7fb7-8992-4a95-8761-3ddc65addc21)](https://codecov.io/gh/MPrazeres-1983/issue-tracker-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

A production-ready REST API for project and issue tracking, built with **Flask**, **PostgreSQL** and a clean layered architecture.

This project demonstrates professional backend engineering practices with a strong focus on software quality: authentication, role-based access control, automated testing, CI/CD, API documentation, deployment and **AI-powered issue classification with prompt regression testing**.

---

## 🟢 Live Demo

The API is deployed and available for testing.

- **Base URL:** `https://issue-tracker-api-860i.onrender.com/api/v1`
- **Health Check:** [Test API Status](https://issue-tracker-api-860i.onrender.com/api/v1/health)

> The service is hosted on Render. If the API has been idle, the first request may take a few seconds to wake up.

---

## 🧑‍💻 Test with Postman

A pre-configured Postman collection is included in the repository.

1. Download `postman_collection.json` from the repository root.
2. Open [Postman](https://www.postman.com/).
3. Click **Import**.
4. Select the downloaded file.
5. Use the collection to register, log in and create projects/issues against the live API.

---

## 📋 Table of Contents

- [Features](#-features)
- [AI-Powered Classification](#-ai-powered-classification)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started-local-development)
- [Environment Variables](#-environment-variables)
- [Testing & Quality](#-testing--quality)
- [Deployment](#-deployment)
- [License](#-license)

---

## ✨ Features

### Core Functionality

- **User management**: registration and authentication with JWT access and refresh tokens.
- **Project management**: create, update and organise projects with team members.
- **Issue tracking**: create and track issues with status, priority and assignments.
- **Labels**: categorise issues with custom labels.
- **Comments**: discussion threads on issues.
- **Role-Based Access Control**: Admin, Developer and Viewer roles with endpoint-level protection.
- **AI classification**: automatic priority and status suggestions for new issues using an LLM.

### Technical Highlights

- RESTful API design with proper HTTP methods and status codes.
- Layered architecture using a Controller-Service-Repository pattern.
- Input validation and serialization with Marshmallow schemas.
- PostgreSQL in production.
- SQLite in-memory database for isolated automated tests.
- Structured JSON logging.
- Global error handlers with standardized JSON responses.
- CI/CD with GitHub Actions.
- Coverage reporting with Codecov.
- Prompt regression testing with [PromptForge](https://github.com/MPrazeres-1983/promptforge).

---

## 🤖 AI-Powered Classification

The API includes an AI classification endpoint that suggests a priority and status for new issues based on their title and description.

Instead of manually assigning the initial priority, a developer can call:

```http
POST /api/v1/issues/suggest
Authorization: Bearer <token>
Content-Type: application/json
```

Example request:

```json
{
  "title": "App crashes on login for all users",
  "description": "Since the last deploy, no user can log in. The app crashes immediately after submitting credentials."
}
```

Example response:

```json
{
  "success": true,
  "data": {
    "priority": "critical",
    "status": "open",
    "confidence": "high",
    "reason": "Complete login failure blocking all users with no workaround indicates a critical production incident."
  }
}
```

---

## 🔬 Prompt Regression Testing

The issue classification prompt is treated as a **versioned and tested artefact** using [PromptForge](https://github.com/MPrazeres-1983/promptforge).

Every relevant CI run can evaluate the classifier against a golden dataset of labelled issues. If a prompt change causes the classifier to regress, the pipeline can fail before the change reaches production.

```text
prompt-eval job:
  ├── prompts/issue_classifier.yaml
  ├── datasets/issue_classifier_golden.yaml
  └── configs/issue_classifier.yaml
```

This makes the AI feature testable and reviewable instead of relying on manual checks or intuition.

The evaluation is powered by [`promptforge-llmops`](https://pypi.org/project/promptforge-llmops/) and runs through the reusable GitHub Action:

```text
MPrazeres-1983/promptforge@v1
```

The current provider setup uses **Groq** through an OpenAI-compatible API interface.

---

## 🛠 Tech Stack

| Area | Technologies |
| ---- | ------------ |
| Language | Python 3.13 |
| Framework | Flask 3.0 |
| Database | PostgreSQL 17, SQLite for tests |
| ORM | SQLAlchemy 2.0 |
| Validation | Marshmallow |
| Authentication | Flask-JWT-Extended, bcrypt |
| Testing | pytest, pytest-cov, factory-boy |
| AI Provider | Groq through an OpenAI-compatible API |
| LLMOps | PromptForge |
| CI/CD | GitHub Actions, Codecov |
| Deployment | Render |
| Database Hosting | Neon |

---

## 🏗 Architecture

The project follows a layered architecture to keep transport, business logic and persistence concerns separated.

```text
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│                 Postman, Web, Mobile, API Clients           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP / REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Routes Layer                         │
│             Blueprints, request parsing, responses          │
├─────────────────────────────────────────────────────────────┤
│                  Business Logic Layer                       │
│             Auth, Project, Issue, Suggest services          │
├─────────────────────────────────────────────────────────────┤
│                   Data Access Layer                         │
│              Repositories and ORM queries                   │
├─────────────────────────────────────────────────────────────┤
│                   Persistence Layer                         │
│              PostgreSQL / SQLite in tests                   │
└─────────────────────────────────────────────────────────────┘
```

This structure makes the business rules easier to test independently from the HTTP layer.

---

## 🚀 Getting Started (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/MPrazeres-1983/issue-tracker-api.git
cd issue-tracker-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the repository root.

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///issue_tracker_dev.db
JWT_SECRET_KEY=change-this-secret-locally
OPENAI_API_KEY=your_groq_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

### 5. Run the development server

```bash
flask run
```

The local API should now be available at:

```text
http://127.0.0.1:5000
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `FLASK_ENV` | yes | Flask environment: `development`, `testing` or `production` |
| `DATABASE_URL` | yes | Database connection string |
| `JWT_SECRET_KEY` | yes | Secret key used to sign JWT tokens |
| `OPENAI_API_KEY` | yes, for AI endpoint | Groq API key when using Groq |
| `OPENAI_BASE_URL` | yes, for Groq | OpenAI-compatible base URL |
| `PYTHON_VERSION` | required on Render | Python runtime version |

For Groq:

```env
OPENAI_API_KEY=your_groq_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

---

## 🧪 Testing & Quality

The project includes approximately 200 automated tests and maintains more than 75% coverage.

Tests use an isolated in-memory SQLite database to avoid state pollution and make the suite fast and repeatable.

### Run all tests

```bash
pytest tests/
```

### Run tests with coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run prompt regression tests locally

```bash
promptforge eval \
  --prompt prompts/issue_classifier.yaml \
  --dataset datasets/issue_classifier_golden.yaml \
  --config configs/issue_classifier.yaml
```

### Quality Signals

- Automated test suite.
- CI/CD pipeline.
- Coverage reporting.
- Isolated test database.
- Prompt regression checks for the AI classifier.
- Postman collection for manual API exploration.

---

## 🌐 Deployment

The application is configured for deployment on **Render**, connected to a **Neon** PostgreSQL database.

### Build Command

```bash
pip install -r requirements.txt && python -c "from src.app import create_app; from src.models.base import db; app=create_app('production'); app.app_context().push(); db.create_all()"
```

### Start Command

```bash
gunicorn "src.app:create_app('production')"
```

### Required Production Variables

```text
FLASK_ENV
DATABASE_URL
JWT_SECRET_KEY
PYTHON_VERSION
OPENAI_API_KEY
OPENAI_BASE_URL
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Author:** Mário Prazeres  
[LinkedIn](https://www.linkedin.com/in/mario-prazeres/) · [GitHub](https://github.com/MPrazeres-1983)
