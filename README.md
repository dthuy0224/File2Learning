# File2Learning

AI-powered learning platform that transforms documents into interactive learning materials with quizzes, flashcards, and intelligent chatbot assistance.

## ✨ Key Features

- **Smart Document Processing** - Upload PDFs, Word docs, or text files for instant analysis
- **AI Content Generation** - Auto-generate quizzes, flashcards using Google Gemini & Groq (FREE & Fast)
- **Interactive Learning** - Spaced repetition system with progress tracking
- **AI Chatbot Assistant** - Real-time help with vocabulary and grammar
- **FREE AI** - Google Gemini + Groq API, zero cost for students

## 🛠️ Tech Stack

**Backend:** FastAPI · PostgreSQL · SQLAlchemy · Redis · Celery  
**AI:** Google Gemini · Groq (Multi-provider, 100% FREE)  
**Frontend:** React · TypeScript · Tailwind CSS · shadcn/ui

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ · Node.js 18+ · Docker (recommended)

### Step 1: Get FREE AI API Keys (5 minutes)

**🎓 All services are 100% FREE for students!**

1. **Gemini API** (Primary, FREE 1,500/day):
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google → Create API Key
   - Copy the key

2. **Groq API** (Backup, FREE 14,400/day):
   - Visit: https://console.groq.com/keys
   - Sign up → Create API Key
   - Copy the key

### Step 2: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys:
# GEMINI_API_KEY=your_actual_gemini_key_here
# GROQ_API_KEY=your_actual_groq_key_here
```

### Step 3: Start Application

**Option 1: Docker (Recommended)**
```bash
# Start all services
docker-compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000

# Test AI connection
curl http://localhost:8000/api/v1/ai/test-connection
```

**Option 2: Manual Setup**
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your API keys to .env

python -m alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**📖 Detailed Setup Guide:** See [backend/AI_SETUP_GUIDE.md](backend/AI_SETUP_GUIDE.md)

## 📚 API Examples

```bash
# Test AI connection (returns active provider)
curl http://localhost:8000/api/v1/ai/test-connection

# Check AI usage statistics
curl http://localhost:8000/api/v1/ai/stats

# Generate quiz from document
curl -X POST "http://localhost:8000/api/v1/ai/{DOCUMENT_ID}/generate-quiz?num_questions=5"

# Generate flashcards (auto-uses Gemini/Groq)
curl -X POST "http://localhost:8000/api/v1/ai/{DOCUMENT_ID}/generate-flashcards?num_cards=10"

# Chat with document
curl -X POST "http://localhost:8000/api/v1/ai/{DOCUMENT_ID}/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain this document"}'
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
