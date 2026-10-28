# Django Clean Architecture API

Ported from Golang Clean Architecture to Python 3.13 / Django 5.2, implementing Uncle Bob's Clean Architecture with PostgreSQL and JWT Authentication (Token Versioning).

---

## Clean Architecture & Project Structure

```
django-clean-code-architecture/
├── apps/
│   ├── shared/
│   │   └── models.py               # Abstract Base Model (created_at, updated_at)
│   └── users/
│       ├── models.py               # User Domain Model
│       ├── services.py             # Business Logic
│       ├── serializers.py          # DTOs Data validation & serialization
│       ├── views.py                # Controllers HTTP Request/Response handling
│       ├── authentication.py       # JWT validation & OpenAPI scheme
│       └── urls.py                 # User Router mapping
├── config/                         # Frameworks & Drivers
│   ├── other_settings/
│   │   ├── rest_framwork.py        # DRF, pagination & schema settings
│   │   └── simple_jwt.py           # SimpleJWT settings & serializer bindings
│   ├── settings.py                 # Core Django configuration
│   ├── urls.py                     # Root URL routing & Swagger endpoints
│   ├── wsgi.py
│   └── asgi.py
├── docker-compose.yml              # PostgreSQL 15 container setup
├── pyproject.toml                  # Python version
└── uv.lock                         # Pinned dependency lockfile
```

---

## Package Manager Installation (uv)

### macOS & Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or via Homebrew (macOS): brew install uv
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Or via Winget: winget install --id=astral-sh.uv -e
```

### Universal (via pip)
```bash
pip install uv
```

---

## Getting Started

### 1. Start Database with Docker Compose
```bash
docker compose up -d
```
*(Runs PostgreSQL 15 on port 5432: database `khaojai_it_db` / user: `postgres` / password: `postgres`)*

### 2. Install Dependencies with uv sync
```bash
uv sync
```

### 3. Run Database Migrations & Start Server
```bash
uv run python manage.py migrate
uv run python manage.py runserver
```
The application will be accessible at: `http://127.0.0.1:8000/`

### 4. Run Tests
```bash
uv run python manage.py test
```

---

## API Endpoints & Swagger UI

Interactive API documentation with Authorize (Bearer Token) support:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema/`

### Endpoints (Matching the original Go specification)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/v1/user/register/` | None | Register a new user (`email`, `password`, `first_name`, `last_name`) |
| `POST` | `/api/v1/login/` | None | Authenticate user; returns `{user: {...}, token: {access, refresh}}` |
| `POST` | `/api/v1/logout/` | Bearer | Invalidate access token immediately via Token Versioning |
| `POST` | `/api/v1/refresh-token/` | None | Refresh access token (accepts both `refresh` and `refresh_token` keys) |
| `GET` / `POST` | `/api/v1/user/profile/` | Bearer | Retrieve current user profile |
