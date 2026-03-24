'use client';

import { useState, useRef, useEffect } from 'react';
import { apiKeys, usage } from '../../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface APIKey {
  id: number;
  key: string;
  name: string;
}

interface UsageStats {
  total_requests: number;
  requests_today: number;
  requests_this_month: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I\'m your Wine API Assistant. Ask me about wines, API usage, or how to get started!' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedKey, setSelectedKey] = useState<string>('');
  const [apiKeyList, setApiKeyList] = useState<APIKey[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen && apiKeyList.length === 0) {
      loadApiKeys();
    }
  }, [isOpen]);

  const isLoggedIn = typeof window !== 'undefined' && localStorage.getItem('token');

  const loadApiKeys = async () => {
    if (!isLoggedIn) {
      return;
    }
    try {
      const keys = await apiKeys.list();
      setApiKeyList(keys);
      if (keys.length > 0 && !selectedKey) {
        setSelectedKey(keys[0].key);
      }
    } catch (err) {
      console.error('Failed to load API keys:', err);
    }
  };

  const callOllama = async (userMessage: string) => {
    if (!selectedKey) {
      throw new Error('No API key selected. Please add an API key in the dashboard.');
    }

    const conversation = [
      ...messages,
      { role: 'user' as const, content: userMessage }
    ];

    const response = await fetch(`${API_BASE}/chat/chat`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-API-Key': selectedKey,
      },
      body: JSON.stringify({ messages: conversation }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to get response');
    }

    const data = await response.json();
    return data.message.content;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim().toLowerCase();
    const isUsageQuestion = userMessage.includes('usage') || userMessage.includes('api usage') || userMessage.includes('how many');
    
    if (isUsageQuestion && isLoggedIn) {
      setInput('');
      setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
      setIsLoading(true);
      setError(null);

      try {
        const stats = await usage.getStats();
        const response = `Your API Usage:
- Total Requests: ${stats.total_requests.toLocaleString()}
- Requests Today: ${stats.requests_today.toLocaleString()}
- Requests This Month: ${stats.requests_this_month.toLocaleString()}

You can view detailed analytics at /analytics`;
        setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I couldn\'t fetch your usage data. Please try again.' }]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    const userMessageOriginal = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessageOriginal }]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await callOllama(userMessageOriginal);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      
      if (errorMessage.includes('Cannot connect')) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'I\'m having trouble connecting to the AI. Make sure Ollama is running:\n\n`ollama serve`\n\nThen try again.' 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error. Please try again.' 
        }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const styles: Record<string, React.CSSProperties> = {
    container: {
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 9999,
    },
    button: {
      width: '56px',
      height: '56px',
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #9333ea, #4f46e5)',
      border: 'none',
      color: 'white',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.3)',
    },
    chatWindow: {
      position: 'fixed',
      bottom: '100px',
      right: '24px',
      width: '340px',
      height: '480px',
      backgroundColor: 'white',
      borderRadius: '16px',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      border: '1px solid #e5e7eb',
    },
    header: {
      background: 'linear-gradient(135deg, #9333ea, #4f46e5)',
      padding: '16px',
      color: 'white',
    },
    select: {
      width: '100%',
      padding: '8px',
      fontSize: '12px',
      border: '1px solid #d1d5db',
      borderRadius: '4px',
      backgroundColor: 'white',
    },
    messagesArea: {
      flex: 1,
      overflowY: 'auto',
      padding: '16px',
      backgroundColor: '#f9fafb',
    },
    userMessage: {
      backgroundColor: '#9333ea',
      color: 'white',
      padding: '8px 12px',
      borderRadius: '12px 12px 4px 12px',
      maxWidth: '80%',
      marginLeft: 'auto',
      marginBottom: '8px',
      fontSize: '14px',
    },
    assistantMessage: {
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      color: '#374151',
      padding: '8px 12px',
      borderRadius: '12px 12px 12px 4px',
      maxWidth: '80%',
      marginRight: 'auto',
      marginBottom: '8px',
      fontSize: '14px',
      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
    },
    inputArea: {
      padding: '12px',
      borderTop: '1px solid #e5e7eb',
      backgroundColor: 'white',
    },
    input: {
      flex: 1,
      padding: '8px 16px',
      border: '1px solid #d1d5db',
      borderRadius: '9999px',
      fontSize: '14px',
      outline: 'none',
    },
    sendButton: {
      width: '36px',
      height: '36px',
      borderRadius: '50%',
      backgroundColor: '#9333ea',
      border: 'none',
      color: 'white',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginLeft: '8px',
    },
  };

  return (
    <div style={styles.container}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={styles.button}
        aria-label="Open chat"
      >
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          )}
        </svg>
      </button>

      {isOpen && (
        <div style={styles.chatWindow}>
          <div style={styles.header}>
            <div style={{ fontWeight: 600, fontSize: '16px' }}>Wine API Assistant</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>Powered by local LLM</div>
          </div>

          {apiKeyList.length > 0 ? (
            <div style={{ padding: '8px 12px', backgroundColor: '#f3f4f6', borderBottom: '1px solid #e5e7eb' }}>
              <select
                value={selectedKey}
                onChange={(e) => setSelectedKey(e.target.value)}
                style={styles.select}
              >
                {apiKeyList.map((key) => (
                  <option key={key.id} value={key.key}>
                    {key.name || 'API Key'}
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div style={{ padding: '12px', backgroundColor: '#fef3c7', borderBottom: '1px solid #fcd34d', fontSize: '12px', color: '#92400e' }}>
              {isLoggedIn ? 'No API keys found. Create one in the dashboard.' : 'Please log in to use the chat.'}
            </div>
          )}

          <div style={styles.messagesArea}>
            {messages.map((msg, i) => (
              <div key={i} style={msg.role === 'user' ? styles.userMessage : styles.assistantMessage}>
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              </div>
            ))}
            {isLoading && (
              <div style={styles.assistantMessage}>
                <div style={{ display: 'flex', gap: '4px' }}>
                  <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1s infinite' }} />
                  <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1s infinite', animationDelay: '0.1s' }} />
                  <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1s infinite', animationDelay: '0.2s' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} style={styles.inputArea}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={isLoggedIn && selectedKey ? "Ask about wines..." : "Log in to chat"}
                style={{ ...styles.input, backgroundColor: (!isLoggedIn || !selectedKey) ? '#f3f4f6' : 'white' }}
                disabled={isLoading || !selectedKey}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading || !selectedKey}
                style={{ ...styles.sendButton, opacity: (!input.trim() || isLoading || !selectedKey) ? 0.5 : 1 }}
              >
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
