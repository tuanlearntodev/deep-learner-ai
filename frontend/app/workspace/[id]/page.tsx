'use client';

import { useState, useEffect, useRef, use } from 'react';
import { useRouter } from 'next/navigation';
import { api, ChatMessage } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Send, Upload, ArrowLeft, FileText, Loader, HelpCircle, BookOpen, CheckCircle2, Award, XCircle, AlertCircle, Layers, RotateCw } from 'lucide-react';

// Flashcard component
const FlashcardCard = ({ flashcards }: { flashcards: any[] }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const currentCard = flashcards[currentIndex];

  const nextCard = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % flashcards.length);
  };

  const prevCard = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + flashcards.length) % flashcards.length);
  };

  const flipCard = () => {
    setIsFlipped(!isFlipped);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, { bg: string, text: string, border: string }> = {
      definition: { bg: '#1E3A5F', text: '#7BA3D1', border: '#2A4A70' },
      concept: { bg: '#3A2A5F', text: '#B39ED1', border: '#4A3A70' },
      formula: { bg: '#1E4F3A', text: '#7BC19E', border: '#2A5F4A' },
      example: { bg: '#5F3A1E', text: '#D1A37B', border: '#704A2A' },
      comparison: { bg: '#5F1E3A', text: '#D17BA3', border: '#702A4A' },
    };
    return colors[category.toLowerCase()] || { bg: '#2A3F5F', text: '#A0A8B8', border: '#3A4F6F' };
  };

  const categoryColors = getCategoryColor(currentCard.category);

  return (
    <div className="rounded-2xl p-8 w-full max-w-4xl shadow-xl border" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4" style={{ borderBottom: '1px solid #1F2937' }}>
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-full shadow-md" style={{ background: '#C4872C', color: '#FFFFFF' }}>
            <Layers size={24} />
          </div>
          <div>
            <h3 className="text-xl font-bold" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>Flashcards Generated!</h3>
            <p className="text-sm" style={{ color: '#A0A8B8' }}>
              {flashcards.length} card{flashcards.length > 1 ? 's' : ''} ready for studying
            </p>
          </div>
        </div>
        <div className="text-sm font-semibold" style={{ color: '#C4872C' }}>
          {currentIndex + 1} / {flashcards.length}
        </div>
      </div>

      {/* Category Badge */}
      <div className="mb-6">
        <span 
          className="inline-block px-4 py-2 rounded-full text-sm font-semibold border"
          style={{ 
            background: categoryColors.bg,
            color: categoryColors.text,
            borderColor: categoryColors.border
          }}
        >
          {currentCard.category.toUpperCase()}
        </span>
      </div>

      {/* Flashcard */}
      <div
        onClick={flipCard}
        className="relative rounded-xl p-12 h-[400px] flex items-center justify-center cursor-pointer shadow-lg hover:shadow-2xl transition-all mb-6 border"
        style={{ background: '#0A0F1E', borderColor: '#1F2937', perspective: '1000px' }}
      >
        <div className={`transition-all duration-300 ${isFlipped ? 'opacity-0' : 'opacity-100'}`}>
          {!isFlipped && (
            <div className="text-center w-full px-4">
              <div className="mb-6">
                <span className="text-sm font-semibold uppercase tracking-wide" style={{ color: '#7BA3D1' }}>Front</span>
              </div>
              <p className="text-2xl font-medium leading-relaxed" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>
                {currentCard.front}
              </p>
              <div className="mt-8 flex items-center justify-center gap-2" style={{ color: '#6B7A8F' }}>
                <RotateCw size={18} />
                <span className="text-sm">Click to flip</span>
              </div>
            </div>
          )}
        </div>

        <div className={`absolute inset-0 p-12 flex items-center justify-center transition-all duration-300 ${isFlipped ? 'opacity-100' : 'opacity-0'}`}>
          {isFlipped && (
            <div className="text-center w-full px-4">
              <div className="mb-6">
                <span className="text-sm font-semibold uppercase tracking-wide" style={{ color: '#7BC19E' }}>Back</span>
              </div>
              <p className="text-xl leading-relaxed" style={{ color: '#E0E5F1' }}>
                {currentCard.back}
              </p>
              <div className="mt-8 flex items-center justify-center gap-2" style={{ color: '#6B7A8F' }}>
                <RotateCw size={18} />
                <span className="text-sm">Click to flip</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="flex items-center justify-between gap-4">
        <button
          onClick={prevCard}
          disabled={flashcards.length <= 1}
          className="flex-1 px-6 py-4 rounded-lg transition-all border font-semibold text-base disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          style={{
            background: '#0A0F1E',
            color: '#E0E5F1',
            borderColor: '#1F2937'
          }}
          onMouseOver={(e) => flashcards.length > 1 && (e.currentTarget.style.background = '#141B2E')}
          onMouseOut={(e) => flashcards.length > 1 && (e.currentTarget.style.background = '#0A0F1E')}
        >
          ← Previous
        </button>
        <button
          onClick={flipCard}
          className="px-8 py-4 rounded-lg transition-all shadow-lg font-semibold text-base flex items-center gap-2"
          style={{
            background: '#C4872C',
            color: '#FFFFFF'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = '#A67324'}
          onMouseOut={(e) => e.currentTarget.style.background = '#C4872C'}
        >
          <RotateCw size={20} />
          Flip
        </button>
        <button
          onClick={nextCard}
          disabled={flashcards.length <= 1}
          className="flex-1 px-6 py-4 rounded-lg transition-all border font-semibold text-base disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
          style={{
            background: '#0A0F1E',
            color: '#E0E5F1',
            borderColor: '#1F2937'
          }}
          onMouseOver={(e) => flashcards.length > 1 && (e.currentTarget.style.background = '#141B2E')}
          onMouseOut={(e) => flashcards.length > 1 && (e.currentTarget.style.background = '#0A0F1E')}
        >
          Next →
        </button>
      </div>

      {/* Progress Dots */}
      {flashcards.length > 1 && (
        <div className="flex items-center justify-center gap-2 mt-6">
          {flashcards.map((_: any, idx: number) => (
            <button
              key={idx}
              onClick={() => {
                setCurrentIndex(idx);
                setIsFlipped(false);
              }}
              className="rounded-full transition-all"
              style={{
                width: idx === currentIndex ? '32px' : '8px',
                height: '8px',
                background: idx === currentIndex ? '#C4872C' : '#1F2937'
              }}
              onMouseOver={(e) => idx !== currentIndex && (e.currentTarget.style.background = '#2A3F5F')}
              onMouseOut={(e) => idx !== currentIndex && (e.currentTarget.style.background = '#1F2937')}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Single evaluation item component
const SingleEvaluation = ({ evaluation, index }: { evaluation: any; index?: number }) => {
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#7BC19E';
    if (score >= 0.4) return '#C4872C';
    return '#D17B7B';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.7) return <CheckCircle2 size={20} style={{ color: '#7BC19E' }} />;
    if (score >= 0.4) return <AlertCircle size={20} style={{ color: '#C4872C' }} />;
    return <XCircle size={20} style={{ color: '#D17B7B' }} />;
  };

  const scorePercentage = Math.round(evaluation.score * 100);

  return (
    <div className="rounded-xl p-5 border shadow-md" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
      {/* Question Header */}
      <div className="flex items-start gap-3 mb-4">
        {index !== undefined && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm" style={{ background: '#C4872C' }}>
            <span className="text-sm font-bold" style={{ color: '#FFFFFF' }}>{index + 1}</span>
          </div>
        )}
        <div className="flex-1">
          <h4 className="text-sm font-semibold mb-2" style={{ color: '#E0E5F1' }}>{evaluation.question}</h4>
          <div className="flex items-center gap-2">
            {getScoreIcon(evaluation.score)}
            <span className="text-sm font-semibold" style={{ color: getScoreColor(evaluation.score) }}>
              {scorePercentage}%
            </span>
          </div>
        </div>
      </div>

      {/* Answer Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs font-semibold mb-2 uppercase" style={{ color: '#A0A8B8' }}>Your Answer</p>
          <p className="text-sm p-3 rounded-lg border shadow-sm" style={{ color: '#E0E5F1', background: '#0A0F1E', borderColor: '#1F2937' }}>
            {evaluation.user_answer}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold mb-2 uppercase" style={{ color: '#A0A8B8' }}>Reference Answer</p>
          <p className="text-sm p-3 rounded-lg border shadow-sm" style={{ color: '#E0E5F1', background: '#1E4F3A', borderColor: '#2A5F4A' }}>
            {evaluation.correct_answer}
          </p>
        </div>
      </div>

      {/* Feedback */}
      <div className="rounded-lg p-4 border shadow-sm" style={{ background: '#1F2937', borderColor: '#2A3F5F' }}>
        <p className="text-sm leading-relaxed" style={{ color: '#E0E5F1' }}>{evaluation.feedback}</p>
      </div>
    </div>
  );
};

// Multiple evaluations component
const EvaluationCard = ({ evaluation }: { evaluation: any }) => {
  // Check if this is a multi-evaluation response
  if (evaluation.evaluations && Array.isArray(evaluation.evaluations)) {
    const overallScore = evaluation.overall_score || 0;
    const totalQuestions = evaluation.total_questions || evaluation.evaluations.length;
    const scorePercentage = Math.round(overallScore * 100);
    
    const getScoreColor = (score: number) => {
      if (score >= 0.7) return '#7BC19E';
      if (score >= 0.4) return '#C4872C';
      return '#D17B7B';
    };

    const getScoreBgColor = (score: number) => {
      if (score >= 0.7) return { bg: '#1E4F3A', border: '#2A5F4A' };
      if (score >= 0.4) return { bg: '#3A2A1E', border: '#4A3A2A' };
      return { bg: '#3A1E1E', border: '#4A2A2A' };
    };

    const getScoreIcon = (score: number) => {
      if (score >= 0.7) return <CheckCircle2 size={32} style={{ color: '#7BC19E' }} />;
      if (score >= 0.4) return <AlertCircle size={32} style={{ color: '#C4872C' }} />;
      return <XCircle size={32} style={{ color: '#D17B7B' }} />;
    };

    const bgColors = getScoreBgColor(overallScore);

    return (
      <div className="rounded-2xl p-6 max-w-4xl border shadow-xl" style={{ background: bgColors.bg, borderColor: bgColors.border }}>
        {/* Overall Header */}
        <div className="flex items-center gap-3 mb-6 pb-4" style={{ borderBottom: '1px solid #1F2937' }}>
          {getScoreIcon(overallScore)}
          <div>
            <h3 className="text-xl font-bold" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>Answer Evaluation</h3>
            <p className="text-lg font-semibold" style={{ color: getScoreColor(overallScore) }}>
              Overall Score: {scorePercentage}% ({totalQuestions} questions)
            </p>
          </div>
        </div>

        {/* Individual Evaluations */}
        <div className="space-y-4">
          {evaluation.evaluations.map((evalItem: any, idx: number) => (
            <SingleEvaluation key={idx} evaluation={evalItem} index={idx} />
          ))}
        </div>
      </div>
    );
  }

  // Single evaluation (backward compatibility)
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#7BC19E';
    if (score >= 0.4) return '#C4872C';
    return '#D17B7B';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 0.7) return { bg: '#1E4F3A', border: '#2A5F4A' };
    if (score >= 0.4) return { bg: '#3A2A1E', border: '#4A3A2A' };
    return { bg: '#3A1E1E', border: '#4A2A2A' };
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.7) return <CheckCircle2 size={32} style={{ color: '#7BC19E' }} />;
    if (score >= 0.4) return <AlertCircle size={32} style={{ color: '#C4872C' }} />;
    return <XCircle size={32} style={{ color: '#D17B7B' }} />;
  };

  const getEvaluationLabel = (evalType: string) => {
    if (evalType === 'correct') return 'Correct!';
    if (evalType === 'partially_correct') return 'Partially Correct';
    return 'Needs Improvement';
  };

  const scorePercentage = Math.round(evaluation.score * 100);
  const bgColors = getScoreBgColor(evaluation.score);

  return (
    <div className="rounded-2xl p-6 max-w-3xl border shadow-xl" style={{ background: bgColors.bg, borderColor: bgColors.border }}>
      {/* Header with Score */}
      <div className="flex items-center gap-3 mb-6 pb-4" style={{ borderBottom: '1px solid #1F2937' }}>
        {getScoreIcon(evaluation.score)}
        <div>
          <h3 className="text-xl font-bold" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>Answer Evaluation</h3>
          <p className="text-lg font-semibold" style={{ color: getScoreColor(evaluation.score) }}>
            {getEvaluationLabel(evaluation.evaluation)} - {scorePercentage}%
          </p>
        </div>
      </div>

      {/* Question */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold mb-2 uppercase tracking-wide" style={{ color: '#A0A8B8' }}>Question</h4>
        <p className="p-4 rounded-lg border shadow-sm" style={{ color: '#E0E5F1', background: '#141B2E', borderColor: '#1F2937' }}>{evaluation.question}</p>
      </div>

      {/* Your Answer */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold mb-2 uppercase tracking-wide" style={{ color: '#A0A8B8' }}>Your Answer</h4>
        <p className="p-4 rounded-lg border shadow-sm" style={{ color: '#E0E5F1', background: '#141B2E', borderColor: '#1F2937' }}>{evaluation.user_answer}</p>
      </div>

      {/* Correct Answer */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold mb-2 uppercase tracking-wide" style={{ color: '#A0A8B8' }}>Reference Answer</h4>
        <p className="p-4 rounded-lg border shadow-sm" style={{ color: '#E0E5F1', background: '#1E4F3A', borderColor: '#2A5F4A' }}>{evaluation.correct_answer}</p>
      </div>

      {/* Feedback */}
      <div className="rounded-xl p-5 border shadow-md" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
        <div className="flex items-center gap-2 mb-3">
          <Award size={20} style={{ color: '#C4872C' }} />
          <h4 className="text-sm font-semibold uppercase tracking-wide" style={{ color: '#E1A43C' }}>Personalized Feedback</h4>
        </div>
        <div className="leading-relaxed whitespace-pre-wrap" style={{ color: '#E0E5F1' }}>
          {evaluation.feedback}
        </div>
      </div>
    </div>
  );
};

const QuizCard = ({ questions, workspaceId }: { questions: any[], workspaceId: string }) => {
  const router = useRouter();

  const startQuiz = () => {
    router.push(`/workspace/${workspaceId}/quiz?questions=${encodeURIComponent(JSON.stringify(questions))}`);
  };

  return (
    <div className="rounded-2xl p-6 max-w-3xl border shadow-xl" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-4 pb-4" style={{ borderBottom: '1px solid #1F2937' }}>
        <div className="p-3 rounded-full shadow-md" style={{ background: '#C4872C', color: '#FFFFFF' }}>
          <HelpCircle size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>Quiz Generated!</h3>
          <p className="text-sm" style={{ color: '#A0A8B8' }}>
            {questions.length} question{questions.length > 1 ? 's' : ''} ready for you
          </p>
        </div>
      </div>

      {/* Questions Preview */}
      <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
        {questions.map((q: any, idx: number) => (
          <div key={idx} className="rounded-xl p-4 border shadow-md" style={{ background: '#0A0F1E', borderColor: '#1F2937' }}>
            <div className="flex items-start gap-2 mb-3">
              <span className="font-bold text-sm px-2.5 py-1 rounded shadow-sm" style={{ background: '#C4872C', color: '#FFFFFF' }}>
                Q{idx + 1}
              </span>
              <p className="font-medium flex-1" style={{ color: '#E0E5F1' }}>{q.question}</p>
            </div>
            
            {q.options && q.options.length > 0 && (
              <div className="space-y-2 ml-8">
                {q.options.map((option: string, optIdx: number) => {
                  const isCorrect = option === q.correctAnswer;
                  return (
                    <div
                      key={optIdx}
                      className="px-3 py-2 rounded-lg border transition-all"
                      style={{
                        borderColor: isCorrect ? '#7BC19E' : '#1F2937',
                        background: isCorrect ? '#1E4F3A' : '#141B2E'
                      }}
                    >
                      <span 
                        className="text-sm"
                        style={{
                          color: isCorrect ? '#7BC19E' : '#A0A8B8',
                          fontWeight: isCorrect ? '500' : '400'
                        }}
                      >
                        {option}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Start Quiz Button */}
      <button
        onClick={startQuiz}
        className="w-full flex items-center justify-center gap-2 px-6 py-4 rounded-xl transition-all shadow-lg hover:shadow-xl"
        style={{ background: '#C4872C', color: '#FFFFFF', fontWeight: '600' }}
        onMouseOver={(e) => e.currentTarget.style.background = '#A67324'}
        onMouseOut={(e) => e.currentTarget.style.background = '#C4872C'}
      >
        <BookOpen size={20} />
        Start Quiz
      </button>
    </div>
  );
};

interface ExtendedMessage extends ChatMessage {
  questions?: any[];
  response_type?: string;
}

export default function WorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { currentWorkspace, setCurrentWorkspace } = useStore();
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Unwrap params Promise
  const { id } = use(params);

  useEffect(() => {
    const initWorkspace = async () => {
      if (!currentWorkspace || currentWorkspace.id.toString() !== id) {
        await loadWorkspace();
      }
      await loadChatHistory();
    };
    initWorkspace();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadWorkspace = async () => {
    try {
      const workspaces = await api.getWorkspaces();
      const workspace = workspaces.find(w => w.id.toString() === id);
      if (workspace) {
        setCurrentWorkspace(workspace);
      }
    } catch (error) {
      console.error('Failed to load workspace:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      console.log('Loading chat history for workspace:', id);
      const history = await api.getChatHistory(parseInt(id));
      console.log('Chat history received:', history);
      console.log('Is array?', Array.isArray(history));
      
      // Process messages to detect quiz data
      const processedMessages: ExtendedMessage[] = Array.isArray(history) 
        ? history.map(msg => {
            // Check if this is a quiz message (assistant message with JSON quiz data)
            if (msg.role === 'assistant' && msg.content) {
              try {
                // Try to parse content as JSON
                const parsed = JSON.parse(msg.content);
                
                // Check if it's an array of quiz questions
                if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].type === 'quiz') {
                  return {
                    ...msg,
                    questions: parsed,
                    response_type: 'quiz',
                    content: `Generated ${parsed.length} quiz questions`
                  };
                }
                
                // Check if it's an array of flashcards
                if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].type === 'flashcard') {
                  return {
                    ...msg,
                    questions: parsed,
                    response_type: 'flashcard',
                    content: `Generated ${parsed.length} flashcards`
                  };
                }
                
                // Check if it's a quiz response object
                if (parsed.response_type === 'quiz' || parsed.response_type === 'questions') {
                  return {
                    ...msg,
                    questions: parsed.questions || [],
                    response_type: parsed.response_type,
                    content: `Generated ${parsed.questions?.length || 0} quiz questions`
                  };
                }
                
                // Check if it's an evaluation response object
                if (parsed.response_type === 'evaluation') {
                  return {
                    ...msg,
                    response_type: 'evaluation',
                    content: JSON.stringify(parsed)
                  };
                }
                
                // Check if it's a flashcard response object
                if (parsed.response_type === 'flashcard') {
                  return {
                    ...msg,
                    questions: parsed.questions || [],
                    response_type: 'flashcard',
                    content: `Generated ${parsed.questions?.length || 0} flashcards`
                  };
                }
              } catch (e) {
                // Not JSON or parsing failed, return as is
              }
            }
            return msg;
          })
        : [];
      
      setMessages(processedMessages);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setMessages([]);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // Add user message immediately for instant feedback
    const tempUserMsg: ExtendedMessage = {
      id: Date.now(), // temporary ID
      workspace_id: parseInt(id),
      role: 'user',
      content: userMessage
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      console.log('Sending message:', userMessage);
      const response = await api.sendMessage(parseInt(id), userMessage);
      console.log('Message response:', response);
      
      // Check if response is questions/quiz
      if (response.response_type === 'questions' || response.response_type === 'quiz') {
        // Add quiz message to chat
        const quizMsg: ExtendedMessage = {
          id: Date.now() + 1,
          workspace_id: parseInt(id),
          role: 'assistant',
          content: `Generated ${response.questions?.length || 0} quiz questions`,
          questions: response.questions || [],
          response_type: response.response_type
        };
        setMessages(prev => [...prev, quizMsg]);
      } else if (response.response_type === 'evaluation') {
        // Add evaluation message to chat
        const evaluationMsg: ExtendedMessage = {
          id: Date.now() + 1,
          workspace_id: parseInt(id),
          role: 'assistant',
          content: response.ai_message.content, // Use the AI message content directly (already JSON)
          response_type: 'evaluation'
        };
        setMessages(prev => [...prev, evaluationMsg]);
      } else if (response.response_type === 'flashcard') {
        // Add flashcard message to chat
        const flashcardMsg: ExtendedMessage = {
          id: Date.now() + 1,
          workspace_id: parseInt(id),
          role: 'assistant',
          content: `Generated ${response.questions?.length || 0} flashcards`,
          questions: response.questions || [],
          response_type: 'flashcard'
        };
        setMessages(prev => [...prev, flashcardMsg]);
      } else {
        // Reload chat history to get updated messages
        console.log('Reloading chat history after message sent');
        await loadChatHistory();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await api.uploadDocument(parseInt(id), file);
      alert('Document uploaded successfully!');
    } catch (error) {
      console.error('Failed to upload document:', error);
      alert('Failed to upload document');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ background: '#0A0F1E' }}>
      {/* Header - Fixed */}
      <div className="shadow-lg border-b flex-shrink-0" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/workspaces')}
              className="p-2 rounded-lg transition-all"
              style={{ color: '#E0E5F1', background: 'transparent' }}
              onMouseOver={(e) => e.currentTarget.style.background = '#1F2937'}
              onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-xl font-bold" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>{currentWorkspace?.name}</h1>
              <p className="text-sm" style={{ color: '#A0A8B8' }}>{currentWorkspace?.subject}</p>
            </div>
          </div>
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              onChange={handleFileUpload}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all shadow-md disabled:opacity-50"
              style={{ background: '#C4872C', color: '#FFFFFF', fontWeight: '600' }}
              onMouseOver={(e) => !uploading && (e.currentTarget.style.background = '#A67324')}
              onMouseOut={(e) => !uploading && (e.currentTarget.style.background = '#C4872C')}
            >
              {uploading ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload size={20} />
                  Upload Document
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Chat Messages - Scrollable */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-16">
              <FileText size={72} className="mx-auto mb-6" style={{ color: '#C4872C', opacity: 0.4 }} />
              <h2 className="text-2xl font-semibold mb-3" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>
                Start a Conversation
              </h2>
              <p className="text-lg" style={{ color: '#A0A8B8', opacity: 0.7 }}>
                Upload a document and ask questions, or try "Quiz me on this topic!"
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => {
              // Check if this is a quiz message
              if (msg.role === 'assistant' && msg.response_type === 'quiz' && msg.questions && msg.questions.length > 0) {
                return (
                  <div key={idx} className="flex justify-start">
                    <QuizCard questions={msg.questions} workspaceId={id} />
                  </div>
                );
              }

              // Check if this is a flashcard message
              if (msg.role === 'assistant' && msg.response_type === 'flashcard' && msg.questions && msg.questions.length > 0) {
                return (
                  <div key={idx} className="flex justify-start">
                    <FlashcardCard flashcards={msg.questions} />
                  </div>
                );
              }

              // Check if this is an evaluation message
              if (msg.role === 'assistant' && msg.response_type === 'evaluation') {
                try {
                  const evaluation = typeof msg.content === 'string' ? JSON.parse(msg.content) : msg.content;
                  return (
                    <div key={idx} className="flex justify-start">
                      <EvaluationCard evaluation={evaluation} />
                    </div>
                  );
                } catch (e) {
                  console.error('Failed to parse evaluation:', e);
                  // Fall through to regular message display
                }
              }
              
              // Regular message
              return (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className="max-w-[70%] rounded-xl px-5 py-3.5 shadow-lg"
                    style={{
                      background: msg.role === 'user' ? '#C4872C' : '#141B2E',
                      color: msg.role === 'user' ? '#FFFFFF' : '#E0E5F1',
                      fontWeight: msg.role === 'user' ? '600' : '400',
                      border: msg.role === 'assistant' ? '1px solid #1F2937' : 'none'
                    }}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              );
            })
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-xl px-5 py-4 shadow-lg border" style={{ background: '#141B2E', color: '#C4872C', borderColor: '#1F2937' }}>
                <Loader size={22} className="animate-spin" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Form - Fixed */}
      <div className="border-t shadow-lg flex-shrink-0" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
        <div className="container mx-auto px-4 py-4">
          <form onSubmit={handleSend} className="max-w-4xl mx-auto flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => {
                console.log('Input changed:', e.target.value);
                setInput(e.target.value);
              }}
              onFocus={() => console.log('Input focused')}
              placeholder="Ask a question or say 'Quiz me'..."
              className="flex-1 px-5 py-3.5 border rounded-xl focus:ring-2 disabled:opacity-50"
              style={{
                background: '#0A0F1E',
                color: '#E0E5F1',
                borderColor: '#1F2937',
                outlineColor: '#C4872C'
              }}
              disabled={loading}
              autoComplete="off"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3.5 rounded-xl transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              style={{
                background: loading || !input.trim() ? '#1F2937' : '#C4872C',
                color: '#FFFFFF',
                fontWeight: '600'
              }}
              onMouseOver={(e) => !loading && input.trim() && (e.currentTarget.style.background = '#A67324')}
              onMouseOut={(e) => !loading && input.trim() && (e.currentTarget.style.background = '#C4872C')}
            >
              <Send size={20} />
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
