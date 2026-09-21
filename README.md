# Campus Connect — Enterprise Campus ERP & Academic Management System

Campus Connect is a comprehensive, production-ready ERP system designed for universities and colleges. It bridges students, faculty, and administrative departments through real-time academic workflows, attendance tracking, examination scorecards, study material repositories, notice broadcasts, and isolated multi-role sessions.

---

## Architecture Overview

```
CampusConnect/
├── backend/                  # Production Flask + SQLAlchemy Backend
│   ├── app/
│   │   ├── extensions/       # Database & Migrate extensions
│   │   ├── models/           # Relational SQLAlchemy models (PostgreSQL)
│   │   ├── routes/           # 12 REST API feature blueprints
│   │   ├── services/         # Storage and academic business logic
│   │   ├── utils/            # Authentication, errors, validators
│   │   ├── schema_compat.py  # Non-destructive schema migration
│   │   └── __init__.py       # Application factory & static file serving
│   ├── migrations/           # Alembic database migration versions
│   ├── tests/                # Automated auth, navigation, and CRUD test suites
│   ├── run.py                # Development & Gunicorn WSGI entrypoint
│   ├── seed.py               # Enterprise academic mapping & data seed
│   ├── config.py             # Multi-environment configuration
│   ├── requirements.txt      # Production dependencies (Gunicorn, psycopg2)
│   ├── Dockerfile            # Container specification
│   ├── .env.example          # Environment variable template
│   └── .env                  # Local environment (excluded from git)
│
├── frontend/                 # High-Performance ERP Multipage Web Application
│   ├── css/style.css         # Academic design system, tokens, and ERP animations
│   ├── js/script.js          # Client-side API client, ERP UX toolkit, routing
│   ├── images/               # Brand & profile assets
│   ├── *.html                # 13 Dedicated ERP views (Dashboard, Users, Results, etc.)
│   ├── package.json          # Vite build & bundle tooling
│   └── vite.config.js        # Multi-page Vite configuration & dev proxy
│
├── docs/                     # Comprehensive Documentation
│   ├── API.md                # REST API endpoints, request/response schema
│   ├── DATABASE.md           # Database tables, relationships, and ER model
│   └── DEPLOYMENT.md         # Step-by-step Render and Docker deployment
│
├── scripts/                  # Cross-platform development and seed utilities
│   ├── dev.bat / dev.sh      # One-command server startup
│   └── seed.bat / seed.sh    # Database seeding
│
├── .github/workflows/ci.yml  # GitHub Actions CI pipeline
├── uploads/materials/        # Persistent study material storage (excluded from git)
├── render.yaml               # Infrastructure-as-code Render Blueprint
├── docker-compose.yml        # PostgreSQL + Backend container orchestration
└── .gitignore                # Production ignore rules (.env, .venv, uploads)
```

---

## Demo Credentials

All accounts are pre-configured with password: `campus@123`

| Role | Email / Login ID | Initial Access |
|---|---|---|
| **Admin** | `admin@campus.edu` | User Directory, Academic Structure, Result Control, Notice Broadcasts |
| **Faculty** | `anita.sen@campus.edu` | Roll-Call Attendance, Examination Marks, Material Uploads, Division A/B |
| **Faculty** | `rajesh.verma@campus.edu` | Computer Networks & Labs, Roll-Call Attendance |
| **Student** | `rahul@campus.edu` | Student Dashboard, Attendance Pct, Course Scorecards, Study Materials |

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally (or via Docker)

### 2. Setup Virtual Environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/macOS
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Environment Configuration
Create `backend/.env` (or copy from `backend/.env.example`):
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/campus_connect
SECRET_KEY=your-secure-random-secret-key
FLASK_ENV=development
```

### 4. Seed Database & Start Server
```bash
# Seed initial departments, faculty, students, and courses
python backend/seed.py

# Launch server
python backend/run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## Docker Deployment (One-Command)

```bash
docker-compose up -d --build
docker-compose exec backend python seed.py
```
The application will be accessible at **`http://localhost:5000`**.

---

## Production Deployment (Render)

1. Push this repository to GitHub.
2. In Render, select **New + $\rightarrow$ Blueprint**.
3. Select your repository. Render will automatically configure the Web Service with **Gunicorn** and provision a managed **PostgreSQL** database based on `render.yaml`.
4. In the Web Service Shell, run `python backend/seed.py`.

---

## Running Test Suites

```bash
# Multi-tab authentication and RBAC isolation tests
python backend/tests/test_auth_sessions.py

# Admin navigation and module isolation tests
python backend/tests/test_admin_nav.py

# 17 CRUD / Action operations reactive ERP UX tests
python backend/tests/test_crud_ux.py

# Comprehensive E2E workflow tests
python backend/tests/test_e2e.py
```
