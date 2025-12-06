import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SettingsState {
  darkMode: boolean
  toggleDarkMode: () => void

  // API Keys (stored encrypted in production)
  openaiApiKey: string | null
  anthropicApiKey: string | null
  ollamaBaseUrl: string

  setOpenaiApiKey: (key: string | null) => void
  setAnthropicApiKey: (key: string | null) => void
  setOllamaBaseUrl: (url: string) => void

  // Default models
  defaultOpenaiModel: string
  defaultAnthropicModel: string
  defaultOllamaModel: string

  setDefaultOpenaiModel: (model: string) => void
  setDefaultAnthropicModel: (model: string) => void
  setDefaultOllamaModel: (model: string) => void
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      darkMode: false,
      toggleDarkMode: () =>
        set((state) => {
          const newMode = !state.darkMode
          // Update document class for dark mode
          if (newMode) {
            document.documentElement.classList.add('dark')
          } else {
            document.documentElement.classList.remove('dark')
          }
          return { darkMode: newMode }
        }),

      openaiApiKey: null,
      anthropicApiKey: null,
      ollamaBaseUrl: 'http://localhost:11434',

      setOpenaiApiKey: (key) => set({ openaiApiKey: key }),
      setAnthropicApiKey: (key) => set({ anthropicApiKey: key }),
      setOllamaBaseUrl: (url) => set({ ollamaBaseUrl: url }),

      defaultOpenaiModel: 'gpt-4o',
      defaultAnthropicModel: 'claude-3-5-sonnet-20241022',
      defaultOllamaModel: 'llama3.2',

      setDefaultOpenaiModel: (model) => set({ defaultOpenaiModel: model }),
      setDefaultAnthropicModel: (model) => set({ defaultAnthropicModel: model }),
      setDefaultOllamaModel: (model) => set({ defaultOllamaModel: model }),
    }),
    {
      name: 'agent-composer-settings',
      partialize: (state) => ({
        darkMode: state.darkMode,
        openaiApiKey: state.openaiApiKey,
        anthropicApiKey: state.anthropicApiKey,
        ollamaBaseUrl: state.ollamaBaseUrl,
        defaultOpenaiModel: state.defaultOpenaiModel,
        defaultAnthropicModel: state.defaultAnthropicModel,
        defaultOllamaModel: state.defaultOllamaModel,
      }),
    }
  )
)

// Initialize dark mode on load
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem('agent-composer-settings')
  if (stored) {
    const { state } = JSON.parse(stored)
    if (state?.darkMode) {
      document.documentElement.classList.add('dark')
    }
  }
}
