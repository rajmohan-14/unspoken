# Unspoken

An anonymous confession and kindness platform built with Django.

## ✅ What to do next (quick-start)

All the code and deployment config is ready. Here is the exact sequence of steps you need to follow to get the app running publicly:

### Deploy on Render (free tier available)

- [ ] 1. **Merge this PR** into `main` on GitHub.
- [ ] 2. Go to [render.com](https://render.com) and create a free account (or log in).
- [ ] 3. Click **New → Blueprint** in the Render dashboard and connect your GitHub repository.
- [ ] 4. Render reads `render.yaml` automatically and provisions everything (web app, Celery worker, Celery beat, PostgreSQL, Redis). Click **Apply**.
- [ ] 5. Wait for the first deploy to finish (~5 minutes).
- [ ] 6. Open a **Shell** for the `unspoken-web` service and run:
       ```
       python manage.py migrate
       python manage.py createsuperuser
       ```
- [ ] 7. Your app is live at the URL shown in the Render dashboard (e.g. `https://unspoken-web.onrender.com`). The admin panel is at `/admin/`.

---

## Features

- Anonymous post submissions with content moderation
- Kindness voting system with weekly highlights
- Automatic expiry and cleanup of old posts
- Admin moderation queue

## Tech Stack

- **Backend**: Django 6.0, Django REST Framework
- **Task Queue**: Celery + Redis
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Static Files**: WhiteNoise

## Local Development

### Prerequisites

- Python 3.13+
- Redis

### Setup

```bash
# Clone the repository
git clone https://github.com/rajmohan-14/unspoken.git
cd unspoken

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env and set your SECRET_KEY, DEBUG=True, and HMAC_SECRET

# Apply migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

In separate terminals, start Celery:

```bash
# Celery worker
celery -A core worker -l info

# Celery beat scheduler
celery -A core beat -l info
```

The app will be available at http://localhost:8000.

## Deployment with Docker

### Prerequisites

- Docker and Docker Compose

### Steps

```bash
# Copy and configure environment file
cp .env.example .env
# Edit .env and set DEBUG=False, a strong SECRET_KEY, and HMAC_SECRET

# Build and start all services
docker compose up --build -d

# Apply migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser
```

The app will be available at http://localhost:8000.

## Deployment on Render

The easiest way to deploy Unspoken is with [Render](https://render.com) using the included `render.yaml` Blueprint. It provisions a web service, Celery worker, Celery beat scheduler, PostgreSQL database, and Redis instance automatically.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Steps

1. Fork or push this repository to GitHub.
2. In the [Render dashboard](https://dashboard.render.com/), click **New → Blueprint** and connect your repository.
3. Render reads `render.yaml` and provisions all services automatically.
4. After the first deploy completes, open a Render Shell for the `unspoken-web` service and run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

All environment variables (`SECRET_KEY`, `HMAC_SECRET`, `DATABASE_URL`, etc.) are generated or wired up automatically by the Blueprint.

## Environment Variables Reference

See [`.env.example`](.env.example) for all available environment variables.

## CI/CD

This repository includes a GitHub Actions CI workflow:

- **CI** (`.github/workflows/ci.yml`): Runs on every push and pull request to `main`. Installs dependencies, runs migrations, runs tests, and checks `collectstatic`.
