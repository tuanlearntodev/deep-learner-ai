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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-800">My Workspaces</h1>
            <p className="text-gray-600 mt-2">Welcome back, {user?.full_name}!</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Create New Workspace Card */}
          <button
            onClick={() => setShowModal(true)}
            className="bg-white border-2 border-dashed border-indigo-300 rounded-xl p-8 hover:border-indigo-500 hover:bg-indigo-50 transition-all flex flex-col items-center justify-center min-h-[200px]"
          >
            <Plus size={48} className="text-indigo-500 mb-3" />
            <span className="text-lg font-semibold text-gray-700">Create Workspace</span>
          </button>

          {/* Workspace Cards */}
          {workspaces.map((workspace) => (
            <button
              key={workspace.id}
              onClick={() => handleSelectWorkspace(workspace)}
              className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-all text-left"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="bg-indigo-100 p-3 rounded-lg">
                  <BookOpen size={24} className="text-indigo-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">{workspace.name}</h3>
              <p className="text-gray-600">{workspace.subject}</p>
            </button>
          ))}
        </div>

        {/* Create Workspace Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-6">Create New Workspace</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Workspace Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900"
                    placeholder="e.g., Biology 101"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900"
                    placeholder="e.g., Biology"
                    required
                  />
                </div>
                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
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
