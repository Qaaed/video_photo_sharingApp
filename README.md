# CloudShare REST API

[![Python](https://img.shields.io/badge/Python-3.13+-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

A modern, secure cloud storage and sharing platform built with **FastAPI** and **Streamlit**. Upload, manage, and share images and videos with ease using cloud-powered infrastructure.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication with email/password registration
- **Media Upload**: Upload images (PNG, JPG, JPEG) and videos (MP4, AVI, MOV, MKV, WEBM)
- **Cloud Storage**: Automatic cloud storage via ImageKit integration
- **Social Feed**: Browse shared media from all users
- **Post Management**: Create, view, and delete your own posts
- **Real-time Sync**: Live updates with automatic page refresh
- **Responsive UI**: Modern dark-themed interface with Streamlit
- **Async Operations**: Fully async backend for high performance

## 🛠️ Tech Stack

### Backend

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - ORM for database management
- **FastAPI-Users** - Authentication and user management
- **SQLite + aiosqlite** - Async database support
- **Uvicorn** - ASGI application server
- **ImageKit** - Cloud image/video hosting and optimization

### Frontend

- **Streamlit** - Rapid UI development for data applications
- **Python Requests** - HTTP client for API calls

### Database

- **SQLite** - Lightweight, file-based relational database
- **SQLAlchemy ORM** - Type-safe database queries

## 📋 Prerequisites

- Python 3.13 or higher
- ImageKit account (for cloud storage)
- `pip` or `uv` package manager

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cloudshare-rest-api.git
cd cloudshare-rest-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
# or with uv:
uv pip install -e .
```

## ⚙️ Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```env
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_URL=https://ik.imagekit.io/your_endpoint
```

### 2. Get ImageKit Credentials

1. Sign up at [ImageKit.io](https://imagekit.io/)
2. Go to Settings → API Keys
3. Copy your Private Key, Public Key, and URL Endpoint
4. Add them to your `.env` file

## 🚀 Running the Application

### Start Backend Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Start Frontend (in a separate terminal)

```bash
streamlit run frontend.py
```

The UI will open at `http://localhost:8501`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication

| Method | Endpoint          | Description                  |
| ------ | ----------------- | ---------------------------- |
| `POST` | `/auth/register`  | Register new user            |
| `POST` | `/auth/jwt/login` | Login user and get JWT token |
| `POST` | `/auth/logout`    | Logout user                  |
| `GET`  | `/users/me`       | Get current user information |

### Posts

| Method   | Endpoint           | Description                              |
| -------- | ------------------ | ---------------------------------------- |
| `POST`   | `/upload`          | Upload a new post with media and caption |
| `GET`    | `/feed`            | Get all posts (most recent first)        |
| `DELETE` | `/posts/{post_id}` | Delete a post (owner only)               |

## 📁 Project Structure

```
cloudshare-rest-api/
├── app/
│   ├── __init__.py
│   ├── app.py              # FastAPI application & routes
│   ├── db.py               # Database models & session management
│   ├── schemas.py          # Pydantic schemas for validation
│   ├── users.py            # Authentication & user management
│   └── images.py           # ImageKit configuration
├── frontend.py             # Streamlit UI application
├── main.py                 # Application entry point
├── .env                    # Environment variables (create this)
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Project dependencies & metadata
└── README.md               # This file
```

## 💾 Database Schema

### User Table

```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY,
  email VARCHAR NOT NULL UNIQUE,
  hashed_password VARCHAR NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  is_superuser BOOLEAN DEFAULT FALSE
);
```

### Post Table

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  caption TEXT,
  url VARCHAR NOT NULL,
  file_type VARCHAR NOT NULL,  -- 'image' or 'video'
  file_name VARCHAR NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 Authentication Flow

1. User registers with email and password
2. Password is hashed and stored securely
3. On login, user receives a JWT token
4. Token is stored in Streamlit session state
5. All API requests include `Authorization: Bearer {token}` header
6. Backend validates token for protected endpoints

## 🎨 UI Features

### Login Page

- Email and password input
- Toggle between login and signup
- Form validation

### Cloud Feed

- View all shared media
- See author and creation date
- Delete your own posts
- Image and video support with caption overlays

### Upload & Share

- Drag-and-drop file upload
- Add captions to media
- Real-time upload status
- Automatic redirect to feed

## 🔧 Configuration Options

### JWT Settings

- **Token Lifetime**: 3600 seconds (1 hour)
- **Secret Key**: Configure in `app/users.py`

### Supported Media Types

- **Images**: PNG, JPG, JPEG
- **Videos**: MP4, AVI, MOV, MKV, WEBM

### Database

- **Type**: SQLite (file-based)
- **Location**: `test.db` (auto-created)
- **Async Support**: Yes (aiosqlite)

## 📝 Example API Usage

### Register User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

### Get Current User

```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Feed

```bash
curl -X GET "http://localhost:8000/feed" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🚨 Troubleshooting

### Issue: "Upload failed" error

**Solution**: Make sure the backend server is running and ImageKit credentials are correctly set in `.env`

### Issue: Connection refused on localhost:8000

**Solution**: Start the backend with `python main.py` in the project root

### Issue: Module not found errors

**Solution**: Ensure dependencies are installed: `pip install -e .`

### Issue: JWT token expired

**Solution**: Logout and login again to get a new token





---

