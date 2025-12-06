import { useState } from 'react'
import { useSettingsStore } from '../stores/settingsStore'

export default function SettingsPage() {
  const {
    openaiApiKey,
    anthropicApiKey,
    ollamaBaseUrl,
    defaultOpenaiModel,
    defaultAnthropicModel,
    defaultOllamaModel,
    setOpenaiApiKey,
    setAnthropicApiKey,
    setOllamaBaseUrl,
    setDefaultOpenaiModel,
    setDefaultAnthropicModel,
    setDefaultOllamaModel,
  } = useSettingsStore()

  const [showOpenai, setShowOpenai] = useState(false)
  const [showAnthropic, setShowAnthropic] = useState(false)

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
        <div className="flex gap-4">
          <button className="btn-secondary" disabled>
            Test OpenAI
          </button>
          <button className="btn-secondary" disabled>
            Test Anthropic
          </button>
          <button className="btn-secondary" disabled>
            Test Ollama
          </button>
        </div>
      </div>
    </div>
  )
}
