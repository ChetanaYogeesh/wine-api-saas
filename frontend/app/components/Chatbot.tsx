'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const WINE_KNOWLEDGE = {
  'red wine': 'Red wines are made from dark-colored grape varieties. Popular varieties include Cabernet Sauvignon, Merlot, Pinot Noir, and Syrah.',
  'white wine': 'White wines are made from green or yellowish grapes. Popular varieties include Chardonnay, Sauvignon Blanc, Riesling, and Pinot Grigio.',
  'rosé': 'Rosé wine has a pink color from brief contact with grape skins. It is typically crisp and refreshing.',
  'sparkling': 'Sparkling wines include Champagne, Prosecco, and Cava. They are known for their bubbles.',
  'region': 'Wine regions include Bordeaux, Burgundy, Napa Valley, Tuscany, and many more. Each region has unique terroir that affects wine flavor.',
  'variety': 'Wine varieties (grapes) include Cabernet Sauvignon, Merlot, Pinot Noir, Chardonnay, Sauvignon Blanc, and Riesling.',
  'vintage': 'A vintage year indicates when the grapes were harvested. Older isn\'t always better - it depends on the wine and storage conditions.',
  'rating': 'Wine ratings typically use a 100-point scale or 5-star system. Wines rated 90+ are considered excellent.',
  'pairing': 'General wine pairing: red meat → Cabernet Sauvignon, fish → Chardonnay, cheese → Merlot, dessert → Sauternes.',
  'api': 'Our Wine API provides access to 32,780+ wines. Use /wines endpoint for search, /wines/stats for statistics.',
  'authentication': 'Authenticate using X-API-Key header. Get your API key from the dashboard.',
  'rate limit': 'Rate limits: Free (60/min), Pro (300/min), Enterprise (1000/min).',
};

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I\'m your Wine API Assistant. Ask me about wines, API usage, or how to get started!' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    for (const [key, response] of Object.entries(WINE_KNOWLEDGE)) {
      if (input.includes(key)) {
        return response;
      }
    }

    if (input.includes('help')) {
      return 'I can help with:\n• Wine types and varieties\n• Food pairing suggestions\n• API authentication\n• Rate limits and pricing\n• Wine regions\n\nWhat would you like to know?';
    }

    if (input.includes('hello') || input.includes('hi')) {
      return 'Hello! How can I help you today?';
    }

    if (input.includes('thank')) {
      return 'You\'re welcome! Feel free to ask more questions.';
    }

    return 'I\'m not sure about that. Try asking about wines, API authentication, or rate limits. You can also type "help" for suggestions.';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    setTimeout(() => {
      const response = getResponse(userMessage);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      setIsLoading(false);
    }, 500);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center z-50 hover:scale-110"
        aria-label="Open chat"
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>

      {isOpen && (
        <div className="fixed bottom-24 right-6 w-80 h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden border border-gray-200">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-700 p-4 text-white">
            <h3 className="font-semibold text-lg">Wine API Assistant</h3>
            <p className="text-purple-100 text-sm">Ask me anything about wines or the API</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                    msg.role === 'user'
                      ? 'bg-purple-600 text-white rounded-br-md'
                      : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="p-3 border-t bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
