'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import {
  ArrowLeft, Settings as SettingsIcon, Sun, Moon, Monitor,
  Key, User, Brain, Save, Check, Server, Wifi, WifiOff, RefreshCw
} from 'lucide-react';
import toast from 'react-hot-toast';
import { settingsAPI } from '@/services/api';

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [provider, setProvider] = useState('openai');
  const [name, setName] = useState('');
  const [learningStyle, setLearningStyle] = useState('balanced');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('llama3.1');
  const [ollamaStatus, setOllamaStatus] = useState<{ available: boolean; models: string[] }>({ available: false, models: [] });
  const [checkingOllama, setCheckingOllama] = useState(false);

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsAPI.get,
  });

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: settingsAPI.getProfile,
  });

  useEffect(() => {
    if (settings) {
      setProvider(settings.preferred_provider);
      if (settings.ollama_model) setOllamaModel(settings.ollama_model);
    }
    if (profile) {
      setName(profile.name);
      setLearningStyle(profile.learning_style);
    }
  }, [settings, profile]);

  // Check Ollama status on mount and when URL changes
  useEffect(() => {
    checkOllamaConnection();
  }, []);

  const checkOllamaConnection = async () => {
    setCheckingOllama(true);
    try {
      // Check via Electron API if available, otherwise via backend
      if (typeof window !== 'undefined' && (window as any).electronAPI) {
        const status = await (window as any).electronAPI.checkOllamaStatus();
        setOllamaStatus(status);
      } else {
        // Fallback: check via backend API
        try {
          const response = await fetch('/api/settings/providers');
          const data = await response.json();
          const ollamaProvider = data.providers?.find((p: any) => p.id === 'ollama');
          if (ollamaProvider) {
            setOllamaStatus({ available: ollamaProvider.available, models: ollamaProvider.models || [] });
          }
        } catch {
          setOllamaStatus({ available: false, models: [] });
        }
      }
    } catch {
      setOllamaStatus({ available: false, models: [] });
    }
    setCheckingOllama(false);
  };

  const saveSettings = async () => {
    try {
      const updates: any = { preferred_provider: provider };
      if (openaiKey) updates.openai_api_key = openaiKey;
      if (geminiKey) updates.gemini_api_key = geminiKey;
      if (provider === 'ollama') {
        updates.ollama_base_url = ollamaUrl;
        updates.ollama_model = ollamaModel;
      }
      await settingsAPI.update(updates);

      // Also save to Electron store if available
      if (typeof window !== 'undefined' && (window as any).electronAPI) {
        await (window as any).electronAPI.saveSettings({
          aiProvider: provider,
          ollamaUrl,
          ollamaModel,
          openaiApiKey: openaiKey || undefined,
          geminiApiKey: geminiKey || undefined,
        });
      }

      if (name || learningStyle) {
        await settingsAPI.updateProfile({ name, learning_style: learningStyle });
      }

      toast.success('Settings saved!');
    } catch (err) {
      toast.error('Failed to save settings');
    }
  };

  const themes = [
    { id: 'light', label: 'Light', icon: Sun },
    { id: 'dark', label: 'Dark', icon: Moon },
    { id: 'amoled', label: 'AMOLED', icon: Monitor },
  ];

  const learningStyles = [
    { id: 'visual', label: 'Visual', desc: 'Diagrams, charts, mental models' },
    { id: 'reading', label: 'Reading', desc: 'Detailed text, definitions' },
    { id: 'kinesthetic', label: 'Hands-on', desc: 'Examples, code, exercises' },
    { id: 'balanced', label: 'Balanced', desc: 'Mix of all approaches' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 glass border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center gap-3">
          <Link href="/dashboard" className="p-2 rounded-xl hover:bg-secondary">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="font-bold">Settings</h1>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-2xl space-y-8">
        {/* Profile */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-card border border-border"
        >
          <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-primary" /> Profile
          </h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Learning Style</label>
              <div className="grid grid-cols-2 gap-3">
                {learningStyles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() => setLearningStyle(style.id)}
                    className={`p-3 rounded-xl border text-left transition-all
                      ${learningStyle === style.id ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'}`}
                  >
                    <p className="font-medium text-sm">{style.label}</p>
                    <p className="text-xs text-muted-foreground">{style.desc}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* AI Provider */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="p-6 rounded-2xl bg-card border border-border"
        >
          <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Key className="w-5 h-5 text-primary" /> AI Configuration
          </h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Provider</label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => setProvider('ollama')}
                  className={`p-3 rounded-xl border text-center transition-all relative
                    ${provider === 'ollama' ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'}`}
                >
                  <Server className={`w-5 h-5 mx-auto mb-1 ${provider === 'ollama' ? 'text-primary' : 'text-muted-foreground'}`} />
                  <p className="font-medium text-sm">Ollama</p>
                  <p className="text-xs text-muted-foreground">Local / Free</p>
                  {ollamaStatus.available && (
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-green-500"></span>
                  )}
                </button>
                <button
                  onClick={() => setProvider('openai')}
                  className={`p-3 rounded-xl border text-center transition-all
                    ${provider === 'openai' ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'}`}
                >
                  <Brain className={`w-5 h-5 mx-auto mb-1 ${provider === 'openai' ? 'text-primary' : 'text-muted-foreground'}`} />
                  <p className="font-medium text-sm">OpenAI</p>
                  <p className="text-xs text-muted-foreground">GPT-4o</p>
                </button>
                <button
                  onClick={() => setProvider('gemini')}
                  className={`p-3 rounded-xl border text-center transition-all
                    ${provider === 'gemini' ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'}`}
                >
                  <Brain className={`w-5 h-5 mx-auto mb-1 ${provider === 'gemini' ? 'text-primary' : 'text-muted-foreground'}`} />
                  <p className="font-medium text-sm">Gemini</p>
                  <p className="text-xs text-muted-foreground">Gemini 1.5 Pro</p>
                </button>
              </div>
            </div>

            {/* Ollama Configuration */}
            {provider === 'ollama' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-3 p-4 rounded-xl bg-secondary/50 border border-border"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {ollamaStatus.available ? (
                      <Wifi className="w-4 h-4 text-green-500" />
                    ) : (
                      <WifiOff className="w-4 h-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${ollamaStatus.available ? 'text-green-500' : 'text-red-500'}`}>
                      {ollamaStatus.available ? 'Connected' : 'Not Connected'}
                    </span>
                  </div>
                  <button
                    onClick={checkOllamaConnection}
                    disabled={checkingOllama}
                    className="p-1.5 rounded-lg hover:bg-secondary transition-colors"
                  >
                    <RefreshCw className={`w-4 h-4 ${checkingOllama ? 'animate-spin' : ''}`} />
                  </button>
                </div>

                {!ollamaStatus.available && (
                  <div className="text-xs text-muted-foreground bg-background p-3 rounded-lg">
                    <p className="font-medium text-foreground mb-1">Ollama not detected</p>
                    <p>Install Ollama from <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" className="text-primary underline">ollama.ai</a> and run it to use local AI models for free.</p>
                    <p className="mt-1">Then run: <code className="bg-secondary px-1 py-0.5 rounded">ollama pull llama3.1</code></p>
                  </div>
                )}

                <div>
                  <label className="text-sm font-medium mb-1 block">Ollama URL</label>
                  <input
                    type="text"
                    value={ollamaUrl}
                    onChange={(e) => setOllamaUrl(e.target.value)}
                    placeholder="http://localhost:11434"
                    className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-1 block">Model</label>
                  {ollamaStatus.models.length > 0 ? (
                    <select
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    >
                      {ollamaStatus.models.map((model: string) => (
                        <option key={model} value={model}>{model}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                      placeholder="llama3.1"
                      className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  )}
                </div>
              </motion.div>
            )}

            {/* API Key Inputs - shown when using cloud providers */}
            {provider === 'openai' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <label className="text-sm font-medium mb-1 block">OpenAI API Key</label>
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder={settings?.has_openai_key ? '••••••••••••••••' : 'sk-...'}
                  className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                {settings?.has_openai_key && (
                  <p className="text-xs text-green-500 mt-1 flex items-center gap-1">
                    <Check className="w-3 h-3" /> Key configured
                  </p>
                )}
              </motion.div>
            )}

            {provider === 'gemini' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <label className="text-sm font-medium mb-1 block">Gemini API Key</label>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder={settings?.has_gemini_key ? '••••••••••••••••' : 'AIza...'}
                  className="w-full px-4 py-2.5 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                {settings?.has_gemini_key && (
                  <p className="text-xs text-green-500 mt-1 flex items-center gap-1">
                    <Check className="w-3 h-3" /> Key configured
                  </p>
                )}
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Theme */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-6 rounded-2xl bg-card border border-border"
        >
          <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Sun className="w-5 h-5 text-primary" /> Theme
          </h2>
          <div className="flex gap-3">
            {themes.map((t) => (
              <button
                key={t.id}
                onClick={() => setTheme(t.id)}
                className={`flex-1 p-3 rounded-xl border text-center transition-all
                  ${theme === t.id ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'}`}
              >
                <t.icon className={`w-5 h-5 mx-auto mb-1 ${theme === t.id ? 'text-primary' : 'text-muted-foreground'}`} />
                <p className="text-sm font-medium">{t.label}</p>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Save */}
        <button
          onClick={saveSettings}
          className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" /> Save Settings
        </button>
      </main>
    </div>
  );
}
