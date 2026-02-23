# DontEatCancer

Research repository aggregating scientific evidence on food chemicals and cancer risk from Chinese, Middle Eastern, and European sources.

## What It Does

DontEatCancer collects, translates, and organizes peer-reviewed research papers about food additives and their links to cancer. It focuses on sources often overlooked in English-language reviews — Chinese, Arabic, and European journals.

- **106 food additives** seeded with multilingual names (English, Chinese, Arabic, French, German)
- **AI-powered extraction** from scientific papers using Claude API
- **RIS file import** from EBSCO, Scopus, Web of Science, PubMed
- **Multilingual search query generator** for academic databases
- **Ingredient-by-ingredient risk assessment** with evidence tracking

## Tech Stack

| Layer    | Technology                                    |
| -------- | --------------------------------------------- |
| Backend  | Python 3.11+ / FastAPI / SQLAlchemy 2 / Alembic |
| Frontend | Next.js 16 / React 19 / TypeScript / Tailwind CSS v4 |
| Database | SQLite (default) or PostgreSQL 16              |
| AI       | Claude API (Sonnet) for paper extraction/translation |
| CLI      | Typer for pipeline commands                    |
| Parsing  | rispy for RIS file import                      |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Clone the repo

```bash
git clone https://github.com/rezanating-dot-com/DontEatCancer.git
cd DontEatCancer
```

### 2. Set up environment variables

```bash
cp .env.example backend/.env
```

Edit `backend/.env` and add your API key:

```
DEEPSEEK_API_KEY=your-key-here
```

### 3. Set up the backend

```bash
cd backend

# Create virtual environment and install dependencies
uv venv .venv --python 3.12
uv pip install -e ".[postgres,dev]" --python .venv/bin/python

# Seed the database with food additives
.venv/bin/python scripts/seed_ingredients.py
```

The app uses SQLite by default — no database server needed. If you want PostgreSQL instead, see [Using PostgreSQL](#using-postgresql).

### 4. Set up the frontend

```bash
cd frontend
npm install
```

### 5. Run the app

Start both servers (in separate terminals):

```bash
# Terminal 1 — Backend (http://localhost:8000)
cd backend
.venv/bin/uvicorn app.main:app --reload

# Terminal 2 — Frontend (http://localhost:3000)
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

## API Endpoints

| Method | Endpoint                          | Description                    |
| ------ | --------------------------------- | ------------------------------ |
| GET    | `/api/v1/health`                  | Health check                   |
| GET    | `/api/v1/stats`                   | Ingredient and evidence counts |
| GET    | `/api/v1/ingredients`             | List all ingredients           |
| GET    | `/api/v1/ingredients/categories`  | List categories                |
| GET    | `/api/v1/ingredients/{slug}`      | Ingredient detail              |
| GET    | `/api/v1/ingredients/{slug}/evidence` | Evidence for an ingredient |
| GET    | `/api/v1/evidence`                | List all evidence              |
| GET    | `/api/v1/evidence/{id}`           | Evidence detail                |
| GET    | `/api/v1/evidence/review-queue`   | Papers needing review          |
| PATCH  | `/api/v1/evidence/{id}/review`    | Submit a review                |
| GET    | `/api/v1/search?q=...`            | Search ingredients & evidence  |
| POST   | `/api/v1/upload/ris`              | Upload RIS file                |
| POST   | `/api/v1/upload/text`             | Upload raw text                |
| POST   | `/api/v1/queries/generate`        | Generate search queries        |
| GET    | `/api/v1/processing/jobs`         | List processing jobs           |
| POST   | `/api/v1/processing/jobs/{id}/start` | Start processing a job      |

Interactive API docs available at **http://localhost:8000/docs**.

## CLI Tools

The pipeline CLI helps generate search queries and process imported papers.

```bash
cd backend

# Generate multilingual search queries for an ingredient
.venv/bin/python -m pipeline.cli query "sodium nitrite"
.venv/bin/python -m pipeline.cli query "sodium nitrite" --database scopus
.venv/bin/python -m pipeline.cli query "sodium nitrite" --no-ai --json

# Parse a RIS file
.venv/bin/python -m pipeline.cli parse path/to/file.ris

# Run the full processing pipeline (parse + AI extract + save to DB)
.venv/bin/python -m pipeline.cli process path/to/file.ris
.venv/bin/python -m pipeline.cli process path/to/file.ris --dry-run
.venv/bin/python -m pipeline.cli process path/to/file.ris --limit 5
```

## Frontend Pages

| Route                      | Description                           |
| -------------------------- | ------------------------------------- |
| `/`                        | Home — stats, search, category browse |
| `/ingredients`             | Ingredient list with filters          |
| `/ingredients/{slug}`      | Ingredient detail with linked evidence |
| `/evidence/{id}`           | Individual paper/evidence detail      |
| `/search`                  | Full-text search                      |
| `/tools/query-generator`   | Generate academic database queries    |
| `/tools/upload`            | Upload RIS files or paste text        |

## Using PostgreSQL

If you prefer PostgreSQL over SQLite:

```bash
# Start PostgreSQL via Docker
docker compose up -d

# Or use an existing PostgreSQL server — create the database:
sudo -u postgres psql -c "CREATE USER donteatcancer WITH PASSWORD 'donteatcancer';"
sudo -u postgres psql -c "CREATE DATABASE donteatcancer OWNER donteatcancer;"
sudo -u postgres psql -d donteatcancer -c "GRANT ALL ON SCHEMA public TO donteatcancer;"

# Set the database URL in backend/.env
echo 'DATABASE_URL=postgresql://donteatcancer:donteatcancer@localhost:5432/donteatcancer' >> backend/.env

# Run migrations
cd backend
.venv/bin/python -m alembic upgrade head

# Seed data
.venv/bin/python scripts/seed_ingredients.py
```

## Project Structure

```
DontEatCancer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings (env vars)
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models/              # DB models (ingredient, evidence)
│   │   ├── routers/             # API route handlers
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── services/            # Business logic
│   ├── pipeline/
│   │   ├── cli.py               # Typer CLI commands
│   │   ├── ai_processor.py      # Claude API integration
│   │   ├── query_generator.py   # Multilingual query builder
│   │   └── ris_parser.py        # RIS file parser
│   ├── alembic/                 # Database migrations
│   ├── scripts/
│   │   └── seed_ingredients.py  # Seed 95+ food additives
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # React components
│   │   └── lib/                 # API client & types
│   └── package.json
└── docker-compose.yml           # PostgreSQL (optional)
```

## License

This project is for research and educational purposes.
