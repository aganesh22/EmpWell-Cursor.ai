# EmpWell-Cursor.ai
Corporate Employee Wellbeing & Psychometric Analysis Platform
============================================================

This repository contains the source code for an internal-facing web application that enables organisations to measure and improve employee wellbeing using validated psychometric instruments.

The codebase is organised as a *monorepo* with two major packages:

1. **backend/** – Python 3.11 + FastAPI service that exposes a REST-style API, handles authentication/SSO, business logic, and persistence to PostgreSQL.
2. **frontend/** – React 18 (TypeScript) application bootstrapped with Vite that consumes the backend API and provides a responsive, WCAG-compliant UI.

Quick start (local development)
------------------------------

```bash
# Clone & enter workspace
$ git clone <repo> wellbeing-platform && cd wellbeing-platform

# Spin up full stack – PostgreSQL, backend, and frontend – with hot-reload
$ docker compose up --build
```

The stack is defined in `docker-compose.yml` and is configured for **development** use. Secrets are injected via the `.env` file (see `.env.example`).

Key tech choices
----------------

* **FastAPI** – modern, async-first framework with excellent type hints and automatic OpenAPI docs.
* **SQLModel** – Pydantic v2 + SQLAlchemy 2.0 = fast, type-safe ORM models.
* **PostgreSQL** – reliable, feature-rich relational database.
* **React + Vite** – fast dev server, modern build, great DX.
* **shadcn/ui + Tailwind CSS** – accessible, composable component library.

Next steps
----------
Phase 1 implementation is in progress:

* [x] Project scaffold & dependencies
* [ ] Email/password registration & login (JWT)
* [ ] Google Workspace SSO (OIDC)
* [ ] Admin dashboard skeleton
* [ ] RBAC middleware (`employee` vs `admin`)

Contributions
-------------
Pull requests are welcome 🚀. Please open an issue first to discuss major changes or features.

License
-------
MIT