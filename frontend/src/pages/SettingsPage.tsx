import { useState } from 'react'
import { useSettingsStore } from '../stores/settingsStore'

export default function SettingsPage() {
  const {
    openaiApiKey,
    anthropicApiKey,
    openrouterApiKey,
    ollamaBaseUrl,
    defaultOpenaiModel,
    defaultAnthropicModel,
    defaultOpenrouterModel,
    defaultOllamaModel,
    setOpenaiApiKey,
    setAnthropicApiKey,
    setOpenrouterApiKey,
    setOllamaBaseUrl,
    setDefaultOpenaiModel,
    setDefaultAnthropicModel,
    setDefaultOpenrouterModel,
    setDefaultOllamaModel,
  } = useSettingsStore()

  const [showOpenai, setShowOpenai] = useState(false)
  const [showAnthropic, setShowAnthropic] = useState(false)
  const [showOpenrouter, setShowOpenrouter] = useState(false)

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      {/* API Keys Section */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">API Keys</h2>
        <div className="space-y-4">
          {/* OpenAI */}
          <div>
            <label className="block text-sm font-medium mb-2">OpenAI API Key</label>
            <div className="flex gap-2">
              <input
                type={showOpenai ? 'text' : 'password'}
                value={openaiApiKey || ''}
                onChange={(e) => setOpenaiApiKey(e.target.value || null)}
                placeholder="sk-..."
                className="input flex-1"
              />
              <button
                onClick={() => setShowOpenai(!showOpenai)}
                className="btn-secondary"
              >
                {showOpenai ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {/* Anthropic */}
          <div>
            <label className="block text-sm font-medium mb-2">Anthropic API Key</label>
            <div className="flex gap-2">
              <input
                type={showAnthropic ? 'text' : 'password'}
                value={anthropicApiKey || ''}
                onChange={(e) => setAnthropicApiKey(e.target.value || null)}
                placeholder="sk-ant-..."
                className="input flex-1"
              />
              <button
                onClick={() => setShowAnthropic(!showAnthropic)}
                className="btn-secondary"
              >
                {showAnthropic ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {/* OpenRouter */}
          <div>
            <label className="block text-sm font-medium mb-2">OpenRouter API Key</label>
            <div className="flex gap-2">
              <input
                type={showOpenrouter ? 'text' : 'password'}
                value={openrouterApiKey || ''}
                onChange={(e) => setOpenrouterApiKey(e.target.value || null)}
                placeholder="sk-or-v1-..."
                className="input flex-1"
              />
              <button
                onClick={() => setShowOpenrouter(!showOpenrouter)}
                className="btn-secondary"
              >
                {showOpenrouter ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {/* Ollama */}
          <div>
            <label className="block text-sm font-medium mb-2">Ollama Base URL</label>
            <input
              type="text"
              value={ollamaBaseUrl}
              onChange={(e) => setOllamaBaseUrl(e.target.value)}
              placeholder="http://localhost:11434"
              className="input"
            />
          </div>
        </div>
      </div>

      {/* Default Models Section */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Default Models</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">OpenAI Model</label>
            <input
              type="text"
              value={defaultOpenaiModel}
              onChange={(e) => setDefaultOpenaiModel(e.target.value)}
              placeholder="gpt-4o"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Anthropic Model</label>
            <input
              type="text"
              value={defaultAnthropicModel}
              onChange={(e) => setDefaultAnthropicModel(e.target.value)}
              placeholder="claude-3-5-sonnet-20241022"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">OpenRouter Model</label>
            <input
              type="text"
              value={defaultOpenrouterModel}
              onChange={(e) => setDefaultOpenrouterModel(e.target.value)}
              placeholder="anthropic/claude-3.5-sonnet"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Ollama Model</label>
            <input
              type="text"
              value={defaultOllamaModel}
              onChange={(e) => setDefaultOllamaModel(e.target.value)}
              placeholder="llama3.2"
              className="input"
            />
          </div>
        </div>
      </div>

      {/* Connection Test */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Test Connection</h2>
        <div className="flex flex-wrap gap-4">
          <button className="btn-secondary" disabled>
            Test OpenAI
          </button>
          <button className="btn-secondary" disabled>
            Test Anthropic
          </button>
          <button className="btn-secondary" disabled>
            Test OpenRouter
          </button>
          <button className="btn-secondary" disabled>
            Test Ollama
          </button>
        </div>
      </div>
    </div>
  )
}
