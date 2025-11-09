# 🚀 Quick Start Guide - Deep Learner AI

Get the AI Study Buddy running in 5 minutes!

## Step 1: Start Backend (2 minutes)

### Option A: With Docker (Recommended)

```bash
# From project root
docker-compose up --build
```

Wait for:
- ✅ "Application startup complete" message
- ✅ Backend running on http://localhost:8000

### Option B: Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (you'll need these running separately)
# Then start the app
uvicorn app.main:app --reload
```

## Step 2: Start Frontend (2 minutes)

```bash
# Open new terminal
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

Wait for:
- ✅ Frontend running on http://localhost:3000

## Step 3: First Demo (1 minute)

1. Open http://localhost:3000
2. Click "Register" → Create account (username, email, password)
3. Create workspace: "Biology 101", subject: "Biology"
4. Click "Upload Document" → Select a PDF
5. Type: "Quiz me on this topic"
6. Watch the magic happen! 🎉

## Verification Checklist

Before the demo:

- [ ] Backend API accessible: http://localhost:8000/docs
- [ ] Frontend loads: http://localhost:3000
- [ ] Can register new account
- [ ] Can create workspace
- [ ] Can upload document (test with small PDF first)
- [ ] Can chat and get responses
- [ ] Can generate quiz with "quiz me" command

## Common Issues

### Backend won't start
```bash
# Check if ports are available
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# If occupied, stop the services or change ports in docker-compose.yml
```

### Frontend won't connect to backend
```bash
# Check .env.local
cat frontend/.env.local

# Should show:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Document upload fails
- Try a smaller PDF (< 10MB for first test)
- Check backend logs: `docker-compose logs -f app`
- Supported formats: PDF, TXT, DOC, DOCX

### Quiz not generating
- Make sure you include keyword: "quiz", "test", "multiple choice"
- Example: "Quiz me on biology"
- Example: "Create a multiple choice test"

## Test Data

Use these sample prompts:

**For RAG/Questions:**
- "What is photosynthesis?"
- "Explain cell division"
- "Generate 5 questions about this topic"

**For Quiz:**
- "Quiz me on biology"
- "Create a multiple choice test"
- "Give me a quiz with 3 questions"

## Performance Tips

### For Hackathon Demo:

1. **Pre-upload documents** before judges arrive
2. **Test the flow** at least once
3. **Have backup internet** in case of API issues
4. **Prepare 2-3 different topics** to show versatility
5. **Show the architecture diagram** (in main README)

### For GPU Acceleration:

```bash
# Verify GPU is available
docker run --rm --gpus all nvidia/cuda:12.1.0-base nvidia-smi

# Should show your GPU info
```

## Architecture At a Glance

```
User Browser (localhost:3000)
    ↓
Next.js Frontend (TypeScript + Tailwind)
    ↓
FastAPI Backend (localhost:8000)
    ↓
┌────────────────────────────────────┐
│  Main Graph (LangGraph Router)    │
│  ├─ Chat Agent                     │
│  ├─ RAG Agent (Document Search)   │
│  └─ Question Generation Agent     │
│     ├─ Open-ended Questions       │
│     └─ Multiple Choice Quiz       │
└────────────────────────────────────┘
    ↓
Database (PostgreSQL) + Redis (State) + Vector DB (FAISS)
```

## Ready for Hackathon? ✅

Your checklist:

- [ ] Both backend and frontend running
- [ ] Test account created
- [ ] Sample workspace with documents uploaded
- [ ] Tested full flow: Chat → Quiz → Results
- [ ] Prepared demo script (see main README)
- [ ] Know your talking points:
  - Multi-agent AI architecture
  - GPU acceleration (2-10x faster)
  - Smart routing between RAG/Chat/Quiz
  - Real-time question generation
  - Complete full-stack solution

## Next Steps

- Read the [main README](../README.md) for detailed documentation
- Check [frontend README](../frontend/README.md) for UI details
- Review API docs at http://localhost:8000/docs
- Prepare your pitch deck!

---

**Pro Tip**: Run through the demo flow 3 times before presenting. Muscle memory helps when you're nervous! 💪

**Good luck with your hackathon! 🏆**
