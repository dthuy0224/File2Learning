# File2Learning

AI-powered learning platform that transforms documents into interactive learning materials with quizzes, flashcards, and intelligent chatbot assistance.

## ✨ Key Features

- **Smart Document Processing** - Upload PDFs, Word docs, or text files for instant analysis
- **AI Content Generation** - Auto-generate quizzes, flashcards, and summaries using Ollama
- **Interactive Learning** - Spaced repetition system with progress tracking
- **AI Chatbot Assistant** - Real-time help with vocabulary and grammar
- **100% Offline** - Local AI processing, no API costs or internet required

## 🛠️ Tech Stack

**Backend:** FastAPI · PostgreSQL · SQLAlchemy · Ollama · Redis · Celery  
**Frontend:** React · TypeScript · Tailwind CSS · shadcn/ui

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ · Node.js 18+ · Docker (recommended)

### Option 1: Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Access application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

### Option 2: Manual Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 📚 API Examples

```bash
# Test AI connection
curl http://localhost:8000/api/v1/ai/test-connection

# Generate quiz from document
curl -X POST "http://localhost:8000/api/v1/ai/{DOCUMENT_ID}/generate-quiz?num_questions=5"

# Generate flashcards
curl -X POST "http://localhost:8000/api/v1/ai/{DOCUMENT_ID}/generate-flashcards?num_cards=10"
```

## 📁 Project Structure

```
File2Learning/
├── backend/          # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # AI & business logic
│   │   └── tasks/    # Celery background jobs
│   └── tests/
├── frontend/         # React + TypeScript
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
└── docker-compose.yml
```

## 🔧 Development

```bash
# Run tests
cd backend && python -m pytest

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Check services
docker-compose ps
```

## 📄 License

MIT License - see LICENSE file for details
