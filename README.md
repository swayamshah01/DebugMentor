# DebugMentor 🧠⚡

> An AI-powered code debugging assistant for computer science students — detect bugs, run test cases, and receive progressive hints instead of direct answers.

## Project Structure

```
DebugMentor/
├── DebugMentor/        # React 18 + Monaco Editor frontend (Vite + Tailwind CSS)
└── backend/            # FastAPI + PostgreSQL backend (Phase 1 skeleton)
```

## Tech Stack

### Frontend
- **React 18** + Vite
- **Monaco Editor** (`@monaco-editor/react`) — VS Code engine
- **Tailwind CSS v4**
- **Axios** (API calls, currently mocked)

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL 15** + **SQLAlchemy 2.x** ORM
- **Alembic** — database migrations
- **Uvicorn** — ASGI server

## Getting Started

### Frontend
```bash
cd DebugMentor
npm install
npm run dev         # → http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # fill in your DB credentials
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

## Features (Phase 1)

- 🎨 Dark/Light theme toggle with Monaco integration
- ⚡ Focused Mode (function-only) ↔ Full Boilerplate toggle
- 🧠 Code-aware mock analysis engine (5 bug scenarios)
- 💡 Progressive hint system (H1 → H2 → Solution modal)
- 🧪 Test case table with pass/fail status
- 🖥️ Terminal-style run output panel
- 🗂️ Language switcher: Python, C++, Java, JavaScript

## Phase 2 Roadmap

- [ ] Real code execution (sandboxed via Docker)
- [ ] LLM-powered hint generation (OpenAI / Gemini)
- [ ] AST-based static analysis
- [ ] JWT authentication
- [ ] Personalized learning profiles
