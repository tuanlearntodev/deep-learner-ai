'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, Workspace } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Plus, BookOpen, LogOut } from 'lucide-react';

export default function WorkspacesPage() {
  const router = useRouter();
  const { user, setCurrentWorkspace, clearSession } = useStore();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [subject, setSubject] = useState('');

  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }
    loadWorkspaces();
  }, [user, router]);

  const loadWorkspaces = async () => {
    try {
      console.log('Loading workspaces...');
      const data = await api.getWorkspaces();
      console.log('Workspaces received:', data);
      setWorkspaces(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load workspaces:', error);
      setWorkspaces([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createWorkspace(name, subject);
      setName('');
      setSubject('');
      setShowModal(false);
      loadWorkspaces();
    } catch (error) {
      console.error('Failed to create workspace:', error);
    }
  };

  const handleSelectWorkspace = (workspace: Workspace) => {
    setCurrentWorkspace(workspace);
    router.push(`/workspace/${workspace.id}`);
  };

  const handleLogout = () => {
    api.clearToken();
    clearSession();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0A0F1E' }}>
        <div className="text-xl font-semibold" style={{ color: '#C4872C' }}>Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: '#0A0F1E' }}>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-4xl font-bold" style={{ color: '#C4872C', fontFamily: 'var(--font-lora)' }}>My Workspaces</h1>
            <p className="mt-2 text-lg" style={{ color: '#A0A8B8' }}>Welcome back, {user?.full_name}!</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all shadow-md"
            style={{ color: '#E0E5F1', background: '#141B2E' }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#1F2937';
              e.currentTarget.style.color = '#C4872C';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = '#141B2E';
              e.currentTarget.style.color = '#E0E5F1';
            }}
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Create New Workspace Card */}
          <button
            onClick={() => setShowModal(true)}
            className="border-2 border-dashed rounded-xl p-8 transition-all flex flex-col items-center justify-center min-h-[220px] shadow-lg hover:shadow-2xl"
            style={{ 
              background: '#141B2E', 
              borderColor: '#C4872C' 
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.borderColor = '#A67324';
              e.currentTarget.style.background = '#1F2937';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = '#C4872C';
              e.currentTarget.style.background = '#141B2E';
            }}
          >
            <Plus size={52} style={{ color: '#C4872C' }} className="mb-4" />
            <span className="text-lg font-semibold" style={{ color: '#E0E5F1' }}>Create Workspace</span>
          </button>

          {/* Workspace Cards */}
          {workspaces.map((workspace) => (
            <button
              key={workspace.id}
              onClick={() => handleSelectWorkspace(workspace)}
              className="rounded-xl shadow-lg p-6 hover:shadow-2xl transition-all text-left border"
              style={{ background: '#141B2E', borderColor: '#1F2937' }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = '#1F2937';
                e.currentTarget.style.borderColor = '#C4872C';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = '#141B2E';
                e.currentTarget.style.borderColor = '#1F2937';
              }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 rounded-lg shadow-md" style={{ background: '#C4872C' }}>
                  <BookOpen size={24} style={{ color: '#FFFFFF' }} />
                </div>
              </div>
              <h3 className="text-xl font-bold mb-2" style={{ color: '#E0E5F1', fontFamily: 'var(--font-lora)' }}>{workspace.name}</h3>
              <p className="text-base" style={{ color: '#A0A8B8' }}>{workspace.subject}</p>
            </button>
          ))}
        </div>

        {/* Create Workspace Modal */}
        {showModal && (
          <div className="fixed inset-0 flex items-center justify-center p-4 z-50" style={{ background: 'rgba(0, 0, 0, 0.85)' }}>
            <div className="rounded-2xl p-8 max-w-md w-full shadow-2xl border" style={{ background: '#141B2E', borderColor: '#1F2937' }}>
              <h2 className="text-2xl font-bold mb-6" style={{ color: '#C4872C', fontFamily: 'var(--font-lora)' }}>Create New Workspace</h2>
              <form onSubmit={handleCreate} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#A0A8B8' }}>
                    Workspace Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 shadow-sm"
                    style={{
                      background: '#0A0F1E',
                      color: '#E0E5F1',
                      borderColor: '#1F2937',
                      outlineColor: '#C4872C'
                    }}
                    placeholder="e.g., Biology 101"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#A0A8B8' }}>
                    Subject
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 shadow-sm"
                    style={{
                      background: '#0A0F1E',
                      color: '#E0E5F1',
                      borderColor: '#1F2937',
                      outlineColor: '#C4872C'
                    }}
                    placeholder="e.g., Biology"
                    required
                  />
                </div>
                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-3 border rounded-lg transition-all shadow-md"
                    style={{ 
                      background: '#0A0F1E', 
                      color: '#E0E5F1',
                      borderColor: '#1F2937'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = '#141B2E'}
                    onMouseOut={(e) => e.currentTarget.style.background = '#0A0F1E'}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-3 rounded-lg transition-all shadow-lg"
                    style={{ 
                      background: '#C4872C',
                      color: '#FFFFFF',
                      fontWeight: '600'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = '#A67324'}
                    onMouseOut={(e) => e.currentTarget.style.background = '#C4872C'}
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
