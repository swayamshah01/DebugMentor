# DebugMentor

DebugMentor is an interview-prep coding platform for curated DSA practice.

It gives the user a focused problem workspace with:
- curated pattern-based questions
- Monaco code editor
- visible testcase checks on `Run`
- official visible + hidden verification on `Submit`
- progressive hints
- learning-profile and streak-style progress feedback

The current stack is:
- `React + Vite + Monaco Editor` frontend
- `FastAPI + SQLAlchemy + PostgreSQL` backend
- optional `Redis` for hint state / caching
- optional `Gemini` for richer hint generation

## What The App Does

The product flow is:

1. Sign in with `email + password`
2. Open the pattern explorer
3. Choose a DSA pattern
4. Open a curated question
5. Write code in the editor
6. Click `Run` to check against visible sample tests
7. Click `Submit` to grade against the full official set, including hidden tests
8. Use hints and progress tracking to iterate

## Current Features

### Practice Workspace
- Curated DSA problem bank grouped by pattern
- Problem statement, constraints, and examples
- Monaco editor with Python / JavaScript / C++ / Java support in the UI
- Simple LeetCode-style split layout
- Visible testcase panel
- Result panel
- Progressive hints panel

### Evaluation Flow
- `Run` checks visible tests only for curated problems
- `Submit` checks full official tests
- Wrong output detection
- Runtime error detection
- Timeout detection
- Empty output detection
- AST-based static analysis

### Hints
- Progressive hints
- More realistic fallback hints even when LLM output is missing or weak
- Reference solution reveal
- Hint level tracking

### Learning / Engagement
- Submission history
- Weak-pattern tracking
- Pass rate
- Current streak
- Recent trend strip

### Auth / Data
- JWT auth
- Email-based login/register
- PostgreSQL persistence
- Curated content seeding on backend startup

## Repo Structure

```text
DebugMentor/
├── DebugMentor/              # Frontend (React + Vite)
│   ├── src/
│   └── package.json
├── backend/                  # Backend (FastAPI)
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── seed_data.py
│   └── requirements.txt
└── README.md
```

## Tech Stack

### Frontend
- React
- Vite
- Monaco Editor
- Axios
- CSS-based custom UI

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Google Gemini API

## Requirements

### Core
- Node.js 18+
- npm
- Python 3.11+
- PostgreSQL

### Optional but Recommended
- Redis
- Gemini API key

### Language Runtimes
For multi-language execution support on your local machine:
- Python runtime must be available
- JavaScript runtime should be available via `node`
- C++ requires `g++`
- Java requires `java` and `javac`

If Java or C++ is missing on your machine, those languages will fail at execution time until the compiler/runtime is installed.

## Backend Setup

From the repo root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example` and replace the placeholder values with your own local credentials.

Important:
- use your own PostgreSQL password and database
- use your own `SECRET_KEY`
- use your own `GEMINI_API_KEY` if you want LLM hints
- `REDIS_URL` is optional

Run migrations:

```powershell
alembic upgrade head
```

Start backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Backend docs:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Frontend Setup

From the repo root:

```powershell
cd DebugMentor
npm install
npm run dev
```

Frontend local URL:

- [http://127.0.0.1:5173](http://127.0.0.1:5173)

## Database Notes

The backend seeds curated DSA content on startup by default.

That means:
- patterns are created automatically
- curated problems are inserted automatically
- visible and hidden tests are stored in the database

If you add or change curated seed content, restart the backend so the seed sync runs again.

## Run vs Submit

This is the intended user experience:

### Run
- fast practice check
- uses visible testcases only
- should help the user iterate quickly
- does not create a graded submission record

### Submit
- official verification step
- uses visible + hidden tests
- persists the submission
- updates learning profile and progress
- generates hints payload

This separation is intentional. A user can pass the visible tests on `Run` and still fail `Submit` if hidden edge cases break the solution.

## Environment Variables

Expected backend environment values:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/your_db
SECRET_KEY=replace_with_a_long_random_secret
DEBUG=True
GEMINI_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379
```

## API Overview

Main routes:

- `POST /api/register`
- `POST /api/login`
- `GET /api/patterns`
- `GET /api/patterns/{pattern_id}/problems`
- `GET /api/problems/{problem_id}`
- `POST /api/run`
- `POST /api/submit`
- `POST /api/hint`
- `GET /api/profile/{user_id}`

## Tests

Backend tests live in:

- `backend/tests`

Typical command:

```powershell
set PYTHONPATH=backend
pytest backend/tests
```

If your shell cannot launch the local virtualenv interpreter correctly, run pytest from a Python installation that can import the `backend/app` package with `PYTHONPATH=backend`.

Frontend build check:

```powershell
cd DebugMentor
npm run build
```

## Current Status

What is already working:
- email/password auth
- curated patterns and questions
- problem workspace
- visible test checks on `Run`
- official grading on `Submit`
- wrong output classification
- hints flow
- streak / pass-rate style profile feedback

What still depends on local machine setup:
- Java execution
- C++ execution
- Redis-backed hint state
- Gemini-backed high-quality hint generation

## Troubleshooting

### Frontend shows no questions
- make sure backend is running
- make sure database is reachable
- make sure seed content completed on startup

### CORS problems
- backend is configured to allow all origins in local development
- restart backend after config changes

### Java fails
- install a JDK
- verify:

```powershell
java -version
javac -version
```

### C++ fails
- install a compiler such as `g++`
- verify:

```powershell
g++ --version
```

### Redis warning on startup
- safe to ignore for local development
- hints will still work, but cached / progressive state may be reduced

## Suggested Local Run Order

1. Start PostgreSQL
2. Start Redis if you want caching/hint state
3. Start backend
4. Start frontend
5. Open frontend in browser
6. Register an account
7. Choose a pattern and problem
8. Run visible tests
9. Submit for full verification

## Demo Checklist

For a clean demo:
- register a new user
- open a curated problem like Two Sum
- run an incomplete solution and show visible testcase failure
- submit the same code and show full failure report
- reveal hints progressively
- fix the code and submit again
- show streak / pass rate / profile trend

## License

This repository currently does not declare a license.
