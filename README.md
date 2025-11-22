# File2Learning 📚🚀

> Transform any document into a personalized English learning experience powered by AI.

**File2Learning** is an AI-powered intelligent learning platform that transforms documents (PDF, DOCX, TXT) into interactive learning tools. The system leverages the power of LLMs (Gemini, Groq) to automatically generate Flashcards, Quizzes, and provides an AI Chatbot assistant for real-time learning support.

**Note**: This is an academic project developed as our final subject project, not intended for commercial purposes.

---

## ✨ Key Features

### 📄 **Smart Document Processing**
- Upload and process multiple formats (PDF, DOCX, TXT)
- AI analyzes content quality and difficulty level
- Automatic extraction of important vocabulary
- AI-powered intelligent summarization
- Reading modes: Normal, Highlight Vocabulary, Key Points

### 🧠 **AI Content Generation**
- Integration with **Google Gemini** and **Groq**
- Automatically create Flashcards from documents
- Generate diverse Quizzes (MCQ, Fill-in-blank, Comprehension)
- AI-powered explanations for each question

### 💬 **AI Chatbot Assistant**
- Direct Q&A with document content
- Detailed vocabulary and grammar explanations
- Context-aware conversations
- 24/7 learning support

### 🎯 **Learning Goals Management**
- Create personalized learning goals (IELTS 7.0, 500 vocabulary words, etc.)
- Track progress with visual dashboards
- Milestone-based achievements
- Link documents and materials to specific goals
- Real-time progress analytics

### 📅 **Intelligent Study Schedules**
- AI-generated study plans based on goals
- Flexible scheduling (time-based, goal-based, exam prep)
- Auto-adjustment based on performance
- Daily task breakdowns with time estimates
- Streak tracking and gamification

### 📖 **Today's Plan**
- Daily task list with priorities
- Progress tracking for each activity
- Time management with estimated durations
- Goal-linked activities
- Motivational elements and rewards

### ✨ **AI-Powered Recommendations**
- Personalized content suggestions
- Weakness identification and targeted practice
- Schedule optimization recommendations
- Learning path adjustments
- Smart content matching based on interests

### 🎴 **Interactive Learning Tools**
- **Flashcards**: Spaced repetition system
- **Quizzes**: Multiple types with immediate feedback
- **Annotations**: Highlight and take notes
- **Audio Pronunciation**: Text-to-speech support
- **Progress Analytics**: Comprehensive learning statistics

### 🔐 **Authentication & Security**
- Multiple authentication methods: Email, OAuth 2.0
- Login support via Google, Microsoft, GitHub
- JWT-based authentication
- Secure password hashing

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0 & Alembic
- **Async Tasks**: Celery + Redis (Background job processing)
- **AI Integrations**: 
  - Google Generative AI (Gemini)
  - Groq SDK
- **Authentication**: JWT, OAuth (Authlib)
- **Server**: Uvicorn (ASGI)

### **Frontend**
- **Framework**: React 18 with Vite + TypeScript
- **State Management**: 
  - TanStack Query (React Query) - Server state
  - Zustand - Client state
- **UI Components**: 
  - shadcn/ui
  - Tailwind CSS
  - Framer Motion (Animations)
  - Lucide React (Icons)
- **Visualizations**: 
  - Recharts
  - React Calendar Heatmap
- **Routing**: React Router v6

### **DevOps & Infrastructure**
- **Containerization**: Docker & Docker Compose
- **Database Migrations**: Alembic (Auto-migration on startup)
- **Task Queue**: Celery with Redis backend
- **Health Checks**: Built-in health monitoring
- **Auto-Deployment Fix**: Schema validation and migration automation

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    FILE2LEARNING ECOSYSTEM                   │
└─────────────────────────────────────────────────────────────┘

1. UPLOAD DOCUMENT
   ↓
   → AI Processing (extraction, quality check, difficulty analysis)
   → Background Task (Celery Worker)
   ↓

2. LEARNING GOALS (Foundation)
   → User defines: "IELTS 7.0 in 3 months"
   → Creates milestones and tracking
   ↓

3. STUDY SCHEDULE (Execution Plan)
   → AI generates: Weekly plan, daily time blocks
   → Auto-links to goals
   ↓

4. TODAY PLAN (Daily Action)
   → Shows specific tasks for today
   → Tracks completion in real-time
   → Updates progress automatically
   ↓

5. RECOMMENDATIONS (Adaptive Learning)
   → AI analyzes performance
   → Suggests adjustments, new content, schedule changes
   ↓
   └──→ Feedback Loop → Updates Goals & Schedules
```

---

## 🚀 Installation & Setup Guide

### **1. System Requirements**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Recommended)
- Git
- Node.js 18+ (if running frontend separately)
- Python 3.10+ (if running backend separately)

### **2. Clone the Repository**
```bash
git clone https://github.com/dthuy0224/file2learning.git
cd file2learning
```

### **3. Environment Configuration**

#### Copy the example file:
```bash
cp .env.example .env
```

#### Update `.env` with important information:

| Variable | Description | Notes |
|----------|-------------|-------|
| `GEMINI_API_KEY` | Google Gemini API Key | **Required** - Get at [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `GROQ_API_KEY` | Groq API Key | Optional (Backup for Gemini, very fast) |
| `DATABASE_URL` | Database connection URL | Default: `postgresql+psycopg2://app_user:app_password@postgres:5432/file2learning` |
| `REDIS_URL` | Redis connection URL | Default: `redis://redis:6379/0` |
| `SECRET_KEY` | JWT encryption key | **Should be changed for production** |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | If using Google login |
| `MICROSOFT_CLIENT_ID` | Microsoft OAuth ID | If using Microsoft login |
| `GITHUB_CLIENT_ID` | GitHub OAuth ID | If using GitHub login |
| `ALLOWED_HOSTS` | CORS origins | Default: `http://localhost:3000` |

### **4. Running with Docker (Recommended)**

The system includes an **Auto-Deployment Fix** mechanism:
- ✅ Automatically waits for Database to be ready
- ✅ Runs Migrations automatically
- ✅ Checks Schema integrity
- ✅ Health checks for all services
```bash
# Build and run the entire system
docker-compose up -d --build

# View logs to monitor startup process
docker-compose logs -f backend
```

**After startup:**
- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000/docs
- 📊 **API Health Check**: http://localhost:8000/health
- 🤖 **AI Connection Test**: http://localhost:8000/api/v1/ai/test-connection

#### Check running containers:
```bash
docker-compose ps
```

#### Stop the system:
```bash
docker-compose down
```

---

## 🧪 Manual Setup (Development Mode)

<details>
<summary>👉 <strong>Click to view manual setup instructions</strong></summary>

### **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database and redis using Docker
docker-compose up postgres redis -d

# Wait for database to be ready
python scripts/wait_for_db.py

# Run migrations
alembic upgrade head

# Verify schema
python check_schema.py

# Start Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Celery Worker (Background Tasks)**

Open new terminal in `backend` directory:
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Windows (Requires pool=solo)
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

# Linux/Mac
celery -A app.tasks.celery_app worker --loglevel=info
```

### **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will run at**: http://localhost:5173

</details>

---

## 📂 Project Structure
```
file2learning/
├── backend/
│   ├── app/
│   │   ├── api/                    # API Endpoints (v1)
│   │   │   ├── v1/
│   │   │   │   ├── auth.py        # Authentication endpoints
│   │   │   │   ├── documents.py   # Document management
│   │   │   │   ├── flashcards.py  # Flashcard operations
│   │   │   │   ├── quizzes.py     # Quiz generation & submission
│   │   │   │   ├── goals.py       # Learning goals
│   │   │   │   ├── schedules.py   # Study schedules
│   │   │   │   └── ai.py          # AI operations
│   │   ├── core/                   # Core configurations
│   │   │   ├── config.py          # Settings management
│   │   │   ├── security.py        # JWT, password hashing
│   │   │   └── database.py        # Database connection
│   │   ├── models/                 # SQLAlchemy Models
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── flashcard.py
│   │   │   ├── quiz.py
│   │   │   ├── goal.py
│   │   │   └── schedule.py
│   │   ├── schemas/                # Pydantic Schemas
│   │   ├── services/               # Business Logic
│   │   │   ├── ai_service.py      # Gemini/Groq integration
│   │   │   ├── document_service.py
│   │   │   ├── flashcard_service.py
│   │   │   └── quiz_service.py
│   │   └── tasks/                  # Celery Background Tasks
│   │       ├── celery_app.py
│   │       └── document_tasks.py
│   ├── alembic/                    # Database Migrations
│   ├── scripts/                    # Utility Scripts
│   │   ├── init_db.py             # Database initialization
│   │   └── wait_for_db.py         # Wait for DB ready
│   ├── check_schema.py             # Schema validation
│   ├── entrypoint.sh               # Docker startup script
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI Components
│   │   │   ├── ui/                # shadcn/ui components
│   │   │   ├── ChatbotModal.tsx
│   │   │   ├── FlashcardDeck.tsx
│   │   │   └── QuizComponent.tsx
│   │   ├── pages/                  # Application Pages
│   │   │   ├── DocumentsPage.tsx
│   │   │   ├── DocumentDetailPage.tsx
│   │   │   ├── LearningGoalsPage.tsx
│   │   │   ├── StudySchedulePage.tsx
│   │   │   ├── TodayPlanPage.tsx
│   │   │   ├── RecommendationsPage.tsx
│   │   │   ├── FlashcardsPage.tsx
│   │   │   └── QuizzesPage.tsx
│   │   ├── services/               # API Integration (Axios)
│   │   │   ├── authService.ts
│   │   │   ├── documentService.ts
│   │   │   ├── flashcardService.ts
│   │   │   ├── quizService.ts
│   │   │   ├── goalService.ts
│   │   │   └── scheduleService.ts
│   │   ├── store/                  # State Management (Zustand)
│   │   ├── hooks/                  # Custom React Hooks
│   │   └── lib/                    # Utilities
│   └── package.json
│
├── scripts/                        # SQL Scripts for Docker
│   └── init.sql
├── docker-compose.yml
├── .env.example
├── DEPLOYMENT_FIXES.md             # Deployment troubleshooting guide
└── README.md
```

---

## 🔧 Deployment & Stability Mechanisms

The project has been optimized for stable deployment (details in `DEPLOYMENT_FIXES.md`):

### **1. Entrypoint Script (`entrypoint.sh`)**
Ensures correct startup sequence:
```bash
1. wait_for_db.py     → Wait for PostgreSQL to be active
2. alembic upgrade    → Automatically run latest migrations
3. check_schema.py    → Check schema integrity
4. uvicorn            → Start API server
```

### **2. Health Checks**
Docker Compose integrates health checks for:
- ✅ PostgreSQL: `pg_isready` check
- ✅ Redis: `redis-cli ping`
- ✅ Backend: HTTP health endpoint
- ✅ Celery Worker: Celery inspect ping

### **3. Auto-Migration System**
- Automatically detects schema changes
- Rollback mechanism if migration fails
- Validation before server startup

### **4. CORS Configuration**
Pre-configured `ALLOWED_HOSTS` for:
- Development: `http://localhost:3000`, `http://localhost:5173`
- Production: Environment-based configuration

---

## 📚 API Documentation

### **Authentication Endpoints**
```
POST   /api/v1/auth/register       # Register account
POST   /api/v1/auth/login          # Login
POST   /api/v1/auth/logout         # Logout
GET    /api/v1/auth/me             # Get current user info
POST   /api/v1/auth/refresh        # Refresh JWT token
GET    /api/v1/auth/google         # Google OAuth login
GET    /api/v1/auth/microsoft      # Microsoft OAuth login
GET    /api/v1/auth/github         # GitHub OAuth login
```

### **Document Management**
```
GET    /api/v1/documents                    # Get documents list
POST   /api/v1/documents/upload             # Upload new document
GET    /api/v1/documents/{id}               # Document details
PUT    /api/v1/documents/{id}               # Update document
DELETE /api/v1/documents/{id}               # Delete document
POST   /api/v1/documents/{id}/generate-summary       # Generate AI summary
POST   /api/v1/documents/{id}/extract-vocabulary    # Extract vocabulary
```

### **AI Features**
```
GET    /api/v1/ai/test-connection           # Test AI connection
POST   /api/v1/ai/documents/{id}/chat       # Chat with document
POST   /api/v1/ai/flashcards/generate       # Generate flashcards
POST   /api/v1/ai/quizzes/generate          # Generate quiz
```

### **Learning Goals**
```
GET    /api/v1/goals                        # List goals
POST   /api/v1/goals                        # Create new goal
GET    /api/v1/goals/{id}                   # Goal details
PUT    /api/v1/goals/{id}                   # Update goal
DELETE /api/v1/goals/{id}                   # Delete goal
GET    /api/v1/goals/{id}/progress          # View progress
```

### **Study Schedules**
```
GET    /api/v1/schedules                    # List schedules
POST   /api/v1/schedules                    # Create schedule
GET    /api/v1/schedules/{id}               # Schedule details
PUT    /api/v1/schedules/{id}               # Update schedule
POST   /api/v1/schedules/{id}/activate      # Activate schedule
POST   /api/v1/schedules/{id}/adjust        # Auto-adjust schedule
GET    /api/v1/schedules/active             # Get active schedule
```

### **Daily Plans**
```
GET    /api/v1/daily-plans/today            # Today's plan
GET    /api/v1/daily-plans/{date}           # Plan for specific date
POST   /api/v1/daily-plans/tasks/{id}/complete  # Complete task
GET    /api/v1/daily-plans/week             # Weekly overview
```

### **Flashcards**
```
GET    /api/v1/flashcards                   # List flashcards
POST   /api/v1/flashcards/generate          # Generate from document
GET    /api/v1/flashcards/due               # Flashcards due for review
POST   /api/v1/flashcards/{id}/review       # Review flashcard
GET    /api/v1/flashcards/stats             # Learning statistics
```

### **Quizzes**
```
POST   /api/v1/quizzes/generate             # Generate quiz
GET    /api/v1/quizzes/{id}                 # Get quiz details
POST   /api/v1/quizzes/{id}/submit          # Submit answers
GET    /api/v1/quizzes/history              # Quiz history
GET    /api/v1/quizzes/stats                # Quiz statistics
```

### **Recommendations**
```
GET    /api/v1/recommendations              # AI recommendations
POST   /api/v1/recommendations/{id}/accept  # Accept recommendation
POST   /api/v1/recommendations/{id}/dismiss # Dismiss recommendation
```

---

---

## 🎯 User Journey Example

### **First-Time User Flow:**
```
1. 📝 Sign Up / Login
   ↓
2. 🎯 Create First Goal
   → "IELTS 7.0 Writing in 3 months"
   ↓
3. 📄 Upload Document
   → Climate change article (PDF)
   → AI processes: extract text, analyze difficulty, identify vocabulary
   ↓
4. 🎴 Generate Study Materials
   → AI creates 20 flashcards
   → AI generates 10-question quiz
   ↓
5. 📅 Create Study Schedule
   → AI suggests: 45 min/day, 5 days/week
   → Links to goal automatically
   ↓
6. ✅ Start Learning
   → Opens "Today's Plan"
   → Sees 4 tasks (vocab + quiz + reading + review)
   → Clicks "Start" and begins learning
```

### **Daily Workflow:**
```
Morning (8:00 AM):
  → Open Today's Plan
  → See: 15 min vocab + 10 min quiz + 12 min reading + 8 min review
  → Complete vocab practice (8:15 AM)
  → System auto-updates progress
  
Afternoon (2:00 PM):
  → Continue with grammar quiz
  → Get immediate AI feedback
  → Review mistakes with explanations
  
Evening (9:00 PM):
  → Check daily progress: 3/4 tasks done (75%)
  → Review AI recommendations
  → Plan for tomorrow
  → Maintain 28-day streak 🔥
```

---

## 🐛 Troubleshooting

### **Common Issues:**

#### 1. **Database connection failed**
```bash
# Check if Postgres is running
docker-compose ps postgres

# View Postgres logs
docker-compose logs postgres

# Restart Postgres
docker-compose restart postgres
```

#### 2. **Migrations failed**
```bash
# Manually run migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current

# Rollback if needed
docker-compose exec backend alembic downgrade -1
```

#### 3. **Celery worker not processing tasks**
```bash
# Check Celery logs
docker-compose logs celery

# Restart Celery worker
docker-compose restart celery

# Check Redis connection
docker-compose exec redis redis-cli ping
```

#### 4. **AI API errors**
```bash
# Verify API keys
docker-compose exec backend python -c "from app.core.config import get_settings; s = get_settings(); print('Gemini:', bool(s.GEMINI_API_KEY), 'Groq:', bool(s.GROQ_API_KEY))"

# Test AI connection
curl http://localhost:8000/api/v1/ai/test-connection
```

#### 5. **Frontend can't connect to backend**
- Check `VITE_API_URL` in `.env`
- Verify CORS settings in backend `.env`
- Clear browser cache and restart frontend

---

## 🧪 Testing
```bash
# Backend unit tests
cd backend
pytest tests/ -v

# Backend with coverage
pytest tests/ --cov=app --cov-report=html

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

---


### **Development Guidelines:**
- ✅ Follow existing code style
- ✅ Write tests for new features
- ✅ Update documentation
- ✅ Keep commits atomic and well-described

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📧 Contact & Support

- 📧 **Email**: damt9362@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/dthuy0224/file2learning/issues)
---

## 🙏 Acknowledgments

- [Google AI](https://ai.google.dev/) for Gemini API
- [Groq](https://groq.com/) for ultra-fast inference
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components
- [FastAPI](https://fastapi.tiangolo.com/) community
- [React](https://react.dev/) and [Vite](https://vitejs.dev/) teams
- All contributors and users of the project

---

## 👥 Team

This project was developed as a final subject project by our team. We hope it serves as a useful learning tool for English language learners.

---

⭐ **If you find this project helpful, please give it a star!** ⭐

---

**Developed with ❤️ as an Academic Project**
