# 🎯 Issue Tracker API

[![CI/CD Pipeline](https://github.com/MPrazeres-1983/issue-tracker-api/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MPrazeres-1983/issue-tracker-api/actions)
[![Prompt Eval](https://github.com/MPrazeres-1983/issue-tracker-api/actions/workflows/prompt-eval.yml/badge.svg)](https://github.com/MPrazeres-1983/issue-tracker-api/actions)
[![codecov](https://codecov.io/gh/MPrazeres-1983/issue-tracker-api/graph/badge.svg?token=776HUXFGKU)](https://codecov.io/gh/MPrazeres-1983/issue-tracker-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

A production-ready REST API for project and issue tracking, built with Flask, PostgreSQL, and modern best practices. Designed as a portfolio project demonstrating professional backend development skills, clean architecture, CI/CD pipelines, and **AI-powered classification with prompt regression testing**.

## 🟢 Live Demo & Testing

The API is currently deployed and live!

* **Base URL:** `https://issue-tracker-api-860i.onrender.com/api/v1`
* **Health Check:** [Test API Status](https://issue-tracker-api-860i.onrender.com/api/v1/health)

### 🧑‍💻 How to test this API (Postman)
To make it easy for recruiters and developers to interact with the live database, a pre-configured Postman collection is included in this repository.
1. Download the `postman_collection.json` file from the root of this repository.
2. Open [Postman](https://www.postman.com/) and click **Import**.
3. Select the downloaded file. You now have a ready-to-use workspace to Register, Login, and Create Projects against the live production server!

## 📋 Table of Contents

- [Features](#features)
- [AI-Powered Classification](#-ai-powered-classification)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Testing & Quality](#testing--quality)
- [Deployment](#deployment)

## ✨ Features

### Core Functionality
- **User Management**: Registration, authentication with JWT (access + refresh tokens).
- **Project Management**: Create, update, and organize projects with team members.
- **Issue Tracking**: Create and track issues with status, priority, and assignments.
- **Labeling System**: Categorize issues with customizable labels.
- **Comments**: Discussion threads on issues.
- **Role-Based Access Control (RBAC)**: Admin, Developer, and Viewer roles with strict endpoint protection.
- **AI Classification**: Automatic priority and status suggestion for new issues via LLM.

### Technical Highlights
- RESTful API design with proper HTTP methods and status codes.
- Input validation and serialization using Marshmallow schemas.
- In-memory SQLite for isolated, fast, and pollution-free testing.
- Structured JSON logging ready for observability stacks.
- Global Error Handlers returning standardized JSON responses.
- **Prompt regression testing** via [PromptForge](https://github.com/MPrazeres-1983/promptforge) — every CI run evaluates the AI classifier against a golden dataset of 12 real issues.

## 🤖 AI-Powered Classification

This API includes an AI classification endpoint that suggests priority and status for new issues based on their title and description.

### How it works

When a developer submits an issue, instead of manually setting the priority, they can call `/api/v1/issues/suggest` to get an AI-generated suggestion with a confidence score and a one-line explanation.

```
POST /api/v1/issues/suggest
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "App crashes on login for all users",
  "description": "Since the last deploy, no user can log in. The app crashes immediately after submitting credentials."
}
```

Response:
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

### Prompt Regression Testing with PromptForge

The classification prompt is treated as a **versioned, tested artefact** using [PromptForge](https://github.com/MPrazeres-1983/promptforge). Every push to `main` runs an automated evaluation of the prompt against a golden dataset of 12 real-world issues — the CI pipeline fails if the classifier regresses.

```
prompt-eval job:
  ├── prompts/issue_classifier.yaml       # versioned prompt with system prompt
  ├── datasets/issue_classifier_golden.yaml  # 12 labelled issues (ground truth)
  ├── configs/issue_classifier.yaml       # evaluators: field_match + LLM-as-judge
  └── rubrics/issue_classifier_quality.yaml  # judge rubric: reasoning + consistency
```

This means: **if someone changes the prompt and the model starts misclassifying issues, the deployment is blocked automatically.**

The eval is powered by [`promptforge-llmops`](https://pypi.org/project/promptforge-llmops/) and runs as a reusable GitHub Action (`MPrazeres-1983/promptforge@v1`).

## 🛠 Tech Stack

- **Language**: Python 3.13
- **Framework**: Flask 3.0
- **Database**: PostgreSQL 17 (Hosted on Neon.tech)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Flask-JWT-Extended, bcrypt
- **Testing**: pytest, pytest-cov, factory-boy
- **AI**: OpenAI-compatible API (Groq / llama-3.3-70b-versatile)
- **LLMOps**: [PromptForge](https://github.com/MPrazeres-1983/promptforge) — prompt versioning & regression testing
- **CI/CD**: GitHub Actions, Codecov
- **Cloud Hosting**: Render

## 🏗 Architecture

The project follows a **Layered Architecture** (Controller-Service-Repository pattern) to promote the Separation of Concerns.

```text
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│                 (Postman, Web, Mobile)                      │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP / REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Routes Layer                         │
│             (Blueprints, Request Extraction)                │
├─────────────────────────────────────────────────────────────┤
│                  Business Logic Layer                       │
│         (Services: Auth, Project, Issue, Suggest)           │
├─────────────────────────────────────────────────────────────┤
│                   Data Access Layer                         │
│              (Repositories, ORM Queries)                    │
├─────────────────────────────────────────────────────────────┤
│                   Persistence Layer                         │
│                 (PostgreSQL Database)                       │
└─────────────────────────────────────────────────────────────┘
```
*This architecture allows business rules to be tested entirely in isolation, independently of the HTTP transport layer.*

## 🚀 Getting Started (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/MPrazeres-1983/issue-tracker-api.git
   cd issue-tracker-api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Linux/Mac: source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # .env
   OPENAI_API_KEY=your_groq_api_key
   OPENAI_BASE_URL=https://api.groq.com/openai/v1
   ```

5. **Run the development server**
   ```bash
   export FLASK_ENV=development
   flask run
   ```

## 🧪 Testing & Quality

The project features a robust test suite with ~200 automated tests and +75% coverage. Tests are executed dynamically using an isolated in-memory SQLite database to prevent state pollution.

**Run all tests:**
```bash
pytest tests/
```

**Run with coverage report:**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Run prompt regression tests locally:**
```bash
promptforge eval \
  --prompt prompts/issue_classifier.yaml \
  --dataset datasets/issue_classifier_golden.yaml \
  --config configs/issue_classifier.yaml
```

## 🌐 Deployment

This application is configured for seamless deployment on **Render**, connected to a **Neon.tech** Serverless Postgres database.

**Render Configuration:**
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python -c "from src.app import create_app; from src.models.base import db; app=create_app('production'); app.app_context().push(); db.create_all()"
  ```
- **Start Command:**
  ```bash
  gunicorn "src.app:create_app('production')"
  ```
- **Environment Variables Required:** `FLASK_ENV`, `DATABASE_URL`, `JWT_SECRET_KEY`, `PYTHON_VERSION`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Author:** Mário Prazeres | [LinkedIn](https://www.linkedin.com/in/mario-prazeres/) | [GitHub](https://github.com/MPrazeres-1983)