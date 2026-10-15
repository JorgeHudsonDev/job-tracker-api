# Job Tracker API

[![CI](https://github.com/JorgeHudsonDev/job-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/JorgeHudsonDev/job-tracker-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

A REST API to keep track of your job applications. Users register, log in with a JWT and manage **their own** applications through their whole lifecycle: saved, applied, interview, offer or rejected.

I built it as a small but complete backend project: authentication, data ownership, validation, automated tests, a container image, CI and a public deployment.

## Live demo

**[Open the interactive docs (Swagger UI)](https://job-tracker-api-exhf.onrender.com/docs)**

> The demo runs on a free Render instance. It sleeps after 15 minutes without traffic, so the first request can take around a minute to wake it up. The filesystem is ephemeral, so users and applications are **reset** whenever the service restarts or sleeps. It is a demo, not a production deployment.

To try it: create a user with `POST /auth/register`, click **Authorize**, log in with that username and password, and use the `/applications` endpoints.

## Features

- User registration and login with **JWT** access tokens.
- Passwords stored as **Argon2 hashes**, never in plain text.
- Full **CRUD** for applications, with filtering by status and pagination.
- **Ownership isolation**: each user can only read, update or delete their own applications.
- Request validation with **Pydantic**, with clear `422` errors for invalid input.
- Interactive documentation generated automatically by FastAPI.
- **Pytest** suite running against an isolated in-memory database.
- **Docker** image running as a non-root user.
- **GitHub Actions** workflow that runs the tests and builds the image on every push.

## Tech stack

| Area | Tools |
|---|---|
| Language and framework | Python, FastAPI, Uvicorn |
| Data | SQLAlchemy 2.0, SQLite |
| Auth and security | PyJWT, pwdlib (Argon2), OAuth2 password flow |
| Validation and settings | Pydantic, pydantic-settings |
| Testing | Pytest, HTTPX (`TestClient`) |
| DevOps | Docker, GitHub Actions, Render |

## API overview

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create a user |
| `POST` | `/auth/login` | No | Get an access token |
| `GET` | `/auth/me` | Yes | Current user |
| `POST` | `/applications` | Yes | Create an application |
| `GET` | `/applications` | Yes | List your applications (`?status=`, `?limit=`, `?offset=`) |
| `GET` | `/applications/{id}` | Yes | Get one application |
| `PATCH` | `/applications/{id}` | Yes | Partially update an application |
| `DELETE` | `/applications/{id}` | Yes | Delete an application |
| `GET` | `/health` | No | Health check |

Valid statuses: `saved`, `applied`, `interview`, `offer`, `rejected`.

## Run it locally

Requirements: Python 3.12 or newer.

```bash
git clone https://github.com/JorgeHudsonDev/job-tracker-api.git
cd job-tracker-api

python -m venv .venv
source .venv/bin/activate        # Windows (PowerShell): .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

cp .env.example .env             # Windows (PowerShell): copy .env.example .env
```

Open `.env` and set a real `SECRET_KEY`. You can generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the server:

```bash
python -m uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000/docs>.

### Configuration

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Key used to sign JWTs (required) | — |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./app.db` |

## Run it with Docker

```bash
docker build -t job-tracker-api .
docker run --rm -p 8000:8000 --env-file .env job-tracker-api
```

The API will be available at <http://localhost:8000/docs>. The `.env` file is passed at runtime and is never copied into the image.

## Run the tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

The tests cover registration, login, token validation, the full applications CRUD, filtering, pagination and, most importantly, that one user cannot read, modify or delete another user's data. Each test runs against its own in-memory database, so nothing touches your local data.

## Project structure

```
.
├── app/
│   ├── main.py            # FastAPI app and router registration
│   ├── config.py          # Settings loaded from environment variables
│   ├── database.py        # Engine, session and get_db dependency
│   ├── models.py          # SQLAlchemy models (User, Application)
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── security.py        # Password hashing and JWT helpers
│   ├── deps.py            # get_current_user dependency
│   └── routers/
│       ├── auth.py        # Register, login, me
│       └── applications.py# Applications CRUD
├── tests/                 # Pytest suite
├── .github/workflows/     # CI pipeline
├── Dockerfile
└── requirements*.txt
```

## Design decisions

- **Separate models and schemas.** SQLAlchemy models describe tables and Pydantic schemas describe what enters and leaves the API. This keeps fields like `hashed_password` out of every response by construction.
- **Ownership is enforced in one place.** Every application lookup goes through a single helper that filters by `owner_id`. The owner is always taken from the token, never from the request body.
- **`404` instead of `403` for other users' data.** Asking for someone else's application returns "not found", so the API never confirms that an id exists in another account. Login errors use the same message for a wrong user or a wrong password for the same reason.
- **Dependency injection for the database.** Because the session comes from `Depends(get_db)`, the tests can swap it for an in-memory database without changing application code.
- **`PATCH` with partial updates.** Only the fields sent by the client are modified.
- **Configuration through the environment.** No secrets live in the repository or in the Docker image. The tests set their own throwaway key, so CI needs no secrets.
- **Container as a non-root user**, with dependencies installed before the code is copied to take advantage of Docker's layer cache.

## Known limitations and next steps

- SQLite and `create_all` keep the demo simple. For a real deployment I would move to **PostgreSQL** with **Alembic** migrations.
- Add a **refresh token** flow and rate limiting on the login endpoint.
- Add statistics endpoints (applications per status, response rate, applications without news after N days).
- Add a small frontend (Next.js) that consumes the API.
- Add a linter and formatter (Ruff) to the CI pipeline.

## Author

**Jorge Hudson Narváez** · Full Stack Developer based in Málaga, Spain

[LinkedIn](https://www.linkedin.com/in/jorge-hudson-narv%C3%A1ez-01b154186/) · [GitHub](https://github.com/JorgeHudsonDev)