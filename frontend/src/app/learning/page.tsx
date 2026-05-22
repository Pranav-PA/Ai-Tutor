'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import { learningAPI, adaptiveAPI } from '@/lib/api';
import { useCourseStore, useLearningStore } from '@/store';
import { FiChevronLeft, FiChevronRight, FiSend, FiCheck, FiBookOpen } from 'react-icons/fi';

export default function LearningPage() {
  const searchParams = useSearchParams();
  const courseId = searchParams.get('course') || '';
  const { currentTopic, setCurrentTopic } = useCourseStore();
  const { chatMessages, addChatMessage, clearChat } = useLearningStore();

  const [topicContent, setTopicContent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'content' | 'keypoints' | 'examples'>('content');

  const fetchTopicContent = useCallback(async (topicId: string) => {
    setLoading(true);
    try {
      const res = await learningAPI.getTopicContent(topicId);
      setTopicContent(res.data);
    } catch (error) {
      toast.error('Failed to load topic content');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Load first topic or current topic
    const loadInitialTopic = async () => {
      if (currentTopic?.id) {
        await fetchTopicContent(currentTopic.id);
      } else if (courseId) {
        try {
          const res = await learningAPI.getNextTopic(courseId);
          if (res.data.next_topic_id) {
            await fetchTopicContent(res.data.next_topic_id);
          }
        } catch (error) {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };
    loadInitialTopic();
  }, [courseId, currentTopic, fetchTopicContent]);

  const handleNextTopic = async () => {
    if (!courseId || !topicContent?.id) return;
    try {
      const res = await learningAPI.getNextTopic(courseId, topicContent.id);
      if (res.data.next_topic_id) {
        clearChat();
        await fetchTopicContent(res.data.next_topic_id);
      } else {
        toast.success('All topics completed! 🎉');
      }
    } catch (error) {
      toast.error('Failed to get next topic');
    }
  };

  const handleMarkComplete = async () => {
    if (!topicContent?.id) return;
    try {
      await learningAPI.markComplete(topicContent.id);
      toast.success('Topic marked as complete!');
    } catch (error) {
      toast.error('Failed to mark complete');
    }
  };

  const handleAskDoubt = async () => {
    if (!chatInput.trim()) return;
    const question = chatInput;
    setChatInput('');
    addChatMessage({ role: 'user', content: question });
    setChatLoading(true);

    try {
      const res = await adaptiveAPI.askDoubt({
        message: question,
        topic_id: topicContent?.id,
      });
      addChatMessage({ role: 'assistant', content: res.data.answer });
    } catch (error) {
      addChatMessage({ role: 'assistant', content: 'Sorry, I couldn\'t process your question. Please try again.' });
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!topicContent) {
    return (
      <div className="text-center py-20">
        <span className="text-6xl block mb-4">📚</span>
        <h2 className="text-2xl font-bold text-dark-100 mb-2">No topic loaded</h2>
        <p className="text-dark-400">Select a course from the dashboard to start learning.</p>
      </div>
    );
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)]">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topic Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center gap-3 mb-2">
            <span className="px-2 py-1 bg-primary-600/20 text-primary-400 text-xs rounded-full capitalize">
              {topicContent.difficulty}
            </span>
            <span className="text-dark-500 text-sm">
              ~{topicContent.estimated_minutes} min
            </span>
          </div>
          <h1 className="text-2xl font-bold text-dark-50">{topicContent.title}</h1>
          {topicContent.description && (
            <p className="text-dark-400 mt-1">{topicContent.description}</p>
          )}
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          {[
            { key: 'content', label: 'Content', icon: FiBookOpen },
            { key: 'keypoints', label: 'Key Points' },
            { key: 'examples', label: 'Examples' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.key
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-800 text-dark-400 hover:text-dark-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto card">
          {activeTab === 'content' && (
            <div className="prose-content">
              <ReactMarkdown>{topicContent.content || 'Content is being generated...'}</ReactMarkdown>
            </div>
          )}

          {activeTab === 'keypoints' && (
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-dark-100 mb-4">Key Points</h3>
              {(topicContent.key_points || []).map((point: string, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex gap-3 p-3 bg-dark-900 rounded-lg"
                >
                  <span className="text-primary-400 font-bold">{i + 1}.</span>
                  <p className="text-dark-300">{point}</p>
                </motion.div>
              ))}
              {topicContent.memory_tricks?.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-md font-semibold text-dark-200 mb-3">💡 Memory Tricks</h4>
                  {topicContent.memory_tricks.map((trick: string, i: number) => (
                    <div key={i} className="p-3 bg-primary-600/10 border border-primary-600/20 rounded-lg mb-2">
                      <p className="text-primary-300 text-sm">{trick}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'examples' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-dark-100 mb-4">Examples</h3>
              {(topicContent.examples || []).map((example: any, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 bg-dark-900 rounded-lg border border-dark-700"
                >
                  <h4 className="font-medium text-dark-200 mb-2">{example.title || `Example ${i + 1}`}</h4>
                  <p className="text-dark-400 text-sm">{example.content}</p>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center mt-4 pt-4 border-t border-dark-700">
          <button className="btn-secondary flex items-center gap-2">
            <FiChevronLeft className="w-4 h-4" /> Previous
          </button>
          <button
            onClick={handleMarkComplete}
            className="btn-secondary flex items-center gap-2 text-green-400 border-green-600/30 hover:bg-green-600/10"
          >
            <FiCheck className="w-4 h-4" /> Mark Complete
          </button>
          <button onClick={handleNextTopic} className="btn-primary flex items-center gap-2">
            Next <FiChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat Panel */}
      <div className="w-96 flex flex-col card">
        <h3 className="text-lg font-semibold text-dark-100 mb-4">💬 Ask Doubts</h3>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-4">
          {chatMessages.length === 0 ? (
            <div className="text-center py-8 text-dark-500 text-sm">
              Ask any question about this topic...
            </div>
          ) : (
            chatMessages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary-600/20 text-primary-200 ml-8'
                    : 'bg-dark-900 text-dark-300 mr-8'
                }`}
              >
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </motion.div>
            ))
          )}
          {chatLoading && (
            <div className="flex gap-1 p-3">
              <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce [animation-delay:150ms]" />
              <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            className="input-field flex-1 text-sm"
            placeholder="Type your question..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAskDoubt()}
          />
          <button
            onClick={handleAskDoubt}
            disabled={chatLoading || !chatInput.trim()}
            className="btn-primary p-2 disabled:opacity-50"
          >
            <FiSend className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
