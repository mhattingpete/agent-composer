import { useSettingsStore } from '../stores/settingsStore'

export default function Header() {
  const { darkMode, toggleDarkMode } = useSettingsStore()

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 dark:border-dark-700 dark:bg-dark-800">
      <div>
        {/* Breadcrumb or page title can go here */}
      </div>

      <div className="flex items-center gap-4">
        {/* Dark mode toggle */}
        <button
          onClick={toggleDarkMode}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-700"
          aria-label="Toggle dark mode"
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </div>
    </header>
  )
}
