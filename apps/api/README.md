# Restaurant Voice Agent API

## Requirements
Python 3.11+

## Setup

```bash
cd apps/api
python -m venv .venv
```

### Windows
```bash
.venv\Scripts\activate
```

### Linux/macOS
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run server:
```bash
uvicorn app.main:app --reload --port 8000
```

Test:
```bash
pytest
```

Lint:
```bash
ruff check .
```

Type check:
```bash
mypy app
```

Health check:
http://localhost:8000/api/health

Swagger:
http://localhost:8000/docs
