'use client';

import { useState, useEffect, Suspense, use } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useStore } from '@/lib/store';
import { ArrowLeft, CheckCircle, XCircle, RotateCcw } from 'lucide-react';

interface Question {
  type?: string;
  question: string;
  options?: string[];
  correctAnswer?: string;
}

function QuizContent({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { id } = use(params);
  const { currentWorkspace } = useStore();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState<boolean[]>([]);
  const [userAnswers, setUserAnswers] = useState<string[]>([]);

  useEffect(() => {
    const questionsParam = searchParams.get('questions');
    if (questionsParam) {
      try {
        const parsed = JSON.parse(decodeURIComponent(questionsParam));
        setQuestions(Array.isArray(parsed) ? parsed : [parsed]);
      } catch (error) {
        console.error('Failed to parse questions:', error);
      }
    }
  }, [searchParams]);

  const currentQuestion = questions[currentIndex];
  const isMultipleChoice = currentQuestion?.options && currentQuestion?.options.length > 0;

  const handleAnswer = (answer: string) => {
    if (!answer) return;

    const isCorrect = answer === currentQuestion.correctAnswer;
    const newAnswers = [...answers, isCorrect];
    const newUserAnswers = [...userAnswers, answer];
    const newScore = isCorrect ? score + 1 : score;
    
    setAnswers(newAnswers);
    setUserAnswers(newUserAnswers);
    setSelectedAnswer(answer);
    
    if (isCorrect) {
      setScore(newScore);
      // Move to next question immediately on correct answer
      if (currentIndex < questions.length - 1) {
        setTimeout(() => {
          setCurrentIndex(currentIndex + 1);
          setSelectedAnswer(null);
        }, 600);
      } else {
        setTimeout(() => {
          setShowResult(true);
        }, 600);
      }
    } else {
      // Show wrong answer feedback for 1.5 seconds
      setTimeout(() => {
        if (currentIndex < questions.length - 1) {
          setCurrentIndex(currentIndex + 1);
          setSelectedAnswer(null);
        } else {
          setShowResult(true);
        }
      }, 1500);
    }
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setShowResult(false);
    setScore(0);
    setAnswers([]);
    setUserAnswers([]);
  };

  if (questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-xl text-gray-600">Loading questions...</div>
      </div>
    );
  }

  if (showResult) {
    const percentage = Math.round((score / questions.length) * 100);
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
          <div className="text-center">
            <div className={`mx-auto w-24 h-24 rounded-full flex items-center justify-center mb-6 ${
              percentage >= 70 ? 'bg-green-100' : 'bg-orange-100'
            }`}>
              <span className={`text-4xl font-bold ${
                percentage >= 70 ? 'text-green-600' : 'text-orange-600'
              }`}>
                {percentage}%
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Quiz Complete!</h1>
            <p className="text-xl text-gray-600 mb-8">
              You scored {score} out of {questions.length}
            </p>
          </div>

          {/* Questions Review */}
          <div className="space-y-6 mb-8 max-h-[60vh] overflow-y-auto">
            {questions.map((q, idx) => {
              const userAnswer = userAnswers[idx];
              const isMultiChoice = q.options && q.options.length > 0;
              
              return (
                <div key={idx} className="border-2 border-gray-200 rounded-xl p-6 bg-gray-50">
                  <div className="flex items-start gap-3 mb-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      answers[idx] ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      {answers[idx] ? (
                        <CheckCircle className="text-white" size={20} />
                      ) : (
                        <XCircle className="text-white" size={20} />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-600 mb-2">Question {idx + 1}</p>
                      <h3 className="text-lg font-semibold text-gray-800">{q.question}</h3>
                    </div>
                  </div>

                  {isMultiChoice ? (
                    <div className="space-y-2 ml-11">
                      {q.options!.map((option, optIdx) => {
                        const isCorrect = option === q.correctAnswer;
                        const wasSelected = option === userAnswer;
                        
                        return (
                          <div
                            key={optIdx}
                            className={`px-4 py-3 rounded-lg border-2 transition-all ${
                              isCorrect
                                ? 'border-green-500 bg-green-50'
                                : wasSelected
                                ? 'border-red-500 bg-red-50'
                                : 'border-gray-300 bg-white'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div
                                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                                  isCorrect
                                    ? 'border-green-500 bg-green-500'
                                    : wasSelected
                                    ? 'border-red-500 bg-red-500'
                                    : 'border-gray-400'
                                }`}
                              >
                                {isCorrect && (
                                  <CheckCircle size={16} className="text-white" />
                                )}
                                {wasSelected && !isCorrect && (
                                  <XCircle size={16} className="text-white" />
                                )}
                              </div>
                              <span className={`${
                                isCorrect ? 'text-green-800 font-medium' : wasSelected ? 'text-red-800' : 'text-gray-600'
                              }`}>
                                {option}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="ml-11 space-y-3">
                      {!answers[idx] && userAnswer && (
                        <div className="px-4 py-3 rounded-lg border-2 border-red-500 bg-red-50">
                          <p className="text-sm text-red-800">
                            <span className="font-medium">Your answer:</span> {userAnswer}
                          </p>
                        </div>
                      )}
                      {q.correctAnswer && (
                        <div className="px-4 py-3 rounded-lg border-2 border-green-500 bg-green-50">
                          <p className="text-sm text-green-800">
                            <span className="font-medium">Correct answer:</span> {q.correctAnswer}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="text-center">
            <div className="flex gap-4">
              <button
                onClick={handleRestart}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors"
              >
                <RotateCcw size={20} />
                Try Again
              </button>
              <button
                onClick={() => router.push(`/workspace/${id}`)}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <ArrowLeft size={20} />
                Back to Chat
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push(`/workspace/${id}`)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-800">{currentWorkspace?.name} - Quiz</h1>
              <p className="text-sm text-gray-600">
                Question {currentIndex + 1} of {questions.length}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Score</p>
            <p className="text-2xl font-bold text-indigo-600">{score}/{questions.length}</p>
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-600 transition-all duration-300"
                  style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
                />
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              {currentQuestion.question}
            </h2>

            {isMultipleChoice ? (
              <div className="space-y-3">
                {currentQuestion.options!.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      if (!selectedAnswer) {
                        handleAnswer(option);
                      }
                    }}
                    disabled={!!selectedAnswer}
                    className={`w-full text-left px-6 py-4 rounded-xl border-2 transition-all ${
                      selectedAnswer === option
                        ? option === currentQuestion.correctAnswer
                          ? 'border-green-500 bg-green-50'
                          : 'border-red-500 bg-red-50'
                        : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
                    } ${selectedAnswer && 'cursor-not-allowed'}`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                          selectedAnswer === option
                            ? option === currentQuestion.correctAnswer
                              ? 'border-green-500 bg-green-500'
                              : 'border-red-500 bg-red-500'
                            : 'border-gray-400'
                        }`}
                      >
                        {selectedAnswer === option && (
                          option === currentQuestion.correctAnswer ? (
                            <CheckCircle size={20} className="text-white" />
                          ) : (
                            <XCircle size={20} className="text-white" />
                          )
                        )}
                      </div>
                      <span className="text-lg">{option}</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <textarea
                  value={selectedAnswer || ''}
                  onChange={(e) => setSelectedAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent min-h-[120px] text-gray-900"
                />
                <button
                  onClick={() => {
                    if (currentIndex < questions.length - 1) {
                      setCurrentIndex(currentIndex + 1);
                      setSelectedAnswer(null);
                    } else {
                      setShowResult(true);
                    }
                  }}
                  disabled={!selectedAnswer}
                  className="w-full px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function QuizPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    }>
      <QuizContent params={params} />
    </Suspense>
  );
}
