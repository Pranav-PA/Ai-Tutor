'use client';

import { useState, useRef, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import {
  Send, ArrowLeft, Sparkles, BookOpen, Brain,
  MessageCircle, Eraser, Loader2
} from 'lucide-react';
import Link from 'next/link';
import { chatAPI, courseAPI } from '@/services/api';
import { ChatMessage } from '@/types';

const modes = [
  { id: 'explain', label: 'Explain', icon: BookOpen },
  { id: 'summarize', label: 'Summarize', icon: Sparkles },
  { id: 'quiz', label: 'Quiz Me', icon: Brain },
  { id: 'revise', label: 'Revise', icon: MessageCircle },
];

export default function ChatPage() {
  const params = useParams();
  const courseId = Number(params.id);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState('explain');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const { data: course } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => courseAPI.getById(courseId),
  });

  const { data: history } = useQuery({
    queryKey: ['chatHistory', courseId],
    queryFn: () => chatAPI.getHistory(courseId),
  });

  useEffect(() => {
    if (history) setMessages(history);
  }, [history]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      mode,
      metadata: {},
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    setStreamingContent('');

    try {
      let fullContent = '';
      for await (const chunk of chatAPI.stream({ content: userMessage.content, mode, course_id: courseId })) {
        fullContent += chunk;
        setStreamingContent(fullContent);
      }

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: fullContent,
        mode,
        metadata: {},
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingContent('');
    } catch (err) {
      setStreamingContent('');
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please check your API key in settings.',
          mode,
          metadata: {},
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const clearChat = async () => {
    await chatAPI.clearHistory(courseId);
    setMessages([]);
    queryClient.invalidateQueries({ queryKey: ['chatHistory', courseId] });
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex-shrink-0 glass border-b border-border">
        <div className="container mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href={`/course/${courseId}`} className="p-2 rounded-xl hover:bg-secondary transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="font-bold">AI Chat</h1>
              <p className="text-xs text-muted-foreground">{course?.title}</p>
            </div>
          </div>
          <button onClick={clearChat} className="p-2 rounded-xl hover:bg-secondary transition-colors text-muted-foreground">
            <Eraser className="w-5 h-5" />
          </button>
        </div>
        {/* Mode Selector */}
        <div className="container mx-auto px-6 pb-3">
          <div className="flex gap-2">
            {modes.map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                  ${mode === m.id ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground hover:text-foreground'}`}
              >
                <m.icon className="w-3 h-3" />
                {m.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && !streamingContent && (
            <div className="text-center py-20">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Start a Conversation</h3>
              <p className="text-muted-foreground text-sm max-w-md mx-auto">
                Ask me anything about your course. I&apos;ll use your uploaded notes to give accurate, personalized answers.
              </p>
              <div className="grid grid-cols-2 gap-2 mt-6 max-w-md mx-auto">
                {['Explain the key concepts', 'Summarize the latest topic', 'Quiz me on Unit 1', 'Help me revise for exam'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => { setInput(suggestion); }}
                    className="p-3 rounded-xl bg-card border border-border text-sm text-left hover:border-primary/30 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-br-md'
                      : 'bg-card border border-border rounded-bl-md'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm">{msg.content}</p>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Streaming response */}
          {streamingContent && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="max-w-[80%] p-4 rounded-2xl bg-card border border-border rounded-bl-md">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {streamingContent}
                  </ReactMarkdown>
                </div>
              </div>
            </motion.div>
          )}

          {isStreaming && !streamingContent && (
            <div className="flex justify-start">
              <div className="p-4 rounded-2xl bg-card border border-border rounded-bl-md">
                <Loader2 className="w-5 h-5 animate-spin text-primary" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-border bg-background/80 backdrop-blur-xl p-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder={`Ask about your ${course?.title || 'course'}...`}
            className="flex-1 px-5 py-3 rounded-2xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            disabled={isStreaming}
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            className="px-5 py-3 rounded-2xl bg-primary text-primary-foreground font-medium transition-all hover:opacity-90 disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
