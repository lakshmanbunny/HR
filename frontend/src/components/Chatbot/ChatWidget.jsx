import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Send, Bot, User, Trash2, Users, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const API_BASE = "/api";

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Initialize messages from localStorage or use default
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chat_history');
    return saved ? JSON.parse(saved) : [
      { role: 'assistant', content: 'Hi! I am the Paradigm AI Assistant. Ask me anything about our database.' }
    ];
  });

  const [sourcingContext, setSourcingContext] = useState(() => {
    const saved = localStorage.getItem('sourcing_context');
    return saved ? JSON.parse(saved) : {};
  });

  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  // Persistence logic: Save to localStorage whenever messages change
  useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem('sourcing_context', JSON.stringify(sourcingContext));
  }, [sourcingContext]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleChat = () => setIsOpen(!isOpen);

  const clearChat = () => {
    const defaultMsg = [{ role: 'assistant', content: 'Hi! I am the Paradigm AI Assistant. Ask me anything about our database.' }];
    setMessages(defaultMsg);
    setSourcingContext({});
    localStorage.removeItem('chat_history');
    localStorage.removeItem('sourcing_context');
  };

  const renderSourceTable = (csvString, intent) => {
    if (intent === 'RECRUITMENT_SOURCE') {
        try {
            const candidates = typeof csvString === 'string' ? JSON.parse(csvString) : csvString;
            if (Array.isArray(candidates) && candidates.length > 0) {
                return (
                    <div className="mt-3 p-4 bg-primary-blue/5 border border-primary-blue/20 rounded-xl flex flex-col items-center gap-3">
                        <div className="text-[11px] font-bold text-primary-blue uppercase tracking-widest flex items-center gap-2">
                             <Users size={14} />
                             {candidates.length} Profiles Found
                        </div>
                        <button 
                            onClick={() => {
                                sessionStorage.setItem('last_sourced_candidates', JSON.stringify(candidates));
                                setIsOpen(false);
                                window.location.href = '/sourced-candidates';
                            }}
                            className="w-full bg-primary-blue text-white py-2.5 rounded-lg font-black text-[10px] uppercase tracking-widest hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
                        >
                            View Sourced Candidates
                            <ExternalLink size={12} />
                        </button>
                    </div>
                );
            }
        } catch (e) {
            return <pre className="text-[10px] text-red-500">Error parsing sourcing data</pre>;
        }
    }

    if (!csvString || typeof csvString !== 'string') return null;
    
    let lines = csvString.trim().split('\n');
    if (lines.length === 0) return null;
    
    const parseCSVLine = (text) => {
        const arr = [];
        let quote = false;
        let val = '';
        for (let i = 0; i < text.length; i++) {
            let cc = text[i];
            if (cc === '"') {
                quote = !quote;
            } else if (cc === ',' && !quote) {
                arr.push(val);
                val = '';
            } else {
                val += cc;
            }
        }
        arr.push(val);
        return arr;
    };

    const headers = parseCSVLine(lines[0]);
    const rows = lines.slice(1).map(parseCSVLine);

    return (
      <div className="overflow-x-auto mt-3 border border-gray-200 rounded-lg shadow-sm scrollbar-thin scrollbar-thumb-gray-300">
        <table className="min-w-full divide-y divide-gray-200 text-left text-xs bg-white">
          <thead className="bg-gray-50 text-gray-700">
            <tr>
              {headers.map((h, i) => (
                <th key={i} className="px-3 py-2.5 font-bold uppercase tracking-wider whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {rows.map((row, i) => (
              <tr key={i} className="hover:bg-blue-50/60 transition-colors">
                {row.map((cell, j) => (
                  <td key={j} className="px-3 py-2 whitespace-nowrap text-gray-600">{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMsg = { role: 'user', content: inputValue.trim() };
    const newMessages = [...messages, userMsg];
    
    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chatbot/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMsg.content,
          history: messages,
          sourcing_context: sourcingContext
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      if (data.sourcing_metadata) {
          setSourcingContext(data.sourcing_metadata);
      }

      setMessages((prev) => [
        ...prev,
        { 
            role: 'assistant', 
            content: data.reply, 
            source_data: data.source_data,
            intent: data.intent 
        }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again later.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Chat Window */}
      {isOpen && (
        <div className="bg-white w-80 sm:w-96 rounded-2xl shadow-2xl mb-4 overflow-hidden border border-gray-100 flex flex-col h-[500px] max-h-[80vh] transition-all duration-300 transform origin-bottom-right">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 flex justify-between items-center shadow-sm">
            <div className="flex items-center space-x-2">
              <Bot size={20} />
              <h3 className="font-semibold text-sm">Paradigm AI Assistant</h3>
            </div>
            <div className="flex items-center space-x-1">
              <button 
                onClick={clearChat}
                title="Clear Conversation"
                className="text-white hover:text-red-200 transition-colors p-1.5 rounded-md hover:bg-blue-700 active:bg-red-500"
              >
                <Trash2 size={18} />
              </button>
              <button 
                onClick={toggleChat}
                title="Close Chat"
                className="text-white hover:text-gray-200 transition-colors p-1.5 rounded-md hover:bg-blue-700"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`flex flex-col max-w-[85%] ${msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}
              >
                <div 
                  className={`p-3 rounded-2xl text-[13px] sm:text-sm leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-br-none shadow-md' 
                      : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none shadow-sm'
                  }`}
                >
                    {msg.role === 'user' ? (
                        msg.content.split('\n').map((line, i) => (
                            <p key={i} className="min-h-[1rem]">{line}</p>
                        ))
                    ) : (
                        <div className="prose prose-sm prose-blue max-w-none">
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                    )}
                </div>
                
                {msg.role === 'assistant' && msg.source_data && (
                  <div className="w-full mt-2">
                      {(() => {
                          try {
                              const candidates = typeof msg.source_data === 'string' ? JSON.parse(msg.source_data) : msg.source_data;
                              // Only show the prominent button if it looks like a list of candidates
                              if (Array.isArray(candidates) && candidates.length > 0 && candidates[0].link) {
                                  return (
                                      <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl flex flex-col items-center gap-3 shadow-sm">
                                          <div className="text-[11px] font-bold text-blue-600 uppercase tracking-widest flex items-center gap-2">
                                              <Users size={14} />
                                              {candidates.length} Profiles Sourced
                                          </div>
                                          <button 
                                              onClick={() => {
                                                  sessionStorage.setItem('last_sourced_candidates', JSON.stringify(candidates));
                                                  setIsOpen(false);
                                                  window.location.href = '/sourced-candidates';
                                              }}
                                              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-bold text-[11px] uppercase tracking-widest hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-md hover:shadow-lg active:scale-[0.98]"
                                          >
                                              View Talent Pool
                                              <ExternalLink size={12} />
                                          </button>
                                      </div>
                                  );
                              }
                          } catch (e) {
                              return null;
                          }
                      })()}
                  </div>
                )}

                {msg.role === 'assistant' && msg.source_data && msg.intent !== 'RECRUITMENT_SOURCE' && (
                  <details className="mt-2 text-xs text-gray-500 bg-gray-200/50 rounded-lg p-2 w-full border border-gray-200 shadow-sm transition-all group">
                    <summary className="cursor-pointer font-medium hover:text-blue-600 list-none flex items-center">
                      <svg className="w-3 h-3 mr-1 transform transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      View Data Source
                    </summary>
                    {renderSourceTable(msg.source_data)}
                  </details>
                )}

                <span className="text-[10px] text-gray-400 mt-1 px-1">
                  {msg.role === 'user' ? 'You' : 'AI Agent'}
                </span>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex bg-white mr-auto border border-gray-100 rounded-2xl rounded-bl-none p-4 max-w-[85%] shadow-sm space-x-2 items-center">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 bg-white border-t border-gray-100">
            <form onSubmit={handleSendMessage} className="flex relative items-center">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask a question..."
                className="w-full bg-gray-50 border border-gray-200 rounded-full py-3 pl-4 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className={`absolute right-1 top-1 bottom-1 p-2 rounded-full flex items-center justify-center transition-all ${
                  inputValue.trim() && !isLoading ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'text-gray-400 bg-transparent'
                }`}
              >
                <Send size={16} className={inputValue.trim() && !isLoading ? 'translate-x-[1px]' : ''} />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={toggleChat}
        className={`${
          isOpen ? 'bg-gray-800 scale-90' : 'bg-blue-600 hover:bg-blue-700 hover:scale-105 shadow-blue-500/30 shadow-lg'
        } text-white p-4 rounded-full transition-all duration-300 flex items-center justify-center group relative`}
      >
        {isOpen ? <X size={28} /> : <MessageSquare size={28} />}
        {!isOpen && (
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
            </span>
        )}
      </button>
    </div>
  );
};

export default ChatWidget;
