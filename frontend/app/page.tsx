'use client';

import React, { useState, useRef, useEffect, CSSProperties } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Send, Database, Sparkles, MessageSquare, Loader2, AlertCircle, FileText, X } from 'lucide-react';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });
const AnimatedBackground = dynamic(() => import('@/components/AnimatedBackground'), { ssr: false });

const API_URL = 'http://localhost:8000';

// Styles
const styles: Record<string, CSSProperties> = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%)',
    color: '#fff',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    position: 'relative' as const,
  },
  header: {
    textAlign: 'center' as const,
    padding: '1.5rem 1rem 1rem',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
  },
  title: { fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' },
  gradientText: {
    background: 'linear-gradient(135deg, #a855f7, #ec4899, #f97316)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: { color: '#6b7280', fontSize: '0.85rem' },

  // Upload - improved
  uploadContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 'calc(100vh - 100px)',
    padding: '2rem'
  },
  uploadCard: {
    background: 'rgba(20, 20, 30, 0.95)',
    borderRadius: '1.5rem',
    padding: '2.5rem',
    textAlign: 'center' as const,
    maxWidth: '420px',
    width: '100%',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
  },
  dropzone: {
    border: '2px dashed rgba(139, 92, 246, 0.3)',
    borderRadius: '1rem',
    padding: '2rem 1.5rem',
    marginBottom: '1.5rem',
    transition: 'all 0.2s ease',
    cursor: 'pointer',
  },
  dropzoneActive: {
    border: '2px dashed rgba(139, 92, 246, 0.8)',
    background: 'rgba(139, 92, 246, 0.1)',
  },
  filePreview: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.75rem',
    padding: '1rem',
    background: 'rgba(139, 92, 246, 0.1)',
    borderRadius: '0.75rem',
    marginBottom: '1rem',
  },
  sampleDataLink: {
    color: '#8b5cf6',
    fontSize: '0.8rem',
    marginTop: '1rem',
    cursor: 'pointer',
    textDecoration: 'underline',
  },
  formatBadges: {
    display: 'flex',
    gap: '0.5rem',
    justifyContent: 'center',
    marginTop: '0.75rem',
  },
  badge: {
    padding: '0.25rem 0.5rem',
    background: 'rgba(139, 92, 246, 0.15)',
    borderRadius: '0.375rem',
    fontSize: '0.7rem',
    color: '#a78bfa',
  },
  primaryButton: {
    width: '100%',
    padding: '0.875rem 1.5rem',
    background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
    border: 'none',
    borderRadius: '0.75rem',
    color: '#fff',
    fontWeight: 600,
    fontSize: '1rem',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    transition: 'transform 0.1s, opacity 0.2s',
  },

  // Chat - wider
  chatContainer: {
    maxWidth: '1100px',  // Wider!
    width: '90%',        // Use more horizontal space
    margin: '0 auto',
    padding: '0 1rem 1.5rem',
    height: 'calc(100vh - 90px)',
    display: 'flex',
    flexDirection: 'column' as const,
  },
  chatPanel: {
    flex: 1,
    background: 'rgba(15, 15, 22, 0.95)',
    borderRadius: '1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    border: '1px solid rgba(255, 255, 255, 0.08)',
    overflow: 'hidden',
  },
  chatHeader: {
    padding: '0.875rem 1.25rem',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    background: 'rgba(20, 20, 30, 0.5)',
  },
  chatMessages: {
    flex: 1,
    overflowY: 'auto' as const,
    padding: '1.25rem',
  },
  chatBubbleUser: {
    background: 'rgba(139, 92, 246, 0.12)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '1rem 1rem 0.25rem 1rem',
    padding: '0.875rem 1rem',
    marginLeft: '20%',
    marginBottom: '0.75rem',
  },
  chatBubbleAgent: {
    background: 'rgba(30, 30, 40, 0.7)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    borderRadius: '1rem 1rem 1rem 0.25rem',
    padding: '0.875rem 1rem',
    marginRight: '10%',
    marginBottom: '0.75rem',
  },
  chatInput: {
    padding: '0.875rem 1.25rem',
    borderTop: '1px solid rgba(255, 255, 255, 0.05)',
    display: 'flex',
    gap: '0.75rem',
    background: 'rgba(20, 20, 30, 0.5)',
  },
  inputField: {
    flex: 1,
    background: 'rgba(10, 10, 15, 0.8)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '0.75rem',
    padding: '0.875rem 1rem',
    color: '#fff',
    fontSize: '0.95rem',
    outline: 'none',
  },
  sendButton: {
    background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
    border: 'none',
    borderRadius: '0.75rem',
    padding: '0.875rem 1.25rem',
    cursor: 'pointer',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Typing indicator
  typingIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    color: '#9ca3af',
    fontSize: '0.875rem',
    padding: '0.5rem 0',
  },

  // Error toast
  errorToast: {
    position: 'fixed' as const,
    bottom: '2rem',
    right: '2rem',
    background: 'rgba(239, 68, 68, 0.95)',
    color: '#fff',
    padding: '1rem 1.25rem',
    borderRadius: '0.75rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
    zIndex: 1000,
  },

  // Quick actions
  quickActions: {
    display: 'flex',
    gap: '0.5rem',
    padding: '0.75rem 1.25rem',
    borderTop: '1px solid rgba(255, 255, 255, 0.03)',
    flexWrap: 'wrap' as const,
  },
  quickAction: {
    padding: '0.375rem 0.75rem',
    background: 'rgba(139, 92, 246, 0.1)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '0.5rem',
    fontSize: '0.75rem',
    color: '#a78bfa',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
};

// Custom markdown components to tone down bold
const markdownComponents = {
  strong: ({ children }: any) => <span style={{ fontWeight: 600, color: '#c4b5fd' }}>{children}</span>,
  p: ({ children }: any) => <p style={{ margin: '0.5rem 0', lineHeight: 1.6 }}>{children}</p>,
  ul: ({ children }: any) => <ul style={{ margin: '0.5rem 0', paddingLeft: '1.25rem' }}>{children}</ul>,
  li: ({ children }: any) => <li style={{ margin: '0.25rem 0' }}>{children}</li>,
};

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  type?: 'text' | 'chart';
  error?: boolean;
  agentName?: string;
}

function parsePlotlyJSON(content: string): { data: any[]; layout: any } | null {
  try {
    let json = content.trim();
    if (json.includes('```')) json = json.replace(/```json?\s*/g, '').replace(/```/g, '').trim();
    const match = json.match(/\{[\s\S]*\}/);
    if (match) {
      const parsed = JSON.parse(match[0]);
      if (parsed.data && Array.isArray(parsed.data)) return parsed;
      if (parsed.data && typeof parsed.data === 'object') return { data: [parsed.data], layout: parsed.layout || {} };
    }
  } catch { }
  return null;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatQuery, setChatQuery] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [view, setView] = useState<'upload' | 'chat'>('upload');
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, chatLoading]);

  // Auto-dismiss error
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
      } else {
        setError('Only CSV files are supported');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post(`${API_URL}/upload`, formData);
      setView('chat');
      setChatHistory([{
        role: 'assistant',
        content: `✅ **${file.name}** loaded successfully!\n\nTry asking:\n- "How many rows and columns?"\n- "Show distribution of [column]"\n- "What are the missing values?"`,
        type: 'text'
      }]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally { setLoading(false); }
  };

  const handleChat = async () => {
    if (!chatQuery.trim() || chatLoading) return;
    const msg = chatQuery.trim();
    setChatQuery('');
    setChatHistory(prev => [...prev, { role: 'user', content: msg, type: 'text' }]);

    try {
      setChatLoading(true);
      inputRef.current?.blur();
      const res = await axios.post(`${API_URL}/chat`, { query: msg });
      const content = typeof res.data.response === 'string' ? res.data.response : JSON.stringify(res.data.response);
      const type = res.data.type === 'chart' ? 'chart' : 'text';
      const agentName = res.data.chart_type
        ? `Visualizer (${res.data.chart_type})`
        : 'Analyst';
      setChatHistory(prev => [...prev, { role: 'assistant', content, type, agentName }]);
    } catch (err: any) {
      setError(err.message);
      setChatHistory(prev => [...prev, { role: 'assistant', content: `Sorry, something went wrong. Please try again.`, type: 'text', error: true }]);
    } finally {
      setChatLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleQuickAction = (query: string) => {
    setChatQuery(query);
    setTimeout(() => handleChat(), 100);
  };

  const renderMessage = (msg: ChatMessage) => {
    if (msg.type === 'chart') {
      const plotData = parsePlotlyJSON(msg.content);
      if (plotData) {
        // Ensure chart has a title
        const layout = {
          ...plotData.layout,
          title: plotData.layout.title || 'Chart',
          autosize: true,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(20,20,30,0.5)',
          font: { color: '#e2e8f0', size: 12 },
          margin: { l: 50, r: 30, t: 50, b: 50 },
        };
        return (
          <Plot
            data={plotData.data}
            layout={layout}
            config={{ responsive: true, displayModeBar: true, displaylogo: false }}
            style={{ width: '100%', height: '320px' }}
          />
        );
      }
    }
    return (
      <div style={{ fontSize: '0.9rem', lineHeight: 1.6 }}>
        <ReactMarkdown components={markdownComponents}>{msg.content}</ReactMarkdown>
      </div>
    );
  };

  const quickActions = [
    "How many rows?",
    "Show missing values",
    "List all columns",
    "Bar chart of first categorical column",
  ];

  return (
    <div style={styles.container}>
      {/* 3D Animated Background */}
      <AnimatedBackground />

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            style={styles.errorToast}
          >
            <AlertCircle size={18} />
            <span>{error}</span>
            <X size={16} style={{ cursor: 'pointer', marginLeft: '0.5rem' }} onClick={() => setError(null)} />
          </motion.div>
        )}
      </AnimatePresence>

      <header style={styles.header}>
        <h1 style={styles.title}><span style={styles.gradientText}>Data Crew</span> AI</h1>
        <p style={styles.subtitle}>Upload CSV • Ask questions • Get insights</p>
      </header>

      <AnimatePresence mode="wait">
        {view === 'upload' ? (
          <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={styles.uploadContainer}>
            <div style={styles.uploadCard}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Upload Dataset</h2>
              <p style={{ color: '#6b7280', marginBottom: '1.25rem', fontSize: '0.875rem' }}>Drag & drop or click to select</p>

              <div
                style={{ ...styles.dropzone, ...(dragActive ? styles.dropzoneActive : {}) }}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={(e) => {
                    const selectedFile = e.target.files?.[0];
                    if (selectedFile) setFile(selectedFile);
                  }}
                  style={{ display: 'none' }}
                />
                {file ? (
                  <div style={styles.filePreview}>
                    <FileText size={24} color="#a78bfa" />
                    <div style={{ textAlign: 'left' as const }}>
                      <div style={{ color: '#fff', fontWeight: 500 }}>{file.name}</div>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>{(file.size / 1024).toFixed(1)} KB</div>
                    </div>
                  </div>
                ) : (
                  <>
                    <Upload size={32} color="#6b7280" style={{ marginBottom: '0.75rem' }} />
                    <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Drop CSV here or click to browse</p>
                  </>
                )}
              </div>

              <div style={styles.formatBadges}>
                <span style={styles.badge}>CSV</span>
                <span style={styles.badge}>Max 50MB</span>
              </div>

              <button
                onClick={handleUpload}
                disabled={!file || loading}
                style={{ ...styles.primaryButton, opacity: !file || loading ? 0.5 : 1, marginTop: '1.25rem' }}
              >
                {loading ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><Sparkles size={18} /> Start Analysis</>}
              </button>


            </div>
          </motion.div>
        ) : (
          <motion.div key="chat" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={styles.chatContainer}>
            <div style={styles.chatPanel}>
              <div style={styles.chatHeader}>
                <MessageSquare size={18} color="#8b5cf6" />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Chat</span>
                <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  <Database size={12} /> {file?.name}
                </span>
              </div>

              <div style={styles.chatMessages}>
                {chatHistory.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={msg.role === 'user' ? styles.chatBubbleUser : { ...styles.chatBubbleAgent, ...(msg.error ? { borderColor: 'rgba(239,68,68,0.3)' } : {}) }}
                  >
                    <div style={{ fontSize: '0.7rem', color: '#6b7280', marginBottom: '0.375rem', fontWeight: 500 }}>
                      {msg.role === 'user' ? 'You' : (msg.agentName || 'Agent')}
                    </div>
                    {renderMessage(msg)}
                  </motion.div>
                ))}
                {chatLoading && (
                  <div style={styles.chatBubbleAgent}>
                    <div style={styles.typingIndicator}>
                      <Loader2 size={14} className="animate-spin" />
                      <span>Analyzing your data...</span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Quick Actions */}
              <div style={styles.quickActions}>
                {quickActions.map((q, i) => (
                  <button key={i} style={styles.quickAction} onClick={() => handleQuickAction(q)}>{q}</button>
                ))}
              </div>

              <div style={styles.chatInput}>
                <input
                  ref={inputRef}
                  style={{ ...styles.inputField, opacity: chatLoading ? 0.6 : 1 }}
                  value={chatQuery}
                  onChange={(e) => setChatQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !chatLoading && handleChat()}
                  placeholder="Ask about your data..."
                  disabled={chatLoading}
                />
                <button onClick={handleChat} disabled={chatLoading || !chatQuery.trim()} style={{ ...styles.sendButton, opacity: chatLoading || !chatQuery.trim() ? 0.5 : 1 }}>
                  {chatLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
