# Campus Connect Production Deployment Guide

This guide covers production deployment on **Render** (via 1-click Blueprint or Manual Service creation) and containerized deployment via **Docker Compose**.

---

## 1. Render Deployment via Blueprint (Recommended)

Campus Connect includes an infrastructure-as-code blueprint in `render.yaml`.

### Step 1: Connect GitHub Repository
1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "fix: render deployment configuration for docker backend and static frontend"
   git push origin main
   ```
2. In the Render Dashboard, click **New +** and select **Blueprint**.
3. Select your repository (`ayanmulani4867-cyber/campus100`).

### Step 2: Automatic Resource Creation
Render will automatically provision:
1. **Backend Web Service (`campus-connect-api`)**:
   - Runtime: `Docker`
   - Root Directory: `backend`
   - Dockerfile: `Dockerfile` (inside `backend/`)
   - Docker Context: `.` (resolving to `backend/`)
   - Gunicorn WSGI binding dynamically to `$PORT`
2. **Frontend Static Site (`campus-connect-frontend`)**:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Rewrites `/api/*` to `https://campus-connect-api.onrender.com/api/*`
3. **Managed PostgreSQL Database (`campus-connect-db`)**:
   - Securely wired to `DATABASE_URL`

### Step 3: Seed Initial ERP Accounts
In the Render Web Service Shell (`campus-connect-api`):
```bash
python seed.py
```

---

## 2. Render Manual Service Configuration (Without Blueprint)

If you are configuring services manually in the Render dashboard:

### Backend Web Service
| Setting | Value |
|---|---|
| **Name** | `campus-connect-api` |
| **Repository** | `ayanmulani4867-cyber/campus100` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Dockerfile Path** | `Dockerfile` |
| **Docker Build Context** | `.` |
| **Plan** | Free |

**Environment Variables**:
- `DATABASE_URL`: Your PostgreSQL connection string (from Render Postgres).
- `SECRET_KEY`: A secure random string (e.g. 64 characters).
- `FLASK_ENV`: `production`

### Frontend Static Site
| Setting | Value |
|---|---|
| **Name** | `campus-connect-frontend` |
| **Repository** | `ayanmulani4867-cyber/campus100` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

**Static Site Rewrites & Redirects**:
- **Source**: `/api/*`
- **Destination**: `https://campus-connect-api.onrender.com/api/*`
- **Action**: Rewrite

---

## 3. Docker Compose Deployment (Local / Self-Hosted)

```bash
# 1. Clone repository
git clone https://github.com/ayanmulani4867-cyber/campus100.git
cd campus100

# 2. Launch PostgreSQL and backend containers
docker-compose up -d --build

# 3. Seed demo accounts
docker-compose exec backend python seed.py

# 4. Open portal
# Access http://localhost:5000 in your browser
```

---

## 4. Production Security Checklist

- [x] Gunicorn WSGI server handles all backend traffic (binds dynamically to `$PORT`).
- [x] Multi-tab token isolation prevents cross-role session contamination.
- [x] Passwords hashed with `Werkzeug` scrypt/pbkdf2 before database insertion.
- [x] File uploads restrict allowed extensions (`.pdf`, `.ppt`, `.pptx`) and enforce a 25MB maximum size.
- [x] `.env` and `uploads/` are strictly excluded from git tracking via `.gitignore`.
- [x] All database queries are parameterized by SQLAlchemy ORM against SQL injection.
