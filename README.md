# AI Learning Material Generator

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

### Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd ai-learning-material

# 2. Start with Docker (recommended)
docker-compose up -d

# 3. Or manual setup:
# Backend
cd backend
python -m venv venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
ai-learning-material/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── crud/         # Database operations
│   │   └── utils/        # Helper functions
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


