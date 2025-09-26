# 🚀 Quick Start Guide - File2Learning

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** for version control
- **Node.js 18+** and **Python 3.11+** (for local development)

## 🐳 Docker Setup (Recommended)

1. **Clone the repository** (when available)
2. **Copy environment file**:
   ```bash
   cp backend/.env.example backend/.env
   ```
3. **Add your OpenAI API key** to `backend/.env`:
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   ```
4. **Start all services**:
   ```bash
   docker-compose up -d
   ```

### Services URLs:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🛠 Manual Setup (Development)

### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

### Database Setup (PostgreSQL):
```bash
# Install PostgreSQL locally or use Docker
docker run -d --name postgres \
  -e POSTGRES_DB=ai_learning_material \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 postgres:15-alpine
```

## 🧪 Testing the Setup

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Create a test account**:
   - Visit http://localhost:3000
   - Click "Get Started" → Register
   - Fill out the form and create account

3. **Login and explore**:
   - Login with your credentials
   - Browse the dashboard and pages

## 📁 Project Structure

```
ai-learning-material/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── crud/           # Database operations
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # State management
│   │   └── main.tsx        # React app entry
│   ├── package.json        # Node dependencies
│   └── Dockerfile
├── scripts/                # Database scripts
├── docker-compose.yml      # Container orchestration
└── README.md
```

## 🐛 Troubleshooting

### Common Issues:

1. **Port conflicts**: Change ports in `docker-compose.yml`
2. **Database connection errors**: Check PostgreSQL is running
3. **CORS errors**: Verify frontend/backend URLs in config
4. **Permission errors**: Check file permissions on volumes

### Logs:
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### Reset Everything:
```bash
docker-compose down -v  # Remove containers and volumes
docker-compose up -d    # Start fresh
```

## 🔑 Environment Variables

Key variables in `backend/.env`:

```bash
# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI Integration
OPENAI_API_KEY=your-openai-api-key

# Redis (optional for dev)
REDIS_URL=redis://localhost:6379
```

## 📚 Next Steps

1. **Week 2**: Database migrations and core API endpoints
2. **Week 3**: Document processing pipeline
3. **Week 4**: AI integration for content generation
4. **Week 5**: Enhanced frontend features
5. **Week 6**: Interactive learning components
6. **Week 7**: Analytics and progress tracking
7. **Week 8**: Production deployment

## 🤝 Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest backend/tests/` and `npm test` 
4. Commit and push changes
5. Create pull request

Happy coding! 🎉
