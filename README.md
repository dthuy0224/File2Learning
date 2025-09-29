# File2Learning
🎯 **AI-powered learning assistant** that converts English documents into interactive learning materials.

## 🚀 Features

- **Document Processing**: Upload PDF, Word, or text documents
- **AI-Generated Content**: Quiz, flashcards, and summaries from documents (powered by Ollama)
- **Personalized Learning**: Adaptive learning paths for IELTS, TOEIC, Business English
- **Spaced Repetition**: Smart flashcard review system
- **Progress Tracking**: Comprehensive learning analytics
- **Interactive Chatbot**: AI assistant for vocabulary and grammar explanations
- **Local AI Processing**: No API costs, works offline with Ollama

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM with Alembic migrations
- **Ollama** - Local AI for content generation (free)
- **Redis** - Caching and session storage

### Frontend
- **React** + **TypeScript** - Modern web framework
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful component library
- **React Query** - Server state management

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Docker)

### Database Setup

#### Using Docker (Recommended)
```bash
# Start all services (including Ollama AI and Celery worker)
docker-compose up -d

# Or start services individually
docker-compose up postgres ollama redis -d  # Database, AI, and Redis
docker-compose up celery-worker -d          # Background processing worker
docker-compose up backend -d                # Backend API
docker-compose up frontend -d               # Frontend

# Check service status
docker-compose ps
```

#### Manual Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings (OAuth credentials, API keys, etc.)

python -m alembic upgrade head
python scripts/seed_data.py  # Optional: seed with sample data

# Test Celery configuration
python scripts/test_celery.py

# Start services (includes Redis, Celery worker, and backend)
python scripts/start_services.py

# OR start individually:
# Start Redis (required for Celery)
docker-compose up redis -d

# Start Celery worker for background processing
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2

# Start backend API (separate terminal)
uvicorn app.main:app --reload

# Frontend setup (separate terminal)
cd frontend
npm install
npm run dev
```

### Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd File2Learning

# 2. Start with Docker (recommended)
docker-compose up -d

# 3. Or manual setup:
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head  # Setup database
python scripts/seed_data.py     # Optional: seed with sample data
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
File2Learning/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── crud/         # Database operations
│   │   └── utils/        # Helper functions
│   ├── scripts/          # Database and utility scripts
│   ├── tests/            # Backend tests
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   └── utils/        # Helper functions
│   └── package.json
├── docker-compose.yml    # Development environment
├── scripts/              # Database initialization scripts
└── README.md
```

## 🤖 AI Features API

Once the system is running with Ollama, you can use these AI-powered endpoints:

```bash
# Test AI connection
curl http://localhost:8000/api/v1/ai/test-connection

# Generate quiz from document (replace DOCUMENT_ID)
curl -X POST "http://localhost:8000/api/v1/ai/DOCUMENT_ID/generate-quiz?quiz_type=mixed&num_questions=5"

# Generate flashcards from document
curl -X POST "http://localhost:8000/api/v1/ai/DOCUMENT_ID/generate-flashcards?num_cards=10"

# Generate summary from document
curl -X POST "http://localhost:8000/api/v1/ai/DOCUMENT_ID/generate-summary?max_length=300"

# Get available AI models
curl http://localhost:8000/api/v1/ai/models
```

### 🧪 Testing AI Integration

```bash
# Run AI integration test
cd backend
python backend/tests/test_ai_integration.py
```

## 📈 Development Roadmap

- [x] Week 1: Project setup and infrastructure
- [x] Week 2: Database design and core API
- [x] Week 3: Document processing pipeline
- [x] Week 4: AI integration and content generation (Ollama)
- [ ] Week 5: Frontend integration with AI features
- [ ] Week 6: Interactive learning features
- [ ] Week 7: Advanced features and analytics
- [ ] Week 8: Testing and deployment


