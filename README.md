# CloudShare REST API

[![Python](https://img.shields.io/badge/Python-3.13+-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-cc0000.svg)](https://www.sqlalchemy.org/)

A modern, full-stack cloud storage and media sharing platform built with **FastAPI** and **Streamlit**. Upload images and videos, share them with the world, and manage your content — all powered by cloud infrastructure.

---

## 📸 Screenshots

<img width="1919" height="637" alt="image" src="https://github.com/user-attachments/assets/6fd46b9b-1c5e-4674-9bd7-8aaca217ff54" />
<br>
<img width="1918" height="906" alt="image" src="https://github.com/user-attachments/assets/fa4f725a-f3d8-47c4-b4e3-a8bf48738b7b" />
<br>
<img width="1915" height="908" alt="image" src="https://github.com/user-attachments/assets/ecb8a609-76b6-4cef-be28-8b38d9c3917c" />
<br>
<img width="1919" height="699" alt="image" src="https://github.com/user-attachments/assets/d254f0d7-7fe0-42a6-9a71-a302572877d3" />
<br>



---

## Features

- **JWT Authentication** — Secure register/login flow using FastAPI Users with bcrypt + argon2 password hashing
- **Media Uploads** — Support for images (PNG, JPG, JPEG) and videos (MP4, AVI, MOV, MKV, WEBM)
- **Cloud Storage** — Files are uploaded directly to [ImageKit.io](https://imagekit.io/) for optimized delivery
- **Social Feed** — Browse all posts from every user, sorted by newest first
- **Caption Overlays** — ImageKit's transformation API renders captions directly on images
- **Post Ownership** — Users can only delete their own posts; enforced at the API level
- **Async Backend** — Fully async FastAPI + aiosqlite stack for high throughput
- **Dark UI** — Polished Streamlit interface with a custom dark theme

---

## Tech Stack

### Backend
| Library | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance async web framework |
| [FastAPI Users](https://fastapi-users.github.io/fastapi-users/) | Auth, JWT, registration, password hashing |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | ORM + async session management |
| [aiosqlite](https://aiosqlite.omnilib.dev/) | Async SQLite driver |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server with hot-reload |
| [ImageKit Python SDK](https://github.com/imagekit-developer/imagekit-python) | Cloud media upload and URL transformations |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management |

### Frontend
| Library | Purpose |
|---|---|
| [Streamlit](https://streamlit.io/) | Rapid Python UI framework |
| [Requests](https://docs.python-requests.org/) | HTTP client for calling the FastAPI backend |

### Database
| Component | Details |
|---|---|
| SQLite | Lightweight, file-based, zero-config |
| aiosqlite | Non-blocking async access |
| SQLAlchemy ORM | Declarative models, relationship management |

---

##  Why SQLAlchemy?

SQLAlchemy is the gold standard ORM for Python, and using it here — even with SQLite — was a deliberate choice for several reasons:

**1. Async-first with SQLAlchemy 2.0**
SQLAlchemy 2.0 introduced a fully async API (`AsyncSession`, `create_async_engine`). Combined with `aiosqlite`, all database operations are non-blocking, which keeps FastAPI's event loop free and maximises concurrency.

**2. Declarative models keep schema close to code**
Defining `User` and `Post` as Python classes (via `DeclarativeBase`) means the database schema is version-controlled alongside the application code. There's no separate migration file to remember to keep in sync.

```python
class Post(Base):
    __tablename__ = "posts"
    id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id  = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption  = Column(Text)
    url      = Column(String, nullable=False)
    ...
```

**3. Relationships with zero raw SQL**
SQLAlchemy's `relationship()` directive wires `Post → User` bidirectionally. Fetching a post's author, or all posts belonging to a user, happens through Python attribute access rather than hand-written JOINs.

**4. FastAPI Users integration**
[FastAPI Users](https://fastapi-users.github.io/fastapi-users/) ships a first-class SQLAlchemy adapter (`fastapi-users-db-sqlalchemy`). Using SQLAlchemy means the full auth stack — registration, JWT login, password reset — is handled by battle-tested library code instead of custom logic.

**5. Easy upgrade path**
Swapping SQLite for PostgreSQL in production requires changing exactly one line:
```python
# Development
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Production
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
```
The rest of the application is untouched.

---

## Project Structure

```
cloudshare-rest-api/
├── app/
│   ├── __init__.py
│   ├── app.py          # FastAPI app, route definitions
│   ├── db.py           # SQLAlchemy models, engine, session factory
│   ├── schemas.py      # Pydantic schemas (request/response validation)
│   ├── users.py        # JWT strategy, auth backend, UserManager
│   └── images.py       # ImageKit SDK initialisation
├── frontend.py         # Streamlit UI
├── main.py             # Uvicorn entry point
├── pyproject.toml      # Project metadata & dependencies
├── uv.lock             # Locked dependency tree
└── .gitignore
```

---

## Database Schema

```sql
CREATE TABLE "user" (
    id               UUID PRIMARY KEY,
    email            VARCHAR NOT NULL UNIQUE,
    hashed_password  VARCHAR NOT NULL,
    is_active        BOOLEAN DEFAULT TRUE,
    is_superuser     BOOLEAN DEFAULT FALSE,
    is_verified      BOOLEAN DEFAULT FALSE
);

CREATE TABLE posts (
    id          UUID PRIMARY KEY,
    user_id     UUID REFERENCES "user"(id) NOT NULL,
    caption     TEXT,
    url         VARCHAR NOT NULL,          -- ImageKit CDN URL
    file_type   VARCHAR NOT NULL,          -- 'image' or 'video'
    file_name   VARCHAR NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Prerequisites

- Python **3.13+**
- A free [ImageKit.io](https://imagekit.io/) account
- `pip` or [`uv`](https://github.com/astral-sh/uv) (recommended)

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/cloudshare-rest-api.git
cd cloudshare-rest-api
```

### 2. Install dependencies

```bash
# Using pip
pip install -e .

# Using uv (faster)
uv pip install -e .
```

### 3. Set your ImageKit credentials

Create a `.env` file in the project root:

```env
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_URL=https://ik.imagekit.io/your_endpoint
```

> Get your credentials from **ImageKit Dashboard → Settings → API Keys**.

---

## Running the App

### Start the backend (FastAPI)

```bash
python main.py
```

The API is now live at **http://localhost:8000**

### Start the frontend (Streamlit) — in a second terminal

```bash
streamlit run frontend.py
```

The UI opens at **http://localhost:8501**

### Browse the auto-generated API docs

| Interface | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create a new account |
| `POST` | `/auth/jwt/login` | Login and receive a JWT |
| `POST` | `/auth/jwt/logout` | Invalidate the current session |
| `GET` | `/users/me` | Return the authenticated user's profile |

### Posts

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a media file and create a post |
| `GET` | `/feed` | Return all posts, newest first |
| `DELETE` | `/posts/{post_id}` | Delete a post (owner only) |

---

##  Authentication Flow

```
User registers  →  Password hashed (argon2/bcrypt)  →  Stored in DB
     ↓
User logs in    →  JWT issued (1 hour lifetime)
     ↓
Frontend stores token in Streamlit session_state
     ↓
All API requests include:  Authorization: Bearer <token>
     ↓
Backend validates token   →  Resolves current_active_user dependency
```

The JWT secret lives in `app/users.py`. **Change this to a strong random value before deploying to production.**

---

##  ImageKit Integration

Uploaded files are streamed to ImageKit's CDN via the Python SDK. The returned CDN URL is saved to the database and served directly to clients — the application server never stores binary files.

Caption overlays are applied using ImageKit's URL-based transformation API:

```
/tr:l-text,ie-<base64_caption>,ly-N20,fs-100,co-white,bg-000000A0,l-end/
```

This encodes the caption as base64, overlays it at the bottom of the image with a semi-transparent background, and delivers it as a single optimised request.

---

## 🔧 Example cURL Requests

**Register**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "secret123"}'
```

**Login**
```bash
curl -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=you@example.com&password=secret123"
```

**Get feed**
```bash
curl http://localhost:8000/feed \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Upload a post**
```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@photo.jpg" \
  -F "caption=Hello world!"
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` on port 8000 | Run `python main.py` first |
| `Upload failed` error | Check that ImageKit credentials in `.env` are correct |
| `Module not found` | Run `pip install -e .` first |
| JWT token expired | Log out and log back in to receive a fresh token |
| Database not created | It auto-creates on first startup; ensure write permissions in the project directory |

---
