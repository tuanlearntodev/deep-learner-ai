# Intellex AI- Frontend

Modern, responsive frontend for the AI Study Buddy application built with Next.js 16, TypeScript, and Tailwind CSS.

## Features

- 🔐 **Authentication**: Secure login and registration
- 📚 **Workspace Management**: Create and organize study workspaces by subject
- 💬 **Interactive Chat**: Ask questions about uploaded documents
- 📄 **Document Upload**: Support for PDF, TXT, DOC, DOCX files
- 🎯 **Smart Quiz Generation**: Automatically generates quizzes from your materials
- 📊 **Real-time Scoring**: Instant feedback with detailed results
- 🎨 **Modern UI**: Beautiful gradient designs with smooth animations

## Tech Stack

- **Next.js 16.0.1** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Zustand** - Lightweight state management with persistence
- **Lucide React** - Beautiful icon library

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Environment is already configured in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx                    # Login/Register page
│   ├── workspaces/
│   │   └── page.tsx               # Workspace list
│   └── workspace/[id]/
│       ├── page.tsx               # Chat interface
│       └── quiz/
│           └── page.tsx           # Quiz interface
├── lib/
│   ├── api.ts                     # API client with TypeScript interfaces
│   └── store.ts                   # Zustand state management
└── .env.local                     # Environment configuration
```

## User Flow

1. **Register/Login** → Create account or sign in
2. **Create Workspace** → Set up subject-specific workspace
3. **Upload Documents** → Add PDFs or text files
4. **Chat/Ask Questions** → Interact with AI about your materials
5. **Generate Quiz** → Say "Quiz me" to generate questions
6. **Take Quiz** → Answer multiple choice questions
7. **Review Results** → See score and correct answers

## Demo Script (Perfect for Hackathon!)

1. **Show Landing** - "This is Deep Learner AI, your AI-powered study buddy"
2. **Register** - Create new account in seconds
3. **Create Workspace** - "Let's create a Biology 101 workspace"
4. **Upload Document** - Drag-drop a PDF about cell biology
5. **Ask Question** - "What is mitochondria?"
6. **Generate Quiz** - Say "Quiz me on cell biology"
7. **Take Quiz** - Answer 3-5 multiple choice questions
8. **Show Results** - Display score with feedback
9. **Highlight Features** - GPU processing, smart routing, instant quiz generation

## Key Features

### Smart Response Routing
The chat interface detects response types:
- `text` - Regular conversation, stays in chat
- `questions` - Open-ended questions, redirects to quiz
- `quiz` - Multiple choice questions with scoring

### Quiz System
- **Progress Tracking** - Visual progress bar
- **Instant Feedback** - Correct/incorrect indication
- **Score Calculation** - Real-time score updates
- **Review Mode** - See all answers with corrections
- **Retry Option** - Take the quiz again

## Troubleshooting

**Issue**: API connection error
- **Solution**: Ensure backend is running on port 8000

**Issue**: Login doesn't work
- **Solution**: Check that backend is accessible at `http://localhost:8000`

**Issue**: Quiz not showing
- **Solution**: Make sure you include "quiz" keyword in your message
