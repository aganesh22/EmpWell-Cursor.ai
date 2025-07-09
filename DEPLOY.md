# Deployment Guide

This document outlines how to build and deploy the Corporate Wellbeing Platform.

## 1. Prerequisites

* Docker 24+
* Docker Compose v2
* PostgreSQL (if you prefer managed DB instead of container)
* SMTP credentials for notifications (`EMAIL_HOST`, `EMAIL_USER`, `EMAIL_PASS`, etc.)
* Cloud provider account (AWS / Azure / GCP).

## 2. Environment Variables

Create a `.env` file in the project root or supply variables via your orchestrator:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/postgres
SECRET_KEY=change_me
GOOGLE_CLIENT_ID=<google-client>
EMAIL_HOST=smtp.yourcompany.com
EMAIL_PORT=587
EMAIL_USER=no-reply@yourcompany.com
EMAIL_PASS=xxxx
HR_ALERT_EMAIL=hr@yourcompany.com
```

## 3. Container Images

```
# Build images
$ docker compose build
# Push to registry (example)
$ docker tag wellbeing-backend:latest registry.io/org/wellbeing-backend:1.0.0
$ docker push registry.io/org/wellbeing-backend:1.0.0
```

## 4. Kubernetes Deployment (optional)

`k8s/` manifests are provided for reference (deployment, service, ingress).

Deploy with:
```
kubectl apply -f k8s/
```

## 5. Scaling & Performance

* Backend is async (FastAPI) – configure Uvicorn workers (e.g., `--workers 4`).
* Use managed PostgreSQL with automatic backups.
* Enable Postgres connection pooler (pgBouncer).
* Add indices for heavy query columns (`user_id`, `template_id`, `created_at`).

## 6. Security Hardening

* Run `docker compose run backend bandit -r backend/app -ll` monthly.
* Keep dependencies updated (`safety check`).
* Enforce HTTPS (TLS cert) on ingress.
* Rotate `SECRET_KEY` annually.

## 7. CI/CD

GitHub Actions workflow `.github/workflows/ci.yml` executes tests, security scans and can be extended to push images + deploy.

---
For detailed production-readiness checks refer to the [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/).