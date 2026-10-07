# Restaurant Bilingual Voice Call Assistant API

## Phase 2 Setup

### 1. MongoDB Requirement & Local Setup
This project requires MongoDB. You can run MongoDB locally using Docker, or use MongoDB Atlas.
To run locally with Docker:
`docker run -d -p 27017:27017 --name mongodb mongo:latest`

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in the values.
```env
APP_NAME=Restaurant Voice Agent API
APP_ENV=development
LOG_LEVEL=INFO
PORT=8000
CORS_ORIGINS=http://localhost:3000

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=restaurant_voice_assistant
```

### 3. Start the Backend
Activate the virtual environment and run the server:
```bash
python -m uvicorn app.main:app --reload
```

### 4. Database Seed
To populate the fictional demo data:
```bash
set PYTHONPATH=.
python -m app.db.seed
```

### 5. Running Tests
Tests use a separate `restaurant_voice_assistant_test` database.
```bash
set PYTHONPATH=.
pytest
```

### 6. Code Quality (Ruff & Mypy)
```bash
ruff check .
mypy .
```
