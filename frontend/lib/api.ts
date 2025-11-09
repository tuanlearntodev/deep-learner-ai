const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AuthTokens {
  access_token: string;
  token_type: string;
}

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

interface Workspace {
  id: number;
  name: string;
  subject: string;
  user_id: number;
}

interface ChatMessage {
  id: number;
  workspace_id: number;
  role: string;
  content: string;
}

interface Question {
  type: string;
  question: string;
  options: string[];
  correctAnswer: string;
}

interface ChatResponse {
  workspace_id: number;
  user_message: ChatMessage;
  ai_message: ChatMessage;
  subject: string | null;
  response_type: 'text' | 'questions' | 'quiz';
  questions: Question[] | null;
}

class ApiClient {
  private token: string | null = null;
  private baseURL: string = API_BASE_URL;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (options.headers) {
      Object.entries(options.headers).forEach(([key, value]) => {
        if (typeof value === 'string') {
          headers[key] = value;
        }
      });
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async register(email: string, password: string, full_name: string): Promise<User> {
    return this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    });
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const tokens = await response.json();
    this.setToken(tokens.access_token);
    return tokens;
  }

  async getCurrentUser(): Promise<User> {
    return this.request('/auth/me');
  }

  // Workspaces
  async getWorkspaces(): Promise<Workspace[]> {
    const response: any = await this.request('/workspaces/');
    return response.workspaces || [];
  }

  async createWorkspace(name: string, subject: string): Promise<Workspace> {
    return this.request('/workspaces/', {
      method: 'POST',
      body: JSON.stringify({ name, subject }),
    });
  }

  async getWorkspace(id: number): Promise<Workspace> {
    return this.request(`/workspaces/${id}`);
  }

  // Documents
  async uploadDocument(workspaceId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/workspaces/${workspaceId}/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  }

  async getDocuments(workspaceId: number): Promise<any[]> {
    const response: any = await this.request(`/workspaces/${workspaceId}/documents`);
    return response.documents || [];
  }

  // Chat
  async sendMessage(
    workspaceId: number,
    message: string,
    webSearch: boolean = false,
    crag: boolean = true
  ): Promise<ChatResponse> {
    return this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        workspace_id: workspaceId,
        message,
        web_search: webSearch,
        crag,
      }),
    });
  }

  async getChatHistory(workspaceId: number, limit: number = 50): Promise<ChatMessage[]> {
    console.log('API: Fetching chat history for workspace:', workspaceId);
    const response: any = await this.request(`/chat/history/${workspaceId}?limit=${limit}`);
    console.log('API: Chat history response:', response);
    console.log('API: Extracted messages:', response.messages || []);
    return response.messages || [];
  }

  async clearChatHistory(workspaceId: number): Promise<void> {
    return this.request(`/chat/history/${workspaceId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();
export type { User, Workspace, ChatMessage, ChatResponse, Question };
