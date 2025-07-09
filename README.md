Corporate Employee Wellbeing & Psychometric Analysis Platform
============================================================

This repository contains the source code for an internal-facing web application that enables organisations to measure and improve employee wellbeing using validated psychometric instruments.

## Architecture

The codebase is organised as a monorepo with two major packages:

1. **backend/** – Python 3.11 + FastAPI service that exposes a REST-style API, handles authentication/SSO, business logic, and persistence to PostgreSQL.
2. **frontend/** – React 18 (TypeScript) application bootstrapped with Vite that consumes the backend API and provides a responsive, WCAG-compliant UI.

## Quick start (local development)

```bash
# Clone & enter workspace
git clone https://github.com/aganesh22/EmpWell-Cursor.ai.git
cd EmpWell-Cursor.ai

# Spin up full stack – PostgreSQL, backend, and frontend – with hot-reload
docker compose up --build
```

The stack is defined in `docker-compose.yml` and is configured for **development** use. Secrets are injected via the `.env` file (see `.env.example`).

## Frontend Only (for Bolt/StackBlitz)

```bash
cd frontend
npm install
npm run dev
```

## Key tech choices

* **FastAPI** – modern, async-first framework with excellent type hints and automatic OpenAPI docs.
* **SQLModel** – Pydantic v2 + SQLAlchemy 2.0 = fast, type-safe ORM models.
* **PostgreSQL** – reliable, feature-rich relational database.
* **React + Vite** – fast dev server, modern build, great DX.
* **Chart.js** – interactive data visualization for admin dashboards.

## Features

### Phase 1 - Foundation
- [x] Email/password registration & login (JWT)
- [x] Google Workspace SSO (OIDC)
- [x] Admin dashboard with user management
- [x] Role-based access control (employee vs admin)

### Phase 2 - Test Engine
- [x] Dynamic test engine with question banks
- [x] WHO-5 Wellbeing Index (5 questions)
- [x] Instant results with scoring logic

### Phase 3 - Advanced Assessments
- [x] MBTI-inspired assessment (32 questions)
- [x] DISC assessment (28 questions)
- [x] Detailed type descriptions and recommendations
- [x] PDF report generation
- [x] HR aggregate reports with department comparisons

### Phase 4 - Enhancements
- [x] Interactive admin analytics dashboard
- [x] Resources & recommendations section
- [x] Email notification system
- [x] Branching logic for conditional questions

### Phase 5 - Production Ready
- [x] Comprehensive testing (pytest)
- [x] Security audits (bandit, safety)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Deployment documentation

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/postgres
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
EMAIL_HOST=smtp.yourcompany.com
EMAIL_USER=no-reply@yourcompany.com
EMAIL_PASS=your-email-password
HR_ALERT_EMAIL=hr@yourcompany.com
```

## API Endpoints

* `/auth/register` - User registration
* `/auth/login` - User login
* `/auth/google` - Google SSO
* `/tests/` - List available tests
* `/tests/{key}/submit` - Submit test answers
* `/reports/aggregate` - HR analytics (admin only)
* `/resources/` - Wellbeing resources
* `/users/` - User management (admin only)

## Deployment

See `DEPLOY.md` for production deployment instructions.

## Contributing

Pull requests are welcome. Please open an issue first to discuss major changes.

## License

MIT