'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';

export default function LoginPage() {
  const router = useRouter();
  const setUser = useStore((state) => state.setUser);
  const [isLogin, setIsLogin] = useState(true);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await api.login(email, password);
        const user = await api.getCurrentUser();
        setUser(user);
        router.push('/workspaces');
      } else {
        await api.register(email, password, fullName);
        await api.login(email, password);
        const user = await api.getCurrentUser();
        setUser(user);
        router.push('/workspaces');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0F1A2E' }}>
      <div className="p-8 rounded-2xl shadow-xl w-full max-w-md" style={{ background: '#1B2B47' }}>
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2" style={{ color: '#C4872C', fontFamily: 'var(--font-lora)' }}>Intellex AI</h1>
          <p style={{ color: '#A0A8B8' }}>Your Personal Learning Assistant</p>
        </div>

        <div className="flex mb-6 rounded-lg p-1" style={{ background: '#0F1A2E' }}>
          <button
            onClick={() => setIsLogin(true)}
            className="flex-1 py-2 rounded-md transition-all"
            style={{
              background: isLogin ? '#E1A43C' : 'transparent',
              color: isLogin ? '#0F1A2E' : '#A0A8B8',
              fontWeight: isLogin ? '600' : '400'
            }}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className="flex-1 py-2 rounded-md transition-all"
            style={{
              background: !isLogin ? '#E1A43C' : 'transparent',
              color: !isLogin ? '#0F1A2E' : '#A0A8B8',
              fontWeight: !isLogin ? '600' : '400'
            }}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#A0A8B8' }}>
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2"
                style={{
                  background: '#0F1A2E',
                  color: '#E0E5F1',
                  borderColor: '#2A3F5F',
                  outlineColor: '#E1A43C'
                }}
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: '#A0A8B8' }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2"
              style={{
                background: '#0F1A2E',
                color: '#E0E5F1',
                borderColor: '#2A3F5F',
                outlineColor: '#E1A43C'
              }}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: '#A0A8B8' }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2"
              style={{
                background: '#0F1A2E',
                color: '#E0E5F1',
                borderColor: '#2A3F5F',
                outlineColor: '#E1A43C'
              }}
              required
              minLength={8}
            />
          </div>

          {error && (
            <div className="border px-4 py-3 rounded-lg" style={{ background: '#5F1E1E', borderColor: '#702A2A', color: '#D17B7B' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full font-semibold py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ 
              background: loading ? '#6B7A8F' : '#E1A43C',
              color: '#0F1A2E'
            }}
            onMouseOver={(e) => !loading && (e.currentTarget.style.background = '#D19535')}
            onMouseOut={(e) => !loading && (e.currentTarget.style.background = '#E1A43C')}
          >
            {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  );
}
