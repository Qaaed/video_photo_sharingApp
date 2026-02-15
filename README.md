# 📸 Video & Photo Sharing API

A robust, asynchronous REST API built with **FastAPI** that allows users to upload, view, and manage photos and videos. It leverages **ImageKit.io** for cloud media storage and optimization, backed by a local **SQLite** database for metadata management.

## Features

- **Media Upload:** Upload photos and videos directly to ImageKit.io via the API.
- **Smart Classification:** Automatically detects if a file is an `image` or `video` and stores the type.
- **Asynchronous Core:** Built on top of `asyncio`, `aiosqlite`, and SQLAlchemy 2.0 (Async) for high-performance, non-blocking operations.
- **Feed Generation:** Retrieve a chronological feed of all uploaded media with metadata.
- **Management:** Delete posts securely by ID (removes record from the local database).

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** SQLite (via `aiosqlite` driver)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Media Storage:** [ImageKit.io](https://imagekit.io/)
- **Package Manager:** [uv](https://github.com/astral-sh/uv) (Recommended) or pip
- **Language:** Python 3.10+

