'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Server, Key, ArrowRight, Check, Wifi, WifiOff, RefreshCw, Sparkles } from 'lucide-react';

interface SetupWizardProps {
  onComplete: () => void;
}

/**
 * First-run setup wizard that helps users configure their AI provider.
 * Shows on first launch or when no provider is configured.
 */
export function SetupWizard({ onComplete }: SetupWizardProps) {
  const [step, setStep] = useState(0);
  const [provider, setProvider] = useState<'ollama' | 'openai' | 'gemini'>('ollama');
  const [apiKey, setApiKey] = useState('');
  const [ollamaStatus, setOllamaStatus] = useState<{ available: boolean; models: string[] }>({ available: false, models: [] });
  const [checking, setChecking] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    checkOllama();
  }, []);

  const checkOllama = async () => {
    setChecking(true);
    try {
      if (window.electronAPI) {
        const status = await window.electronAPI.checkOllamaStatus();
        setOllamaStatus(status);
      } else {
        // Browser mode fallback
        try {
          const res = await fetch('/api/settings/providers');
          const data = await res.json();
          const ollamaP = data.providers?.find((p: any) => p.id === 'ollama');
          setOllamaStatus({ available: ollamaP?.available || false, models: ollamaP?.models || [] });
        } catch {
          setOllamaStatus({ available: false, models: [] });
        }
      }
    } catch {
      setOllamaStatus({ available: false, models: [] });
    }
    setChecking(false);
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      const settings: any = { preferred_provider: provider };
      
      if (provider === 'openai' && apiKey) {
        settings.openai_api_key = apiKey;
      } else if (provider === 'gemini' && apiKey) {
        settings.gemini_api_key = apiKey;
      }

      // Save to backend
      await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      // Save to Electron store if available
      if (window.electronAPI) {
        await window.electronAPI.saveSettings({
          aiProvider: provider,
          openaiApiKey: provider === 'openai' ? apiKey : undefined,
          geminiApiKey: provider === 'gemini' ? apiKey : undefined,
        });
      }

      // Mark onboarding as complete
      localStorage.setItem('onboarding-complete', 'true');
      onComplete();
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
    setSaving(false);
  };

  const steps = [
    // Step 0: Welcome
    <motion.div key="welcome" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="text-center space-y-6">
      <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-4xl shadow-lg">
        🧠
      </div>
      <div>
        <h1 className="text-2xl font-bold">Welcome to AI Semester Companion</h1>
        <p className="text-muted-foreground mt-2">
          Your personal AI-powered study partner. Let&apos;s get you set up in under a minute.
        </p>
      </div>
      <button
        onClick={() => setStep(1)}
        className="px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity inline-flex items-center gap-2"
      >
        Get Started <ArrowRight className="w-4 h-4" />
      </button>
    </motion.div>,

    // Step 1: Choose provider
    <motion.div key="provider" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-bold">Choose Your AI Engine</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          You can change this anytime in Settings.
        </p>
      </div>

      <div className="space-y-3">
        {/* Ollama - Free & Local */}
        <button
          onClick={() => { setProvider('ollama'); }}
          className={`w-full p-4 rounded-xl border text-left transition-all flex items-start gap-4
            ${provider === 'ollama' ? 'border-primary bg-primary/5 ring-1 ring-primary/20' : 'border-border hover:border-primary/40'}`}
        >
          <div className="p-2.5 rounded-xl bg-green-500/10 shrink-0">
            <Server className={`w-5 h-5 ${provider === 'ollama' ? 'text-green-500' : 'text-muted-foreground'}`} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-semibold">Ollama (Local)</p>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-500/10 text-green-500 font-medium">FREE</span>
              {ollamaStatus.available && <span className="w-2 h-2 rounded-full bg-green-500"></span>}
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Run AI models locally on your machine. No API key needed. Requires Ollama installed.
            </p>
          </div>
          {provider === 'ollama' && <Check className="w-5 h-5 text-primary shrink-0 mt-1" />}
        </button>

        {/* OpenAI */}
        <button
          onClick={() => { setProvider('openai'); }}
          className={`w-full p-4 rounded-xl border text-left transition-all flex items-start gap-4
            ${provider === 'openai' ? 'border-primary bg-primary/5 ring-1 ring-primary/20' : 'border-border hover:border-primary/40'}`}
        >
          <div className="p-2.5 rounded-xl bg-blue-500/10 shrink-0">
            <Brain className={`w-5 h-5 ${provider === 'openai' ? 'text-blue-500' : 'text-muted-foreground'}`} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-semibold">OpenAI GPT-4o</p>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-blue-500/10 text-blue-500 font-medium">API KEY</span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Best quality responses via cloud. Requires an OpenAI API key (pay-per-use).
            </p>
          </div>
          {provider === 'openai' && <Check className="w-5 h-5 text-primary shrink-0 mt-1" />}
        </button>

        {/* Gemini */}
        <button
          onClick={() => { setProvider('gemini'); }}
          className={`w-full p-4 rounded-xl border text-left transition-all flex items-start gap-4
            ${provider === 'gemini' ? 'border-primary bg-primary/5 ring-1 ring-primary/20' : 'border-border hover:border-primary/40'}`}
        >
          <div className="p-2.5 rounded-xl bg-amber-500/10 shrink-0">
            <Sparkles className={`w-5 h-5 ${provider === 'gemini' ? 'text-amber-500' : 'text-muted-foreground'}`} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-semibold">Google Gemini</p>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/10 text-amber-500 font-medium">API KEY</span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Google&apos;s powerful AI model. Free tier available with generous limits.
            </p>
          </div>
          {provider === 'gemini' && <Check className="w-5 h-5 text-primary shrink-0 mt-1" />}
        </button>
      </div>

      <button
        onClick={() => setStep(2)}
        className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
      >
        Continue <ArrowRight className="w-4 h-4" />
      </button>
    </motion.div>,

    // Step 2: Configure chosen provider
    <motion.div key="configure" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-bold">
          {provider === 'ollama' ? 'Ollama Setup' : `Enter ${provider === 'openai' ? 'OpenAI' : 'Gemini'} API Key`}
        </h2>
      </div>

      {provider === 'ollama' ? (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-secondary/50 border border-border space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {ollamaStatus.available ? (
                  <Wifi className="w-4 h-4 text-green-500" />
                ) : (
                  <WifiOff className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ${ollamaStatus.available ? 'text-green-500' : 'text-red-500'}`}>
                  {checking ? 'Checking...' : ollamaStatus.available ? `Connected (${ollamaStatus.models.length} models)` : 'Not detected'}
                </span>
              </div>
              <button onClick={checkOllama} disabled={checking} className="p-1.5 rounded-lg hover:bg-secondary">
                <RefreshCw className={`w-4 h-4 ${checking ? 'animate-spin' : ''}`} />
              </button>
            </div>
            
            {!ollamaStatus.available && (
              <div className="text-xs text-muted-foreground space-y-2">
                <p>To use local AI models for free:</p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Download Ollama from <a href="https://ollama.ai" className="text-primary underline" target="_blank" rel="noopener noreferrer">ollama.ai</a></li>
                  <li>Install and start Ollama</li>
                  <li>Run: <code className="bg-secondary px-1.5 py-0.5 rounded text-foreground">ollama pull llama3.1</code></li>
                  <li>Click refresh above to check connection</li>
                </ol>
              </div>
            )}

            {ollamaStatus.available && ollamaStatus.models.length > 0 && (
              <div className="text-xs text-muted-foreground">
                <p className="font-medium text-foreground mb-1">Available models:</p>
                <div className="flex flex-wrap gap-1.5">
                  {ollamaStatus.models.slice(0, 8).map((model: string) => (
                    <span key={model} className="px-2 py-0.5 rounded-full bg-secondary text-foreground">{model}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground text-center">
            You can skip this step and set up Ollama later in Settings.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1.5 block">
              {provider === 'openai' ? 'OpenAI API Key' : 'Google Gemini API Key'}
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={provider === 'openai' ? 'sk-...' : 'AIza...'}
              className="w-full px-4 py-3 rounded-xl bg-secondary border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              autoFocus
            />
          </div>
          <p className="text-xs text-muted-foreground">
            {provider === 'openai'
              ? 'Get your API key from platform.openai.com/api-keys'
              : 'Get your API key from aistudio.google.com/apikey'}
          </p>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={() => setStep(1)}
          className="flex-1 py-3 rounded-xl border border-border font-medium hover:bg-secondary transition-colors"
        >
          Back
        </button>
        <button
          onClick={handleFinish}
          disabled={saving || (provider !== 'ollama' && !apiKey)}
          className="flex-1 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {saving ? 'Setting up...' : 'Finish Setup'} {!saving && <Check className="w-4 h-4" />}
        </button>
      </div>
    </motion.div>,
  ];

  return (
    <div className="fixed inset-0 z-[200] bg-background flex items-center justify-center">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,hsl(262,83%,58%,0.1),transparent)]" />
      <div className="relative w-full max-w-md mx-4 p-6">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-8">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i <= step ? 'bg-primary w-8' : 'bg-border w-4'
              }`}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {steps[step]}
        </AnimatePresence>
      </div>
    </div>
  );
}
