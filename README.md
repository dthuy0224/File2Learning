# File2Learning
🎯 **AI-powered learning assistant** that converts English documents into interactive learning materials.

## 🚀 Features

- **Document Processing**: Upload PDF, Word, or text documents
- **AI-Generated Content**: Quiz, flashcards, and summaries from documents
- **Personalized Learning**: Adaptive learning paths for IELTS, TOEIC, Business English
- **Spaced Repetition**: Smart flashcard review system
- **Progress Tracking**: Comprehensive learning analytics
- **Interactive Chatbot**: AI assistant for vocabulary and grammar explanations

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM with Alembic migrations
- **LangChain** - LLM orchestration
- **OpenAI API** - AI content generation
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
# Start PostgreSQL and all services
docker-compose up -d

# Or start only database first
docker-compose up postgres -d
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

# Start backend
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

## 📈 Development Roadmap

- [x] Week 1: Project setup and infrastructure
- [ ] Week 2: Database design and core API
- [ ] Week 3: Document processing pipeline
- [ ] Week 4: AI integration and content generation
- [ ] Week 5: Frontend foundation
- [ ] Week 6: Interactive learning features
- [ ] Week 7: Advanced features and analytics
- [ ] Week 8: Testing and deployment


