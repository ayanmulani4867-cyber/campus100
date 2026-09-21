# Campus Connect Production Deployment Guide

This guide covers production deployment on **Render**, containerized deployment via **Docker Compose**, and environment configuration.

---

## 1. Render Deployment (Recommended)

Campus Connect includes an infrastructure-as-code blueprint in `render.yaml`.

### Step 1: Connect GitHub Repository
1. Push your restructured repository to GitHub:
   ```bash
   git add .
   git commit -m "Production ready Campus Connect architecture"
   git push origin main
   ```
2. In the Render Dashboard, click **New +** and select **Blueprint**.
3. Select your GitHub repository. Render will detect `render.yaml`.

### Step 2: Automatic Resource Creation
Render will automatically provision:
1. **Web Service (`campus-connect`)**:
   - Runtime: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `gunicorn --chdir backend run:app`
2. **Managed PostgreSQL Database (`campus-connect-db`)**:
   - Provisioned with `DATABASE_URL` securely linked to the web service.

### Step 3: Seed Initial ERP Accounts
In the Render Web Service Shell:
```bash
python backend/seed.py
```

---

## 2. Docker Compose Deployment

For containerized cloud or self-hosted deployment:

```bash
# 1. Clone repository
git clone <repo-url>
cd CampusConnect

# 2. Build and launch database and web services
docker-compose up -d --build

# 3. Apply migrations and seed data
docker-compose exec backend python seed.py

# 4. Access portal
# Open http://localhost:5000 in your browser
```

---

## 3. Production Environment Variables

| Variable | Required | Default / Example | Purpose |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | `postgresql://user:pass@host:5432/campus_connect` | PostgreSQL connection string. |
| `SECRET_KEY` | **Yes** | 64+ char random string | Session cookie signing key. |
| `FLASK_ENV` | No | `production` | Enables production security settings. |
| `PORT` | No | `5000` | HTTP listening port. |
| `CORS_ORIGINS` | No | `https://your-domain.com` | Allowed CORS origins. |
| `MATERIAL_UPLOAD_DIR` | No | `/var/data/uploads/materials` | Mount point for persistent disk storage. |
| `FRONTEND_DIR` | No | `../frontend` | Path to static frontend files. |

---

## 4. Production Security Checklist

- [x] Gunicorn WSGI server handles all incoming traffic (no dev servers in production).
- [x] Passwords hashed with `Werkzeug` scrypt/pbkdf2 before database insertion.
- [x] Multi-tab token isolation prevents cross-role session contamination.
- [x] File uploads restrict allowed extensions (`.pdf`, `.ppt`, `.pptx`) and enforce a 25MB maximum size.
- [x] `.env` and `uploads/` are strictly excluded from git tracking via `.gitignore`.
- [x] All database queries are parameterized by SQLAlchemy ORM against SQL injection.
