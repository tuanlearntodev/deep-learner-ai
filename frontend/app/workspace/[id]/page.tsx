'use client';

import { useState, useEffect, useRef, use } from 'react';
import { useRouter } from 'next/navigation';
import { api, ChatMessage } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Send, Upload, ArrowLeft, FileText, Loader, HelpCircle, BookOpen, CheckCircle2 } from 'lucide-react';

const QuizCard = ({ questions, workspaceId }: { questions: any[], workspaceId: string }) => {
  const router = useRouter();

  const startQuiz = () => {
    router.push(`/workspace/${workspaceId}/quiz?questions=${encodeURIComponent(JSON.stringify(questions))}`);
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 max-w-3xl border-2 border-indigo-200 shadow-lg">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4 pb-4 border-b border-indigo-200">
        <div className="bg-indigo-600 text-white p-3 rounded-full">
          <HelpCircle size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-800">Quiz Generated!</h3>
          <p className="text-sm text-gray-600">
            {questions.length} question{questions.length > 1 ? 's' : ''} ready for you
          </p>
        </div>
      </div>

      {/* Questions Preview */}
      <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
        {questions.map((q: any, idx: number) => (
          <div key={idx} className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
            <div className="flex items-start gap-2 mb-3">
              <span className="bg-indigo-100 text-indigo-700 font-bold text-sm px-2 py-1 rounded">
                Q{idx + 1}
              </span>
              <p className="text-gray-800 font-medium flex-1">{q.question}</p>
            </div>
            
            {q.options && q.options.length > 0 && (
              <div className="space-y-2 ml-8">
                {q.options.map((option: string, optIdx: number) => {
                  const isCorrect = option === q.correctAnswer;
                  return (
                    <div
                      key={optIdx}
                      className={`px-3 py-2 rounded-lg border-2 transition-all ${
                        isCorrect
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <span className={`text-sm ${
                        isCorrect ? 'text-green-800 font-medium' : 'text-gray-600'
                      }`}>
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
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors shadow-md hover:shadow-lg"
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
                
                // Check if it's a quiz response object
                if (parsed.response_type === 'quiz' || parsed.response_type === 'questions') {
                  return {
                    ...msg,
                    questions: parsed.questions || [],
                    response_type: parsed.response_type,
                    content: `Generated ${parsed.questions?.length || 0} quiz questions`
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
    <div className="h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col overflow-hidden">
      {/* Header - Fixed */}
      <div className="bg-white shadow-sm border-b flex-shrink-0">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/workspaces')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-800">{currentWorkspace?.name}</h1>
              <p className="text-sm text-gray-600">{currentWorkspace?.subject}</p>
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
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
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
            <div className="text-center py-12">
              <FileText size={64} className="mx-auto text-gray-400 mb-4" />
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Start a Conversation
              </h2>
              <p className="text-gray-600">
                Upload a document and ask questions, or try "Quiz me on this topic!"
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => {
              // Check if this is a quiz message
              if (msg.role === 'assistant' && msg.questions && msg.questions.length > 0) {
                return (
                  <div key={idx} className="flex justify-start">
                    <QuizCard questions={msg.questions} workspaceId={id} />
                  </div>
                );
              }
              
              // Regular message
              return (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white text-gray-800 shadow-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              );
            })
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 rounded-xl px-4 py-3 shadow-sm">
                <Loader size={20} className="animate-spin" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Form - Fixed */}
      <div className="bg-white border-t shadow-lg flex-shrink-0">
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
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900"
              disabled={loading}
              autoComplete="off"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
